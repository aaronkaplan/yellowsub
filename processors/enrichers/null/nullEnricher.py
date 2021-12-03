"""NullEnricher: this basically passes through the message. Useful for testing."""

from lib.processor.enricher import Enricher

class nullEnricher(Enricher):
    def __init__(self, processor_id: str, n: int = 1):
        super(nullEnricher, self).__init__(processor_id, n)

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        self.producer.produce(msg, routing_key = "")
        self.consumer.ack(method)