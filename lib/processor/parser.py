"""Parser abstract class. Inherts from Processor."""

from lib.processor.processor import Processor


class Parser(Processor):

    def __init__(self, processor_name: str, n: int = 1):
        super().__init__(processor_name, n)
