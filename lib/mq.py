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
from lib.utils.yellowsublogger import YellowsubLogger


class MQ:
    """ The message queue class """
    connection = None
    channel = None
    queue = None
    queue_name = ""
    exchange = None
    processor_name: str = ""

    logger: logging.Logger = None  # the logger to be used

    def __init__(self, processor_name: str, logger=None):
        self.processor_name = processor_name
        if not logger:
            self.logger = YellowsubLogger.get_logger()
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
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port,
                                                                                credentials=credentials))
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
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='fanout', durable=True)
        except Exception as ex:
            self.logger.error("can't Create exchange '%s'. Reason: %s" % (exchange, str(ex)))
            raise ex

    def _publish(self, msg: dict, routing_key=""):
        data = bytes(json.dumps(msg), 'utf-8')  # JSON is always utf-8
        try:
            self.channel.basic_publish(exchange=self.exchange, routing_key=routing_key, body=data,
                                       properties=pika.BasicProperties(delivery_mode=2, ),
                                       # make the message persistent
                                       mandatory=True
                                       )
        except pika.exceptions.UnroutableError as ex:
            self.logger.error("Could not publish message. Reason: {}".format(str(ex)))

    def _consume(self, queue: str, callback=None, auto_ack=False):
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=auto_ack)

    def create_queue(self, queue_name: str = ''):
        """
        Create a queue in RabbitMQ. Do not connect it yet to an exchange.
        @param queue_name: the name of the queue
        """
        self.queue = self.channel.queue_declare(queue=queue_name, durable=True, exclusive=False,
                                                auto_delete=False)
        self.logger.debug("create_queue(): queue = %r" % self.queue)
        self.channel.basic_qos(prefetch_count=1)
        self.queue_name = self.queue.method.queue
        self.logger.debug("queue_name = %r" % self.queue_name)

    def bind_queue(self):
        """
        Bind the queue to the (already created) exchange.
        """
        retv = self.channel.queue_bind(exchange=self.exchange, queue=self.queue_name)
        self.logger.debug("bind_queue(): answer = %r" % retv)

    def unbind_queue(self):
        """
        Disconnect the queue from any exchanges.
        """
        self.channel.queue_unbind(queue=self.queue_name, exchange=self.exchange)


class Producer(MQ):
    """A producer, based on the base functionality of MQ."""

    def __init__(self, processor_name: str, logger, to_ex: str, to_q: str):
        if not processor_name:
            self.logger.error("processor_name is not defined in producer. Cant continue...")
            sys.exit(1)

        if not to_ex:
            self.logger.error("to_ex is not defined in producer. Cant continue...")
            sys.exit(1)

        if not to_q:
            self.logger.error("to_q is not defined in producer. Cant continue...")
            sys.exit(1)

        super().__init__(processor_name, logger)
        super().connect2mq()

        self.create_queue(to_q)
        self.create_exchange(to_ex)
        self.bind_queue()

    def produce(self, msg: dict, routing_key: str = ""):
        """Send a msg to the exchange with the given routing_key."""
        if msg:
            super()._publish(msg=msg, routing_key=routing_key)
            self.logger.info("[x] Sent %r" % msg)
            print(f"Message sent {msg}")


class Consumer(MQ):
    """A consumer, based on the base functionality of MQ."""

    def __init__(self, processor_name: str, logger, from_q: str, callback=None):

        if not processor_name:
            self.logger.error("processor_name is not defined in producer. Cant continue...")
            sys.exit(1)

        if not from_q:
            self.logger.error("from_q is not defined in producer. Cant continue...")
            sys.exit(1)

        super().__init__(processor_name, logger)
        super().connect2mq()
        self.create_queue(from_q)

        print(f"Queue name before: {from_q}")
        self.queue_name = from_q if from_q else "q.%s.%s" % (self.exchange, self.processor_name)
        print(f"Queue name after normalization: {self.queue_name}")
        self.process= callback

    def consume(self):
        """Register the callback function for consuming from the exchange / queue given the routing_key."""

        self.logger.info("[*] Waiting for logs on queue {}.".format(self.queue_name))
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.mq_msg_callback, auto_ack=False)
        self.channel.start_consuming()

    def _convert_to_internal_df(self, msg: bytes) -> dict:
        try:
            data = json.loads(msg)
        except Exception as ex:
            self.logger.error("Could not convert msg (bytes) to msg (JSON) internal format. Reason: %s" % str(ex))
            return None
        return data

    def _validate(self, msg: dict) -> bool:
        # TODO: implement me
        return super().validate(msg)

    def mq_msg_callback(self, channel=None, method=None, properties=None, msg: bytes = None):
        """Callback function which will be registered with the MQ's callback system.
        Initially converts the (bytes) msg to an internal data format.
        Then calls the self.process() function."""

        print("1111")
        if not msg:
            print("2222")
            return
        print(f"1Message: {msg}")
        msg = self._convert_to_internal_df(msg)
        print(f"2Message: {msg}")

        # if self.processor_name in self.config['parameters'] and 'validate_msg' in self.config['parameters'][
        #     self.processor_name] and \
        #         self.config['parameters'][self.processor_name]['validate_msg']:
        #     self._validate(msg)
        self.process(channel, method, properties, msg)
        # here we submit to the other exchanges
        
        # FIXME: this MUST be called by the process method in processor, not here! 
        # self.ack(method)

    def ack(self, method):
        """
        Acknowledge a message to RabbitMQ.
        @param method: the method parameter from process()
        """
        self.channel.basic_ack(delivery_tag=method.delivery_tag)


def my_test_process(channel=None, method=None, properties=None, msg: bytes = None):
    print(msg)
    print("hello world")

if __name__ == "__main__":

    logger = logging.getLogger()

    _c = Config()
    config = _c.load()
    print("Loaded config: %r" % config)
    parser = argparse.ArgumentParser(description='testing the mq module')
    parser.add_argument('-p', '--producer', action='store_true', help="run as a producer")
    parser.add_argument('-c', '--consumer', action='store_true', help="run as a consumer")
    parser.add_argument('-e', '--exchange', help="Exchange to connect2mq to.", required=False)
    parser.add_argument('-q', '--queue_name', help="Queue name to read from.", required=True)
    parser.add_argument('-i', '--processor_name',
                        help="Unique ID of the producer or consumer (used to set the queue name!)",
                        required=True)
    args = parser.parse_args()

    if args.producer:
        p = Producer(args.processor_name, logger=logger, to_ex=args.exchange, to_q=args.queue_name)
        for i in range(10):
            p.produce({"msg": i})
            time.sleep(3)
    elif args.consumer:
        if args.queue_name:
            qn = args.queue_name
        else:
            qn = ""  # auto-decide

        c = Consumer(args.processor_name, logger=logger, from_q=qn, callback=my_test_process)
        c.consume()
    else:
        print("Need to specify one of -c or -p. See --help.", file=sys.stderr)
        sys.exit(1)
