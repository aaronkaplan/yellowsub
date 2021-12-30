"""VirusTotalHashEnricher: this basically passes through the message. Useful for testing."""

from typing import Union
import vt
import sys

from lib.processor.enricher import Enricher


class VirusTotalHash(Enricher):
    def __init__(self, processor_name: str, n: int = 1):
        super(VirusTotalHash, self).__init__(processor_name, n)
        try:
            self.client = vt.Client(self.config['parameters']['apikey'])
        except Exception as ex:
            sys.exit(f'Could not initialize VT API client. Did you specify an API key in the config? Reason: {str(ex)}')

    def _is_harmless_by_hash(self, hash: str) -> Union[None, int]:
        """classify according to VT based on it's malware hash.
        See https://developers.virustotal.com/reference/files """
        result: vt.Object
        try:
            result = self.client.get_object(f"/files/{hash}")
        except vt.error.APIError as ex:
            self.logger.error(f"No results for hash {hash} in VT. Ignoring.")
            self.logger.debug(f"No results for hash {hash} in VT. VT's response: {str(ex)}")
            return None
        return int(result.get('total_votes')['harmless'])

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        print("yeahhhhhhhhhhhhhhhhh")
        self.producer.produce(msg, routing_key = "")
        self.consumer.ack(method)


PROCESSOR=VirusTotalHash

