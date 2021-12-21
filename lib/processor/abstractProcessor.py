"""The Abstract Processor class"""

import sys
from pathlib import Path
from typing import List
import logging
import argparse

import yaml
from pydantic.utils import deep_update

from importlib import import_module

from lib.config import Config, GLOBAL_CONFIG_PATH, PROCESSOR_CONFIG_DIR, GLOBAL_WORKFLOW_PATH
from lib.mq import Consumer, Producer
from lib.utils.yellowsublogger import YellowsubLogger


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
    processor_name: str = None  # the unique name of the processor
    consumer: Consumer = None  #
    producer: Producer = None

    from_q: str = None
    to_ex: str

    instances: int = 1
    config = dict()     # the merged configuration for the processor.
    logger = None

    
    def __init__(self, processor_name: str, n: int = 1):
        """
        :param processor_name: the ID of the processor. Used to set the queue names
        :param n: Number of (unix, system) processes should be instantiated for parallel processing
        """
        assert isinstance(processor_name, str), "ID needs to be a string."
        assert processor_name, "processor_name needs a value when instantiating a processor."
        # TODO: DG_Comment: check that the name of the processor matches case-insensitive with the class name it is
        #                   implemented in as per the project convention fail otherwise

        self.processor_name = processor_name
        self.instances = n

        # initial logger, this is going to be overwritten
        self.logger = logging.getLogger()

        # make sure the config is loaded
        self.load_config(processor_name)

        # setup logger using the global config the processor class name and the processor_name of the processor
        # TODO: DG_Comment :this can and should be moved to a higher level (orchestrator) as it does not pertain
        #       to the processor itself in addition setting up the logger should probably be made at the same
        #       level and not using ProjectUtils
        # self.logger = YellowsubLogger.get_logger()

        # Do other startup stuff like connecting to an enrichment DB such as maxmind or so.
        # Load the input queue and output exchanges, this processor will have to connect to

    def load_config(self, processor_name: str):
        """
        Load the global config file (usually etc/config.yml) and also check if a specific config file
        for this processor exists in etc.d/<processor_name>.yml. If such a specific config file exist, merge it into the
        self.config dict

        :param processor_name: The processor's ID string
        """
        # load the global config
        _c = Config()
        try:
            self.config = _c.load(Path(GLOBAL_CONFIG_PATH))
        except Exception as ex:
            print("Error while loading processor {}'s global config. Reason: {}".format(self.processor_name, str(ex)))
            sys.exit(255)

        # merge in the specific config
        try:
            specific_config = _c.load(Path(PROCESSOR_CONFIG_DIR) / "{}.yml".format(processor_name))
            self.logger.debug("Specific config found: {}".format(specific_config))
            if not self.validate_specific_config(specific_config):
                self.logger.error(
                    "Specific config for processor ID {} is invalid. Can't start it.".format(self.processor_name))
                sys.exit(254)
            self.config = deep_update(self.config,
                                      specific_config)  # FIXME, might need to re-initialize the logger here
        except Exception as ex:
            self.logger.error(
                "Error while loading processor {}'s specific config. Reason: {}".format(self.processor_name, str(ex)))
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
        if 'name' not in config and self.processor_name != config['name']:
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

    def start(self, from_q: str, to_ex: str, to_q: str):
        """
        start() will connect the processor to its output exchanges and its input queue (in this order).
        After connecting to the queues and exchanges, the processor can start  processing incoming messages.

        The start function will then signal the orchestrator, that this processor is running.

        The difference to the __init__() function is that, __init__() shall deal with loading of the config,
        connecting to DBs, reading in supporting data sets, etc.
        Therefore, the assumption here is that the config for this processor is already loaded at this stage.

        If you are looking for the main "run" entrypoint to a Processor, please look at the "run()" method (which
        in turn calls start(...) with the right params).

        @param from_ex: which exchange to connect to from_queue
        @param from_queue: which queue to read from. The queue will be connected to from_ex
        @param to_ex: which exchanges (possibly multiple) to send to.

        """

        self.from_q = from_q
        self.to_ex = to_ex
        self.to_q = to_q

        # first start with the output side
        if self.to_ex:
            print("about to start a producer...")
            self.producer = Producer(processor_name = self.processor_name, exchange = self.to_ex, to_q = self.to_q,
                                     logger = self.logger)
            self.producer.start()

        # then the input side
        if self.in_exchange:
            # need a Consumer, bind the consumer to the in_exchange
            print("about to start a consumer...")
            self.consumer = Consumer(processor_name = self.processor_name, from_q = self.from_q, queue_name = self.from_q, logger = self.logger)
            self.consumer.start()

    @classmethod
    def load_workflows(cls, processor_name: str) -> dict:
        """Load the wokflow.yml file and iterate over all workflows which are defined there.
        For each workflow, check out if <processor_name> is in the "processor" key-value pairs in a workflow.
        If yes, read that dict line and yield back a dict : { "from": <queuename as string>, "to": <exchange name as str> }

        """
        file = GLOBAL_WORKFLOW_PATH
        try:
            with open(file, 'r') as _f:
                workflows = yaml.safe_load(_f)
        except (OSError, FileNotFoundError) as ex:
            logging.error('Could not load workflow config file %s. Reason: %s' % (file, str(ex)))
            raise ValueError('File not found: %r.' % file)
            # FIXME: here, we might also have other exceptions maybe? Catch them!

        retval = dict()
        # see workflow.yml for an example of how it looks like
        for name, settings in workflows.items():

            if 'flow' not in settings:
                continue

            for flow in settings["flow"]:

                if 'processor' not in flow:
                    continue
                
                if flow['processor'] not in processor_name:
                    continue

                retval['from_q'] = flow.get('from_q', None)
                retval['to_ex'] = flow.get('to_ex', None)
                retval['to_q'] = flow.get('to_q', None)
                retval['parallelism'] = flow.get('parallelism', 1)

                yield retval

    @classmethod
    def _create_argparser(cls):
        """
        shamlessly copied & modified from intelmq
        """
        argparser = argparse.ArgumentParser(usage='%(prog)s [OPTIONS] PROCESSOR_NAME')
        argparser.add_argument('processor_name', nargs='?', metavar='PROCESSOR_NAME', help='unique processor_name')
        return argparser

    @classmethod
    def run(cls, parsed_args=None):
        """The main entry point (without parameters). run() calls start(...) with the proper params."""

        if not parsed_args:
            parsed_args = cls._create_argparser().parse_args()

        if not parsed_args.processor_name:
            sys.exit('No processor name given.')
        processor_name = parsed_args.processor_name


        # next read the workflow.yml config -> we need to get the input queue and output exchange.
        workflows = cls.load_workflows(processor_name)      # generator
        
        # # get the module name:
        # modulename="processors.collectors.filecollector"
        # try:
        #     module = import_module(modulename)
        # except Exception as ex:
        #     print(f"Error loading module: {modulename}. Reason: {ex}")
        #     sys.exit(252)

        # clsname = getattr(module, "PROCESSOR", None)
        # if not clsname:
        #     print(f"Could not find the class name in module {modulename}. Exiting.")
        #     sys.exit(251)
 
        # instance = cls(processor_name)
        

        # IDEA taken from intelmq:
        # 1. read the python module (importlib or similar)
        # 2. read the PROCESSOR variable --> this gives the name of the class we need to instantiate in run()
        # 3. the run() class method gets the from: /to: exchanges
        # 4. it will then create an object instance of that particular Processor class and...
        # 5. call the start() method with the from: / to: paramaters
        # #### --> ignroe, this is already in a separate unix process, since we started it from the bash shell (was: but as a separate unix process... (popen, psutils)

        instance = cls(processor_name)

        for workflow in workflows:
            instance.start(to_q=workflow['from_q'], from_queue=workflow['from_q'], to_ex=workflow['to_ex'])

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

