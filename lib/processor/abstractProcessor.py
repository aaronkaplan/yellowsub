"""The Abstract Processor class"""

import json
import logging
from lib.mq import Consumer, Producer
from lib.config import Config, ROOTDIR
from pathlib import Path
from lib.utils.projectutils import ProjectUtils


class AbstractProcessor:
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
    to the output exchange. The exchange is configured to fan-out to multiple queues (queue 1 til queue 4).
    Queue 1 has two consumers c1 and c2. They will get the messages round robin again . Queue 2 has one consumer c3.
    Queue 3 has no consumers, Queue 4 has two consumers c4 and c5 again.
    """
    id: str = None
    consumer: Consumer = None
    producer: Producer = None
    instances: int = 1

    def __init__(self, id: str, n: int = 1):
        """
        :param id: the ID of the processor. Used to set the queue names
        :param n: Number of (unix, system) processes should be instantiated for parallel processing
        """
        assert isinstance(id, str), "ID needs to be a string."
        assert id, "ID needs a value when instantiating a processor."

        # set up the Consumer and Producers
        self.id = id
        self.instances = n
        # create self.consumer and self.producer
        # create n instances of yourself as parallel processes
        # load the global config
        _c = Config()

        #BUG:
        #TODO:  DG_Comment: this implementation does not support local testin configuration files as the path to the
        #       config file is hardcoded use of Projectuils.get_config_path_as_str would be more appropriate
        self.config = _c.load(Path(ROOTDIR) / 'etc/config.yml')
        # override with specific config

        # setup logger using the global config the processor class name and the id of the processor
        # TODO: DG_Comment :this can and should be moved to a higher level (orchestrator) as it does not pertain
        #       to the processor itself in addition setting up the logger should probably be made at the same
        #       level and not using ProjectUtils

        ProjectUtils.configure_logger(self.config, self.__class__.__name__, self.id)

        # using getLogger from ProjectUtils to get the logger
        self.logger = ProjectUtils.get_logger(self.__class__.__name__ + "." + str(self.id))

    def validate(self, msg: bytes) -> bool:
        """
        Method responsible of validating a message. Validation should do any kind
        of input checking so that on_message can process the message flawlessly

        :param msg: message to be validated
        :return: True if the message is valid, False otherwise
        """
        raise RuntimeError("not implemented in the abstract base class. This should have not been called.")

    def process(self, channel=None, method=None, properties=None, msg: bytes = None):
        """The process function. Gets called for every arriving message from the consumers.
        This function MUST be overwritten by the sub-class.

        Usually code like:

        if self.validate(msg):           # check if correct
            self.on_message(msg)
            producer.produce(msg)      # pass it on to the next queue/exchange

        :param channel: The channel the message came in from
        :param method:  the method
        :param properties: the properties attached to the message
        :param msg: the message (byte representation of a dict)
        """
        logging.info("received '%r from channel %s, method: %s, properties: %r'" % (msg, channel, method, properties))
        raise RuntimeError("not implemented in the abstract base class. This should have not been called.")

    def on_message(self, msg: bytes):
        """
        This method must be implemented to handle one single message entity

        Usually code like:

        enriched_data = enrich(msg['url'])
        if enriched_data:
            msg['url_enriched'] = enriched_data

        :param msg: python dictionary holding the valuable data to process
        """
        raise RuntimeError("not implemented in the abstract base class. This should have not been called.")


class MyProcessor(AbstractProcessor):
    """Sample of a processor."""

    msg = None

    def __init__(self, id: str, n: int = 1, incoming_queue="", outgoing_exchanges=[]):
        super().__init__(id, n)
        # here we should read the config on where to connect to...

        # this is an example only and the connection to the exchanges and incoming queues will be done by the orchestrator.
        self.consumer = Consumer(id = id, exchange = "MyEx", callback = self.process)
        self.producer = Producer(id = id, exchange = "MyEx2")

    def process(self, channel=None, method=None, properties=None, msg: bytes = None):
        """
        The main process() callback function. It gets called from rabbitMQ on every message that comes in.

        :param channel: The channel the message came in from
        :param method:  the method
        :param properties: the properties attached to the message
        :param msg: the message (byte representation of a dict). Example:  msg = b'{"msg": 0}', type(msg) = '<class 'bytes'>
        """
        self.msg = json.loads(msg)
        # validate the message here
        logging.info("MyProcessor (ID: %s). Got msg %r" % (self.id, self.msg))
        # do something with the msg in the process() function, the msg is in self.msg
        # ...
        # then send it onwards to the outgoing exchange
        self.producer.produce(msg = self.msg, routing_key = "")

    def start(self):
        """Start the processor."""
        self.consumer.consume()


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    p = MyProcessor(id = "myProc", n = 1)
    p.start()
