"""
A simple config loader.

USAGE EXAMPLE:

from config import config

TTL = config['redis'].get('cache_ttl', 24*3600)         # 1 day default

"""

import yaml
from lib.utils.projectutils import ProjectUtils
from pathlib import Path

__all__ = ["ROOTDIR", "CONFIG_FILE_PATH_STR", "Config"]


class Config:
    """The Configuration file class."""
    params = dict()

    def __init__(self):
        self.params = dict()

    def load(self, file: Path):
        """Load the config file."""

        # if no path is supplied get the config from the default location inside the project folder
        if file is None:
            file = Path(ProjectUtils.get_config_path_as_str())
        try:
            with open(file, 'r') as _f:
                self.params = yaml.safe_load(_f)
        except (OSError, FileNotFoundError) as ex:
            print("could not load config file %s. Reason: %s" % (file, str(ex)))
            # FIXME: here, we might also have other exceptions maybe? Catch them!
        return self.params

    def store(self, file: Path):
        """Store the config to <file>."""

        raise RuntimeError("not implemented.")

    def __getitem__(self, item: str) -> object:
        """Get item from config."""
        if item in self.params.keys():
            return self.params[item]
        else:
            return None

    def __setitem__(self, key: str, obj: dict) -> None:
        """Store the key and the dict as part of the config."""
        self.params[key] = obj

    def __contains__(self, item: object) -> bool:
        """Check for existence of the key in the config. Note that this will only check the highest level.
        It will not iterate through the whole tree.
        """
        return item in self.params

    def __len__(self) -> int:
        """Return how many keys are stored in the config. Not particularly useful.
        But not sure what else would be useful instead tbh.
        """
        return len(self.params)


# TODO:     Implement as standalone class and instantiate wherever necessary, ideally through projectutils and
#           env variables rather than instantiating globally. Will probably need to implement all the interfaces
#           that dict implements at that point to support dict like interaction.
# if __name__ == "__main__":

# FIXME:    this still creates the global config dict. This is going away.
#           DG_Comment: I believe these globals should be part of the Config class or rather be called from PorjectUtils
#                       as static methods wherever they are needed
ROOTDIR: str = ProjectUtils.get_project_path_as_str()
CONFIG_FILE_PATH_STR: str = ProjectUtils.get_config_path_as_str()

