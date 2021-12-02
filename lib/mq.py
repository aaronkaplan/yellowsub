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
    processor_id: str = ""

    logger: logging.Logger = None  # the logger to be used

    def __init__(self, processor_id: str, logger=None):
        self.processor_id = processor_id
        if not logger:
            self.logger = ProjectUtils.get_logger()
        else:
            self.logger = logger
        _c = Config()
        self.config = _c.load(Path(GLOBAL_CONFIG_PATH))
        self.logger.info("Loaded global config")

    def close(self):
        """
        Tear down the RabbitMQ connection and channel.
        """
        self.logger.info("Disconnecting from MQ")
        self.unbind_queue()
        self.channel.close()
        self.connection.close()

    def _setup_channel(self):
        """
        Do the RabbitMQ channel setup. No creation of queues, exchanges etc. yet.
        Internal method, called by connect2mq().
        """
        try:
            self.logger.info("Setting up the channels...")
            self.channel = self.connection.channel()
            self.channel.confirm_delivery()  # required to be informed if a basic_publish() fails!
            self.logger.debug("channel = %r" % self.channel)
        except Exception as ex:
            self.logger.error("can't set up channel. Reason: %s. Bailing out." % (str(ex)))
            sys.exit(-2)
        self.logger.info("Done")

    def connect2mq(self):
        """Connect to the MQ system. Calls _setup_channel()"""

        try:
            self.logger.info("Connecting to RabbitMQ...")
            host = self.config['rabbitmq']['host']
            port = int(self.config['rabbitmq'].get('port', 5672))
            # user and password config
            user = self.config['rabbitmq'].get('user', "guest")
            password = self.config['rabbitmq'].get('password', "guest")
            credentials = pika.PlainCredentials(user, password)
            self.logger.info("Attempting to connect2mq with (%s:%d as %s/%s)" % (host, port, user,
                                                                                 sanitize_password_str(password)))
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host = host, port = port,
                                                                                credentials = credentials))
        except Exception as ex:
            self.logger.error("can't connect2mq to the MQ system. Bailing out. Reason: %s" % (str(ex)))
            sys.exit(-1)
        self.logger.info("Done. Connected!")
        self._setup_channel()

    def create_exchange(self, exchange: str = ""):
        """
        Create an exchange. This operation is idempotent. Pre-condition: channel and connection was set up.
        @param exchange: the name of the exchange
        """
        self.exchange = exchange
        self.logger.info("Creating exchange %s" % exchange)
        try:
            self.channel.exchange_declare(exchange = self.exchange, exchange_type = 'fanout', durable = True)
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

    def create_queue(self, queue_name: str = ''):
        """
        Create a queue in RabbitMQ. Do not connect it yet to an exchange.
        @param queue_name: the name of the queue
        """
        self.queue = self.channel.queue_declare(queue = queue_name, durable = True, exclusive = False,
                                                auto_delete = False)
        self.channel.basic_qos(prefetch_count = 1)
        # self.queue_name = self.queue.method.queue

    def bind_queue(self):
        """
        Bind the queue to the (already created) exchange.
        """
        self.channel.queue_bind(exchange = self.exchange, queue = self.queue_name)

    def unbind_queue(self):
        """
        Disconnect the queue from any exchanges.
        """
        self.channel.queue_unbind(queue = self.queue_name, exchange = self.exchange)


class Producer(MQ):
    """A producer, based on the base functionality of MQ."""

    def __init__(self, processor_id: str, exchange: str, logger):
        super().__init__(processor_id, logger)
        self.connect2mq()
        self.exchange = exchange

    def start(self):
        """Create queues bind them. Make stuff flowing from to the output exchange."""
        super().create_exchange(self.exchange)

    def produce(self, msg: dict, routing_key: str = ""):
        """Send a msg to the exchange with the given routing_key."""
        if msg:
            super()._publish(msg = msg, routing_key = routing_key)
            self.logger.info("[x] Sent %r" % msg)


class Consumer(MQ):
    """A consumer, based on the base functionality of MQ."""

    cb_function = None

    def __init__(self, processor_id: str, exchange: str, queue_name: str, logger, callback=None):
        super().__init__(processor_id, logger)
        super().connect2mq()
        super().create_exchange(exchange)  # should have been done by the producer.

        # establish callback. Here you can override the callback function if needed.
        if callback:
            self.cb_function = callback
        else:
            self.cb_function = self.process

        if not queue_name:
            queue_name = "q.%s.%s" % (self.exchange, self.processor_id)  # default
        self.queue_name = queue_name

    def start(self):
        """Create queues bind them. Make stuff flowing from the input queue."""
        super().create_queue(self.queue_name)
        super().bind_queue()
        self.consume()

    def consume(self) -> None:
        """Register the callback function for consuming from the exchange / queue given the routing_key."""
        self.logger.info("[*] Waiting for logs on queue {}.".format(self.queue_name))
        self.channel.basic_consume(queue = self.queue_name, on_message_callback = self.cb_function, auto_ack = False)
        self.channel.start_consuming()

    def process(self, ch, method, properties, msg):
        """Handle the arriving message."""
        # raise RuntimeError("Not implemented in the abstract Consumer. Need to override this method in the derived "
        #                    "class.")
        #
        # A typical Consumer would do:
        self.logger.info("[*] received '%r'" % msg)
        #   # ACKing is important:
        self.channel.basic_ack(delivery_tag = method.delivery_tag)


if __name__ == "__main__":

    _c = Config()
    config = _c.load()
    print("Loaded config: %r" % config)

    ProjectUtils.configure_logger(config, processor_class = None, processor_id = None)
    logger = ProjectUtils.get_logger("")
    parser = argparse.ArgumentParser(description = 'testing the mq module')
    parser.add_argument('-p', '--producer', action = 'store_true', help = "run as a producer")
    parser.add_argument('-c', '--consumer', action = 'store_true', help = "run as a consumer")
    parser.add_argument('-e', '--exchange', help = "Exchange to connect2mq to.", required = True)
    parser.add_argument('-q', '--queue_name', help = "Queue name to read from.", required = False)
    parser.add_argument('-i', '--processor_id',
                        help = "Unique ID of the producer or consumer (used to set the queue name!)",
                        required = True)
    args = parser.parse_args()

    if args.producer:
        p = Producer(args.processor_id, args.exchange, logger)
        for i in range(10):
            p.produce({"msg": i})
            time.sleep(3)
    elif args.consumer:
        if args.queue_name:
            queue_name = args.queue_name
        else:
            queue_name = ""     # auto-decide
        c = Consumer(args.processor_id, args.exchange, queue_name = queue_name, logger = logger)
        c.consume()
    else:
        print("Need to specify one of -c or -p. See --help.", file = sys.stderr)
        sys.exit(1)
