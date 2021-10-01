"""The Abstract Processor class"""

import logging
import sys
import uuid
import json

from lib.mq import Consumer, Producer


class AbstractProcessor():
    """The Abstract Processor class. Here the model is that there is _ONE_ incoming consumer source
    _instance_ number of instances of the processor, each taking a message in a round robin fashion from the input queue
    (consumer). For each such message, the process() method is called and it does it's stuff. It then sends out to the
    _one_producer which is responsible for sending it to the right exchange. At the exchange, messages may be
    routed (via routing_keys) and/or fan-outed to multiple consumers further down the line.
                                                                                                                    /--> c1
    Picture:                                                                                            / -> queue 1  -> c2
    ```
    \                                                                                                  /--> queue 2  -> c3
      \  --> queue |  --> consumer c0 reads -----> process()  ---> producer sends to output exchange. -->   queue 3
     /                                                                                                \ --> queue 4  -> c4
    /                                                                                                      etc.     \ -> c5
    ```

    Here, consumer c0 reads from its (input) queue. It calls the process() function for each message.
    It does its thing with the message (f.e.x enrichment) and passes it on to its producer. The producer sends it
    to the output exchange. The exchange is configured to fan-out to mulitple queues (queue 1 til queue 4).
    Queue 1 has two consumers c1 and c2. They will get the messages round robin again . Queue 2 has one consumer c3.
    Queue 3 has no consumers, Queue 4 has two consumers c4 and c5 again.
    """
    id: str = None
    consumer = None
    producer = None
    instances: int = 1

    def __init__(self, id: str = uuid.uuid4(), n: int = 1):
        """
        :param id: the ID of the processor. Used to set the queue names
        :param n: Number of (unix, system) processes should be instantiated for parallel processing
        """
        # set up the Consumer and Producers
        self.id = id
        self.instances = n
        # create self.consumer and self.producer
        # create n instances of yourself as parallel processes

    def process(self, ch = None, method = None, properties = None, msg: dict = {}):
        """The process function. Gets called for every arriving message from the consumers.
        This function MUST be overwritten by the sub-class.

        Usually code like:

        msg = consumer.consume()
        if validate_msg(msg):           # check if correct
            enriched_data = enrich(msg['url'])
            if enriched_data:
                msg['url_enriched'] = enriched_data
            producer.produce(msg)      # pass it on to the next queue/exchange

        :param ch: channel
        :param method:  the method
        :param properties: the properties attached to the message
        :param msg: the message (dict)
        """
        logging.info("received '%r from channel %s, method: %s, properties: %r'" % (msg, ch, method, properties))
        raise RuntimeError("not implemented in the abstract base class. This should have not been called.")


class StdinProcessor(AbstractProcessor):
    """This processor can read line by line from stdin and calls the process() method for it."""

    def __init__(self, id: str, n: int = 1):
        """Here we go into an endless loop and pull from stdin and call the process() function on each line."""

        super().__init__()
        for line in sys.stdin.readlines():
            line = line.rstrip()
            logging.debug("StdinProcessor (ID: %s). Got line %s" % (self.id, line))
            self.process(line)


class StdoutProcessor(AbstractProcessor):
    """This processor will consume from its input queue, process the message and then send it to stdout, line by line"""

    def __init__(self, id: str, n: int = 1):
        super().__init__()
        # register process function for consumer

    def send(self, msg: dict):
        sys.stdout.write(json.dumps(msg))


if __name__ == "__main__":
    p = StdinProcessor("myStdinProcessor", n=1)
