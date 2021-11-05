import os


class ProjectUtils():
    """Class that offers utility functions around project organisation"""
    def __init__(self):
        if os.getenv("YELLOWSUB_TEST") is None:
            self.config_path_rel_proj_root = "/etc/config.yml"
        else:
            if os.getenv("YELLOWSUB_TEST") == "1" or str.lower(os.getenv("YELLOWSUB_TEST")) == "true":
                self.config_path_rel_proj_root = "/etc/config_test.yml"
            else:
                self.config_path_rel_proj_root = "/etc/config.yml"

    def get_project_path_as_str(self):
        """
        Get Project root folder path as string. The method assumes that the name of the root folder is yellowsub"

        Args:

        Returns:
            str: The path of the root folder for the project as string.
        """
        p = os.path.dirname(os.path.realpath(__file__))
        project_p = p[:p.find("yellowsub") + len("yellowsub")] + "/"
        return project_p

    def get_config_path_as_str(self):
        """
        Get Project main config file path as string. The method implies that the name of the root folder is yellowsub"

        Args:

        Returns:
            str: The path of the main configuration file as string.
        """
        # p = os.path.dirname(os.path.realpath(__file__))
        # config_p = p[:p.find("yellowsub") + len("yellowsub")] + self.config_path_rel_proj_root
        return 'etc/config.yml'

    def get_logger(self):
        # ...
        """
        @return: logger instance

        parse the config
        if there is a specific logger, make a logger and return it
        if there is non, return the global logger

        """
