import os

class ProjectUtils():
    """Class that offers utility functions around project organisation"""
    def __init__(self):
        return None

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
        p = os.path.dirname(os.path.realpath(__file__))
        project_p = p[:p.find("yellowsub") + len("yellowsub")] + "/etc/config.yml"
        return project_p