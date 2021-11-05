from unittest import TestCase
from pathlib import Path
from lib.config import Config, ROOTDIR
from lib.utils.projectutils import ProjectUtils

class TestConfig(TestCase):

    def test_load(self):
        _c = Config()
        pu = ProjectUtils()
        config = _c.load(pu.get_config_path_as_str())
        assert 'general' in config
        assert 'mq' in config['general']

