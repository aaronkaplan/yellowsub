#!/usr/bin/env python

"""Small wrapper around a MQ system"""
import logging
import json
import time

import lib.config
import pika
from lib.config import config


class MQ:
    """ The message queue class """
    connection = None
    channel = None
    queue = None
    exchange = None

    def __init__(self):
        pass

    def connect(self, exchange: str = ""):
        """Connect to the MQ system."""

        try:
            logging.info("connecting to RabbitMQ...")
            host = config['rabbitmq']['host']
            # port config
            if config['rabbitmq'].get('port', None):
                port = int(config['rabbitmq']['port'])
            else:
                port = 5672     # default port

            # user and password config
            if config['rabbitmq'].get('user', None) and config['rabbitmq'].get('password', None):
                credentials = pika.PlainCredentials(config['rabbitmq']['user'], config['rabbitmq']['password'])
                print("Attempting to connect with (%s:%d as %s/%s)" %(host, port, user, password))
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host = host, port = port,
                                                                                    credentials = credentials))
            else:
                # credentials = pika.PlainCredentials(None, None)
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
        except Exception as ex:
            logging.error("can't connect to the MQ system. Bailing out. Reason: %s" % (str(ex)))
            return False
        logging.info("connected!")

        # set up the channel
        self.channel = self.connection.channel()
        print("channel = %r" % self.channel)
        self._create_exchange(exchange)
        print("exchange = %r" % self.exchange)

        return True

    def _create_exchange(self, exchange: str = ""):
        try:
            self.exchange = exchange
            self.channel.exchange_declare(exchange = self.exchange, exchange_type = 'fanout')
        except Exception as ex:
            logging.error("can't Create exchange '%s'. Reason: %s" % (exchange, str(ex)))
            raise ex

    def _publish(self, message: dict, routing_key=""):
        data = bytes(json.dumps(message), 'utf-8')      # JSON is always utf-8
        self.channel.basic_publish(exchange=self.exchange, routing_key=routing_key, body=data)

    def _consume(self, queue: str, callback=None, auto_ack=False):
        self.channel.basic_consume(queue = queue, on_message_callback = callback, auto_ack = auto_ack)

    def _connect_queue(self, queue: str = ''):
        self.queue = self.channel.queue_declare(queue = queue, durable = True, exclusive = True)
        self.channel.basic_qos(prefetch_count = 1)

    def _bind_queue(self, exchange: str = ""):
        self.channel.queue_bind(exchange = exchange, queue = self.queue.method.queue)


class Producer(MQ):
    """A producer, based on the base functionality of MQ."""
    def __init__(self, exchange: str):
        super().__init__()
        self.connect(exchange)

    def connect(self, exchange: str = ""):
        """Connect to an exchange."""
        logging.info("Connecting to exchange %s" % (exchange,))
        super().connect(exchange)
        # super()._connect_queue()

    def produce(self, msg: dict, routing_key: str = ""):
        """Send a msg to the exchange with the given routing_key."""
        if msg:
            super()._publish(message=msg, routing_key = routing_key)
            logging.info("[x] Sent %r" % msg)


class Consumer(MQ):
    """A consumer, based on the base functionality of MQ."""
    def __init__(self, exchange: str):
        super().__init__()
        super().connect(exchange)
        self.channel.queue_bind(exchange = self.exchange, queue = self.queue)

    def consume(self) -> None:
        """Register the callback function for consuming from the exchange / queue given the routing_key."""
        logging.info("[*] Waiting for logs.")
        self.channel.basic_consume(queue = self.queue, on_message_callback = self.process, auto_ack = True)
        self.channel.start_consuming()

    def process(self, ch, method, properties, msg):
        """Handle the arriving message."""
        logging.info("received '%r'" % msg)
        print("[*] received '%r'" % msg)


if __name__ == "__main__":
    p = Producer("hello-exchange")
    c = Consumer("hello-exchange")
    c.consume()
    p.produce({"foo": "bar"})
    for i in range(10):
        p.produce({"msg":  i})
        time.sleep(3)
