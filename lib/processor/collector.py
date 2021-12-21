"""Collector abstract class. Inherts from Processor."""

from lib.processor.processor import Processor


class Collector(Processor):

    def __init__(self, processor_name: str, n: int = 1):
        super().__init__(processor_name, n)

    def start(self, from_ex: str, from_queue: str, to_ex: str):
        super().start(from_ex=from_ex, from_queue=from_queue, to_ex=to_ex)
        self.process()
