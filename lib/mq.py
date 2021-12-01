#!/usr/bin/env python

"""Small wrapper around a MQ system"""
import argparse
import json
import logging
import sys
import time
from pathlib import Path

import pika
import pika.exceptions

from lib.config import Config, GLOBAL_CONFIG_PATH
from lib.utils import sanitize_password_str
from lib.utils.projectutils import ProjectUtils


class MQ:
    """ The message queue class """
    connection = None
    channel = None
    queue = None
    queue_name = ""
    exchange = None
    id: str = ""

    logger: logging.Logger = None  # the logger to be used

    def __init__(self, id: str, logger=None):
        self.id = id
        if not logger:
            self.logger = ProjectUtils.get_logger()
        else:
            self.logger = logger
        _c = Config()
        self.config = _c.load(Path(GLOBAL_CONFIG_PATH))
        self.logger.info("Loaded global config")

    def __del__(self):
        self.logger.info("Disconnecting from MQ")
        self._queue_unbind()
        self.channel.close()
        self.connection.close()

    def setup_channel(self, exchange: str):
        """Do the RabbitMQ channel setup."""

        try:
            # set up the channel
            self.logger.info("Setting up the exchange and channels...")
            self.channel = self.connection.channel()
            self.channel.confirm_delivery()  # required to be informed if a basic_publish() fails!
            self.logger.debug("channel = %r" % self.channel)
            self._create_exchange(exchange)
            self.logger.debug("exchange = %r" % self.exchange)
        except Exception as ex:
            self.logger.error("can't set up channel and exchange. Reason: %s. Bailing out." % (str(ex)))
            sys.exit(-2)
        self.logger.info("Done")

    def connect(self, exchange: str = ""):
        """Connect to the MQ system."""

        try:
            self.logger.info("Connecting to RabbitMQ...")
            host = self.config['rabbitmq']['host']
            port = int(self.config['rabbitmq'].get('port', 5672))
            # user and password config
            user = self.config['rabbitmq'].get('user', "guest")
            password = self.config['rabbitmq'].get('password', "guest")
            credentials = pika.PlainCredentials(user, password)
            self.logger.info("Attempting to connect with (%s:%d as %s/%s)" % (host, port, user,
                                                                              sanitize_password_str(password)))
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host = host, port = port,
                                                                                credentials = credentials))
        except Exception as ex:
            self.logger.error("can't connect to the MQ system. Bailing out. Reason: %s" % (str(ex)))
            sys.exit(-1)
        self.logger.info("Done. Connected!")
        self.setup_channel(exchange)

    def _create_exchange(self, exchange: str = ""):
        self.exchange = exchange
        self.logger.info("Creating exchange %s" % exchange)
        try:
            self.channel.exchange_declare(exchange = self.exchange, exchange_type = 'fanout', durable = True,
                                          auto_delete = False)
        except Exception as ex:
            self.logger.error("can't Create exchange '%s'. Reason: %s" % (exchange, str(ex)))
            raise ex

    def _publish(self, msg: dict, routing_key=""):
        data = bytes(json.dumps(msg), 'utf-8')  # JSON is always utf-8
        try:
            self.channel.basic_publish(exchange = self.exchange, routing_key = routing_key, body = data,
                                       properties = pika.BasicProperties(delivery_mode = 2, ),
                                       # make the message persistent
                                       mandatory = True
                                       )
        except pika.exceptions.UnroutableError as ex:
            self.logger.error("Could not publish message. Reason: {}".format(str(ex)))

    def _consume(self, queue: str, callback=None, auto_ack=False):
        self.channel.basic_consume(queue = queue, on_message_callback = callback, auto_ack = auto_ack)

    def _connect_queue(self, queue_name: str = ''):
        self.queue = self.channel.queue_declare(queue = queue_name, durable = True, exclusive = False,
                                                auto_delete = False)
        self.channel.basic_qos(prefetch_count = 1)
        self.queue_name = self.queue.method.queue

    def _queue_bind(self):
        self.channel.queue_bind(exchange = self.exchange, queue = self.queue_name)

    def _queue_unbind(self):
        self.channel.queue_unbind(queue = self.queue_name, exchange = self.exchange)

    def close(self):
        """Close the connection to rabbitmq."""
        if self.connection:
            self.channel.close()
            self.connection.close()
            self.logger.info("Closed connection")


class Producer(MQ):
    """A producer, based on the base functionality of MQ."""

    def __init__(self, id: str, exchange: str, logger):
        super().__init__(id, logger)
        self.connect(exchange)

    def connect(self, exchange: str = ""):
        """Connect to an exchange."""
        self.logger.info("Connecting to exchange %s" % (exchange,))
        super().connect(exchange)
        # super()._connect_queue()       # producers don't need to connect to queues, they send to the exchange.

    def produce(self, msg: dict, routing_key: str = ""):
        """Send a msg to the exchange with the given routing_key."""
        if msg:
            super()._publish(msg = msg, routing_key = routing_key)
            self.logger.info("[x] Sent %r" % msg)


class Consumer(MQ):
    """A consumer, based on the base functionality of MQ."""

    cb_function = None

    def __init__(self, id: str, exchange: str, logger, callback=None):
        super().__init__(id, logger)
        super().connect(exchange)
        queue_name = "q.%s.%s" % (self.exchange, self.id)
        if callback:
            self.cb_function = callback
        else:
            self.cb_function = self.process

        super()._connect_queue(queue_name)
        super()._queue_bind()

    def consume(self) -> None:
        """Register the callback function for consuming from the exchange / queue given the routing_key."""
        self.logger.info("[*] Waiting for logs.")
        self.channel.basic_consume(queue = self.queue_name, on_message_callback = self.cb_function, auto_ack = False)
        self.channel.start_consuming()

    def process(self, ch, method, properties, msg):
        """Handle the arriving message."""
        self.logger.info("received '%r'" % msg)
        print("[*] received '%r'" % msg)
        self.channel.basic_ack()


if __name__ == "__main__":

    logger = ProjectUtils.get_logger("test")
    parser = argparse.ArgumentParser(description = 'testing the mq module')
    parser.add_argument('-p', '--producer', action = 'store_true', help = "run as a producer")
    parser.add_argument('-c', '--consumer', action = 'store_true', help = "run as a consumer")
    parser.add_argument('-e', '--exchange', help = "Exchange to connect to.", required = True)
    parser.add_argument('-i', '--id', help = "Unique ID of the producer or consumer (used to set the queue name!)",
                        required = True)
    args = parser.parse_args()

    if args.producer:
        p = Producer(args.id, args.exchange, logger)
        for i in range(10):
            p.produce({"msg": i})
            time.sleep(3)
    elif args.consumer:
        c = Consumer(args.id, args.exchange, logger)
        c.consume()
    else:
        print("Need to specify one of -c or -p. See --help.", file = sys.stderr)
        sys.exit(1)