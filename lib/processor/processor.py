"""Processor - a subclass of Abstract Processor."""
import json
# from lib.dataformat import DataFormat
from lib.processor.abstractProcessor import AbstractProcessor


class Processor(AbstractProcessor):
    """The main Processor class, all others derive from it."""

    # logger = ...

    def __init__(self, id: str, n: int = 1):
        super().__init__(id, n)
        self.start()

    def _convert_to_internal_df(self, msg: bytes) -> dict:
        try:
            data = json.loads(msg)
        except Exception as ex:
            self.logger.error("Could not convert msg (bytes) to msg (JSON) internal format. Reason: %s" % str(ex))
            return None
        return data

    def validate(self, msg: dict) -> bool:
        # TODO: implement me
        return super().validate(msg)

    def mq_msg_callback(self, channel=None, method=None, properties=None, msg: bytes = None):
        """Callback function which will be registered with the MQ's callback system.
        Initially converts the (bytes) msg to an internal data format.
        Then calls the self.process() function."""

        if not msg:
            return
        msg = self._convert_to_internal_df(msg)
        if self.id in self.config['processors'] and 'validate_msg' in self.config['processors'][self.id] and \
                self.config['processors'][self.id]['validate_msg']:
            self.validate(msg)
        self.process(channel, method, properties, msg)
        # here we submit to the other exchanges

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        # TODO: do we need channel, method, properties here?
        raise RuntimeError("not implemented in the abstract base class. This should not have been called.")
