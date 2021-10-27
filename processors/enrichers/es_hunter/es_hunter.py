import logging
import socket
import uuid
from lib.processor.enricher import Enricher


# see https://stackoverflow.com/questions/2805231/how-can-i-do-dns-lookups-in-python-including-referring-to-etc-hosts
# thanks stackoverflow


def elastic_hunter_lookup_hash(hash: str) -> bool:
    """
        This function looks up sometihing in ES ES hunter and returns True if it finds something
    """

    try:
        data = self.es_conn.lookup(hash)
    except Exception as ex:
        logging.info("Could not look up data in ES Hunter (key: %s). Reason: %s" % (hash, str(ex)))
        return False
    if not data:
        return False
    return True


class ElasticHunter_Hash_Lookup(Enricher):
    """A very simple / KISS gethostbyname enricher. """
    es_conn = None

    def __init__(self):
        # Conenct to ES
        # es_conn =
        pass

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        hash = msg.get('hash', None)
        if hash:
            rc = elastic_hunter_lookup_hash(hash)
            msg['found_in_es_hunter'] = rc
        return msg


if __name__ == "__main__":
    # make a unit test...
    pass