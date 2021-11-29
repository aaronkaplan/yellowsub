#!/usr/bin/env python
"""DataModel definitions and classes."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

import jsonschema

from lib.utils.cache import cache


class DataModel:
    """The main DataModel utility class."""
    schema = None

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
            msg = json.loads(emessage)
            jsonschema.validate(instance = msg, schema = self.schema)
        except Exception as ex:
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
        """Check if a message has been cached before."""
        if 'meta' in imessage and imessage['meta']['uuid'] in cache:
            return True

    def add_to_cache(self, imessage: dict):
        """Add a message to the cache."""
        cache[imessage['meta']['uuid']] = 1

    def dedup(self, imessage: dict) -> Optional[Dict]:
        """De-duplicate . Returns None if the message has already been seen."""
        if self.has_been_seen(imessage):
            return None
        else:
            return imessage


""" Data model example: """

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
    d = DataModel()
    print(80 * "=")
    print("Testing loading the schema")
    print(80 * "=")
    d.load_schema(Path("datamodel/yellowsub_schema.json"))
    print("OK")
    print()

    print(80 * "=")
    print("Testing if VALID JSON validation:")
    with open("data_sample.json") as testdata:
        data = testdata.read()
        print("Valid: %s" % d.validate(data))
    print(80 * "=")
    print()

    print(80 * "=")
    print("Testing if INvalid JSON will be noticed:")
    print(80 * "=")
    print("Invalid test successful: %s" % (not d.validate(data_invalid)))
    print()
