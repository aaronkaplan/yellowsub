#!/usr/bin/env python


import json
import jsonschema
from pathlib import Path
import logging

from typing import Optional, Dict

from cache import cache


class DataFormat():
    def __init__(self):
        pass

    def load_schema(self, file: Path):
        """Load the JSON Schema describing the internal data format."""
        try:
            with open(file, 'r') as f:
                self.schema = json.load(f)
                logging.info("loaded JSON Schema: %s " % self.schema)
        except Exception as ex:
            logging.error('Could not load schema file. Reason: %s' % str(ex))

    def validate(self, emessage: str) -> bool:
        """Validate a message (JSON) against the schema. Returns True/False if it validates"""
        try:
            # v = jsonschema.Draft7Validator(self.schema)
            # print("foodd")
            msg = json.loads(emessage)
            # errors = sorted(v.iter_errors(msg), key = lambda e: e.path)
            jsonschema.validate(instance = msg, schema = self.schema)
            # if errors:
            #     for error in errors:
            #         logging.warning(error.message)
            #     return False
        except Exception as ex:
            # except jsonschema.exceptions.ValidationError as ex:
            logging.warning('Could not validate message against schema. Reason: %s' % (str(ex)))
            return False
        return True

    def map_to_internal(self, emessage: str) -> Optional[Dict]:
        """Map the JSON message to the internal data format. Returns None on error or on an empty message."""
        if emessage:
            return json.loads(emessage)  # note, it is already valid JSON and validated here
        else:
            return None

    def validate_semantic(self, message: dict) -> bool:
        """Validate semantically: is the contents of the fields OK?"""
        return True

    def has_been_seen(self, imessage: dict) -> bool:
        if 'meta' in imessage and imessage['meta']['uuid'] in cache:
            return True

    def add_to_cache(self, imessage: dict):
        cache[imessage['meta']['uuid']] = 1

    def dedup(self, imessage: dict) -> Optional[Dict]:
        if self.has_been_seen(imessage):
            return None
        else:
            return imessage


""" Data format example: """

data_invalid = """{
    "format": "s2-common-data-format", 
    "version": 1, 
    "type": "event",
    "metaXXXX": {
        "uuid": "25c9487c-1ae9-11ec-99a3-b3a261e8732d",
        "relations": [
            {
                "type": "is_parent_of",
                "right_side": "38bd847a-1ae9-11ec-a308-ef1417ea8564"
            }
        ]
    }
    "payload": { 
        "source.ip": "127.0.0.1",
        "source.fqdn": "example.com"
    }
}"""


if __name__ == "__main__":
    d = DataFormat()
    print(80*"=")
    print("Testing loading the schema")
    print(80*"=")
    d.load_schema(Path("dataformat_schema.json"))
    print("OK")
    print()

    print(80*"=")
    print("Testing if VALID JSON validation:")
    with open("data_sample.json") as testdata:
        data = testdata.read()
        print("Valid: %s" % d.validate(data))
    print(80*"=")
    print()

    print(80*"=")
    print("Testing if INvalid JSON will be noticed:")
    print(80*"=")
    print("Invalid test successful: %s" % (not d.validate(data_invalid)))
    print()
