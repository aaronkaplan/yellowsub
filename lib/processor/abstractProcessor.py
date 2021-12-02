"""The Abstract Processor class"""

import json
import sys
from pathlib import Path
from typing import List

from pydantic.utils import deep_update

from lib.config import Config, GLOBAL_CONFIG_PATH, PROCESSOR_CONFIG_DIR
from lib.mq import Consumer, Producer
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
    processor_id: str = None
    consumer: Consumer = None
    producer: Producer = None

    in_queue: str = None
    out_exchanges: List[str] = []  # FIXME

    instances: int = 1
    config = dict()
    logger = None

    def __init__(self, processor_id: str, n: int = 1):
        """
        :param processor_id: the ID of the processor. Used to set the queue names
        :param n: Number of (unix, system) processes should be instantiated for parallel processing
        """
        assert isinstance(processor_id, str), "ID needs to be a string."
        assert processor_id, "ID needs a value when instantiating a processor."

        self.processor_id = processor_id
        self.instances = n

        # make sure the config is loaded
        self.load_config(processor_id)

        # setup logger using the global config the processor class name and the processor_id of the processor
        # TODO: DG_Comment :this can and should be moved to a higher level (orchestrator) as it does not pertain
        #       to the processor itself in addition setting up the logger should probably be made at the same
        #       level and not using ProjectUtils
        ProjectUtils.configure_logger(self.config, self.__class__.__name__, self.processor_id)

        # using getLogger from ProjectUtils to get the logger
        self.logger = ProjectUtils.get_logger(self.__class__.__name__ + "." + str(self.processor_id))

        # Do other startup stuff like connecting to an enrichment DB such as maxmind or so.
        # Load the input queue and output exchanges, this processor will have to connect to

    def load_config(self, processor_id: str):
        """
        Load the global config file (usually etc/config.yml) and also check if a specific config file
        for this processor exists in etc.d/<processor_id>.yml. If such a specific config file exist, merge it into the
        self.config dict

        :param processor_id: The processor's ID string
        """
        # load the global config
        _c = Config()
        try:
            self.config = _c.load(Path(GLOBAL_CONFIG_PATH))
        except Exception as ex:
            print("Error while loading processor {}'s global config. Reason: {}".format(self.processor_id, str(ex)))
            sys.exit(255)

        # merge in the specific config
        try:
            specific_config = _c.load(Path(PROCESSOR_CONFIG_DIR) / "{}.yml".format(processor_id))
            self.logger.debug("Specific config found: {}".format(specific_config))
            if not self.validate_specific_config(specific_config):
                self.logger.error(
                        "Specific config for processor ID {} is invalid. Can't start it.".format(self.processor_id))
                sys.exit(254)
            self.config = deep_update(self.config,
                                      specific_config)  # FIXME, might need to re-initialize the logger here
        except Exception as ex:
            self.logger.error(
                    "Error while loading processor {}'s specific config. Reason: {}".format(self.processor_id, str(ex)))
            sys.exit(255)

    def validate(self, msg: bytes) -> bool:
        """
        Method responsible of validating a message. Validation should do any kind
        of input checking so that on_message can process the message flawlessly

        @param msg: message to be validated
        @return: True if the message is valid, False otherwise
        """
        raise RuntimeError("not implemented in the abstract base class. This should have not been called.")

    def validate_specific_config(self, config: dict) -> bool:
        """
        Validate a specific
        @param config:
        @return:
        """
        if 'name' not in config and self.processor_id != config['name']:
            return False
        if 'parameters' not in config:
            return False
        return True

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
        self.logger.info(
                "received '%r from channel %s, method: %s, properties: %r'" % (msg, channel, method, properties))
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

    def start(self, from_ex: str, from_queue: str, to_ex: str):
        """
        start() will connect the processor to its output exchanges and its input queue (in this order).
        After connecting to the queues and exchanges, the processor can start  processing incoming messages.

        The start function will then signal the orchestrator, that this processor is running.

        The difference to the __init__() function is that, __init__() shall deal with loading of the config,
        connecting to DBs, reading in supporting data sets, etc.
        Therefore, the assumption here is that the config for this processor is already loaded at this stage.

        @param from_ex: which exchange to connect to from_queue
        @param from_queue: which queue to read from. The queue will be connected to from_ex
        @param to_ex: which exchanges (possibly multiple) to send to.

        """
        self.in_exchange = from_ex
        self.in_queue = from_queue
        self.out_exchange = to_ex

        # first start with the output side
        if self.out_exchange:
            self.producer = Producer(processor_id = self.processor_id, exchange = self.out_exchange, logger = self.logger)
            self.producer.start()

        # then the input side
        if self.in_exchange:
            # need a Consumer, bind the consumer to the in_exchange
            self.consumer = Consumer(processor_id = self.processor_id, exchange = self.in_exchange,
                                     queue_name = self.in_queue, logger = self.logger)
            self.consumer.start()

        """
        # XXX FIXME
        # we know, based on the specific config, what kind processor group this is: collector, output, enricher, etc.
        if self.config['group'] == "collector":
            # only need out_exchanges
            for exchange in self.out_exchanges:
                self.consumer = Consumer(processor_id = self.processor_id, exchange = exchange, logger = self.logger)
        elif self.config['group'] == "outputProcessor":
            # only need from_ex
            self.consumer = Consumer(processor_id = self.processor_id, in_queue = from_ex, logger = self.logger)
        else:
            # need both
            pass
        """

    def reload(self):
        """
        Reload the config. Possibly also reconnect to different input queues and/or output exchanges.
        """
        pass

    def pause(self):
        """
        Pause processing of infos. Connections to incoming MQs and outgoing exchanges will remain open.
        """
        pass

    def stop(self):
        """
        Stop processing, disconnect from incoming MQs, outgoing exchanges. Tear down DB connections etc.
        """
        pass


class MyProcessor(AbstractProcessor):
    """Sample of a processor."""

    msg = None

    def __init__(self, processor_id: str, n: int = 1, incoming_queue="", outgoing_exchanges=[]):
        super().__init__(processor_id, n)
        # here we should read the config on where to connect to...

        # this is an example only and the connection to the exchanges and incoming queues will be done by the orchestrator.
        self.consumer = Consumer(processor_id = processor_id, exchange = "MyEx", callback = self.process,
                                 queue_name = "", logger = self.logger)
        self.producer = Producer(processor_id = processor_id, exchange = "MyEx2", logger = self.logger)

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
        self.logger.info("MyProcessor (ID: %s). Got msg %r" % (self.processor_id, self.msg))
        # do something with the msg in the process() function, the msg is in self.msg
        # ...
        # then send it onwards to the outgoing exchange
        self.producer.produce(msg = self.msg, routing_key = "")
