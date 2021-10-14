from unittest import TestCase
from pathlib import Path
from lib.config import Config, ROOTDIR


class TestConfig(TestCase):

    def test_load(self):
        _c = Config()
        config = _c.load(Path(ROOTDIR) / 'etc' / "config.yml")
        assert 'general' in config
        assert 'mq' in config['general']