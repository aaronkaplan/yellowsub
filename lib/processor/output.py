"""OutputProcessor abstract class. Inherts from Processor."""

from lib.processor.processor import Processor


class OutputProcessor(Processor):
    def __init__(self, processor_id: str, n: int = 1):
        super().__init__(processor_id, n)
