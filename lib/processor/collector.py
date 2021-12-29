"""Collector abstract class. Inherts from Processor."""

from lib.processor.abstractProcessor import AbstractProcessor


class Collector(AbstractProcessor):
    """
    Collector class.
    """

    def __init__(self, processor_name: str, n: int = 1):
        super().__init__(processor_name, n)

    def start(self, from_q: str, to_ex: str, to_q: str):
        super().start(from_q = from_q, to_ex = to_ex, to_q = to_q)
        self.process()

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        self.logger.info(
            f"simulating a process() call... channel={channel}, method={method}, properties={properties}, msg={msg}")