"""VirusTotalHashEnricher: this basically passes through the message. Useful for testing."""

from stix2 import Bundle, Malware, Relationship
from stix2patterns.pattern import Pattern
from typing import Union
import vt
import sys

from lib.processor.enricher import Enricher


def get_file_hash_from_indicador_pattern(indicator):
    if "malicious-activity" not in indicator.indicator_types:
        return None

    pattern = Pattern(indicator.pattern)
    pattern_data = pattern.inspect()

    if "file" not in pattern_data.comparisons:
        return None

    for item in pattern_data.comparisons['file']:
        if "hashes" in item[0]:
            return item[2].strip("'")


class VirusTotalHash(Enricher):
    def __init__(self, processor_name: str, n: int = 1):
        super(VirusTotalHash, self).__init__(processor_name, n)
        try:
            self.client = vt.Client(self.config['parameters']['apikey'])
        except Exception as ex:
            sys.exit(f'Could not initialize VT API client. Did you specify an API key in the config? Reason: {str(ex)}')

    def __collect_data(self, hash: str) -> Union[None, dict]:
        """classify according to VT based on it's malware hash.
        See https://developers.virustotal.com/reference/files """
        result: vt.Object
        try:
            return self.client.get_object(f"/files/{hash}")
        except vt.error.APIError as ex:
            self.logger.error(f"No results for hash {hash} in VT. Ignoring.")
            self.logger.debug(f"No results for hash {hash} in VT. VT's response: {str(ex)}")
            return None

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):

        """
        #########################################################
        ################# FIX ME ################################
        ### The code should be replaced by the following line ###
        ###                                                   ###
        ###    bundle = msg["payload"]                        ###
        ###                                                   ###
        #########################################################
        """

        from stix2 import parse
        import base64
        import json

        bundle = base64.b64decode(msg["payload"]["raw"].encode())
        bundle = parse(json.loads(bundle))

        #######################################################

        new_objects = list()

        for obj in bundle.objects:

            if obj.type != "file":
                self.logger.debug("The object type is not a file object: {}".format(obj))
                continue

            if not obj.hashes:
                self.logger.debug("The supplied file object does not have any hashes: {}".format(obj))
                continue

            #TODO: DG_Comment: check for all hash types not just for the first one
            malware_hash_type, malware_hash = obj.hashes.items[0]

            result = self.__collect_data(malware_hash)

            if not result:
                self.logger.debug("The hash for the associated file object could not be found in VT: {}".format(obj))
                continue

            malware_name = result.get("popular_threat_classification")["suggested_threat_label"]
            malware_types = [item["value"] for item in result.get("popular_threat_classification")["popular_threat_category"]]
            # harmless_votes = int(result.get('total_votes')['harmless'])
            # malicious_votes = int(result.get('total_votes')['malicious'])

            malware = Malware(
                name=malware_name,
                malware_types=malware_types,
                is_family=False
            )

            relationship = Relationship(
                source_ref=obj.id,
                target_ref=malware.id,
                relationship_type="indicates",
            )

            new_objects.append(malware)
            new_objects.append(relationship)

        bundle = Bundle(bundle.objects, new_objects)

        """
        #########################################################
        ################# FIX ME ################################
        ### The code should be replaced by the following line ###
        ###                                                   ###
        ###    msg.payload = bundle                           ###
        ###                                                   ###
        #########################################################
        """

        data = bundle.serialize()
        msg["payload"] = data

        #######################################################

        self.producer.produce(msg, routing_key = "")
        self.consumer.ack(method)


PROCESSOR=VirusTotalHash