# class MyProcessor(AbstractProcessor):
#     """Sample of a processor."""
#
#     msg = None
#
#     def __init__(self, processor_name: str, n: int = 1, incoming_queue="", outgoing_exchanges=[]):
#         super().__init__(processor_name, n)
#         # here we should read the config on where to connect to...
#
#         # this is an example only and the connection to the exchanges and incoming queues will be done by the orchestrator.
#         self.consumer = Consumer(processor_name=processor_name, exchange="MyEx", callback=self.process,
#                                  queue_name="", logger=self.logger)
#         self.producer = Producer(processor_name=processor_name, exchange="MyEx2", logger=self.logger)
#
#     def process(self, channel=None, method=None, properties=None, msg: bytes = None):
#         """
#         The main process() callback function. It gets called from rabbitMQ on every message that comes in.
#
#         :param channel: The channel the message came in from
#         :param method:  the method
#         :param properties: the properties attached to the message
#         :param msg: the message (byte representation of a dict). Example:  msg = b'{"msg": 0}', type(msg) = '<class 'bytes'>
#         """
#         self.msg = json.loads(msg)
#         # validate the message here
#         self.logger.info("MyProcessor (ID: %s). Got msg %r" % (self.processor_name, self.msg))
#         # do something with the msg in the process() function, the msg is in self.msg
#         # ...
#         # then send it onwards to the outgoing exchange
#         self.producer.produce(msg=self.msg, routing_key="")


if __name__ == "__main__":
    x = AbstractProcessor("filecollector")
    [ y for y in x.load_workflows("filecollector") ]