"""NullEnricher: this basically passes through the message. Useful for testing."""

from lib.processor.enricher import Enricher


class nullEnricher(Enricher):
    def __init__(self, processor_name: str, n: int = 1):
        super().__init__(processor_name, n)

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        print(f"got msg {msg}")
        self.producer.produce(msg, routing_key = "")
        print(f"passed on msg to {self.producer.queue_name}")
        self.consumer.ack(method)


PROCESSOR=nullEnricher
