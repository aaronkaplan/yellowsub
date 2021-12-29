"""VirusTotalHashEnricher: this basically passes through the message. Useful for testing."""

from lib.processor.enricher import Enricher


class VirusTotalHash(Enricher):
    def __init__(self, processor_name: str, n: int = 1):
        super(VirusTotalHash, self).__init__(processor_name, n)

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        print("yeahhhhhhhhhhhhhhhhh")
        self.producer.produce(msg, routing_key = "")
        self.consumer.ack(method)


PROCESSOR=VirusTotalHash

