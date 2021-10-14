"""
A simple config loader.

USAGE EXAMPLE:

from config import config

TTL = config['redis'].get('cache_ttl', 24*3600)         # 1 day default

"""

import os
import logging
import yaml
from pathlib import Path


__all__ = ["config", "Config"]


class Config:
    """The Configuration file class."""
    params = dict()

    def __init__(self):
        self.params = dict()

    def load(self, file: Path):
        """Load the config file."""
        try:
            with open(file, 'r') as _f:
                self.params = yaml.safe_load(_f)
        except Exception as ex:
            print("could not load config file %s. Reason: %s" % (file, str(ex)))
        return self.params


ROOTDIR = os.getenv('ROOTDIR', '/')

_c = Config()
config = _c.load(Path(ROOTDIR) / 'etc' / "config.yml")
logging.info(config)
