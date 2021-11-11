from lib.config import Config, ROOTDIR
from pathlib import Path
from unittest import TestCase


class TestConfig(TestCase):

    def load_testcases_config(self):
        _c = Config()
        return _c.load(Path(ROOTDIR) / 'tests/data/etc' / "config.yml")

    def test_load(self):
        config = self.load_testcases_config()
        assert isinstance(config, dict)
        assert 'general' in config
        assert 'mq' in config['general']

    def test_store(self):
        config = Config()
        with self.assertRaises(RuntimeError):
            config.store('/tmp/foo.yml')

    def test___setitem__getitem__(self):
        config = self.load_testcases_config()
        assert 'mq' in config['general']
        config['foobar'] = "xyz"
        assert config['foobar'] == "xyz"

    def test___len__(self):
        config = self.load_testcases_config()
        assert len(config) == 5
