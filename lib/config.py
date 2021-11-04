"""
A simple config loader.

USAGE EXAMPLE:

from config import config

TTL = config['redis'].get('cache_ttl', 24*3600)         # 1 day default

"""

import logging
import yaml
from pathlib import Path
from lib.utils.projectutils import ProjectUtils


__all__ = ["config", "Config"]


class Config:
    """The Configuration file class."""
    params = dict()

    def __init__(self):
        self.params = dict()

    def load(self, file: Path):
        """Load the config file."""
        # if no path is supplied get the config from the default location inside the project folder
        if file is None:
            p = ProjectUtils()
            file = Path(p.get_config_path_as_str())
        try:
            with open(file, 'r') as _f:
                self.params = yaml.safe_load(_f)
        except (OSError, FileNotFoundError) as ex:
            print("could not load config file %s. Reason: %s" % (file, str(ex)))
        return self.params

    def __getitem__(self, item):
        if item in self.params.keys():
            return self.params[item]
        else:
            return None


# TODO:     Implement as standalone class and instantiate wherever necessary, idealy through projectutils and
#           env varibales rather than instantiating globally. Will probably need to implement all the interfaces
#           that dict implements at that point to support dict like interaction.
# if __name__ == "__main__":

p = ProjectUtils()
ROOTDIR = p.get_project_path_as_str()
config_file_path_str = p.get_config_path_as_str()
_c = Config()
config = _c.load(Path(config_file_path_str))

# config['general']['ROOTDIR'] = ROOTDIR
logging.info(config)
