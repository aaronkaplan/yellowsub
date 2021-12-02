from lib.processor.parser import Parser
from typing import Dict, Any
import base64
import re
from stix2 import Bundle, File, ObservedData
import json


class HashListToStixBundleParser(Parser):
    MD5_REGEX = re.compile(r'^[a-f0-9]{32}(:.+)?$', re.IGNORECASE)
    SHA1_REGEX = re.compile(r'^[a-f0-9]{40}(:.+)?$', re.IGNORECASE)
    SHA256_REGEX = re.compile(r'^[a-f0-9]{64}(:.+)?$', re.IGNORECASE)
    HASH_REGEXES = {'MD5': MD5_REGEX, 'SHA1': SHA1_REGEX, 'SHA256': SHA256_REGEX}

    def __init__(self, processor_id: str, n: int = 1):
        super().__init__(processor_id, n)

    def process(self, channel=None, method=None, properties=None, msg: dict = Dict[Any, Any]) -> None:
        # Retrieving the raw payload
        try:
            payload = msg['payload']['raw']
        except KeyError:
            self.logger.error("could not parse msg as payload did not contain raw data: {}".format(str(msg)))
            return

        # Decoding the raw payload
        decoded_payload = base64.b64decode(payload).decode('utf-8')

        # Create list to hold created indicators
        objects = []

        # Parsing payload line by line
        for line in decoded_payload.splitlines():
            hash_family = ''
            for hash_name, regex in self.HASH_REGEXES.items():
                if regex.match(line):
                    hash_family = hash_name
                    break

            if not hash_family:
                self.logger.error("could not identify hash family for value: {}. Skipping.".format(line))
                continue

            # Creating File object
            f = File(hashes={hash_family: line})
            od = ObservedData(object_refs=[f.id])
            objects.append(f)
            objects.append(od)

        # Create the bundle
        bundle = Bundle(objects)

        # Update the payload
        msg['payload'] = json.loads(bundle.serialize(pretty=True))

        # Send the message
        self.producer.produce(msg=msg, routing_key="")
