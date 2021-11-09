import os
import logging
import logging.handlers


class ProjectUtils:
    """Class that offers utility functions around project organisation"""

    def __init__(self):
        pass

    @staticmethod
    def get_config_path_env_var_resolved():
        """
        Get project config file path relative to the root of the project taking into consideration the env variable for
        testing

        @return:    Relative path to config file from the project root
        @rtype:     str
        """
        if os.getenv("YELLOWSUB_TEST") is None:
            return "/etc/config.yml"
        else:
            if os.getenv("YELLOWSUB_TEST") == "1" or str.lower(os.getenv("YELLOWSUB_TEST")) == "true":
                return "/etc/config_test.yml"
            else:
                return "/etc/config.yml"

    @staticmethod
    def get_project_path_as_str():
        """
        Get Project root folder path as string. The method assumes that the name of the root folder is yellowsub"

        @return:    Absolute path for the project root
        @rtype:     str
        """
        p = os.path.dirname(os.path.realpath(__file__))
        project_p = p[:p.find("yellowsub") + len("yellowsub")] + "/"
        return project_p

    @staticmethod
    def get_config_path_as_str():
        """
        Get Project main config file path as string. The method implies that the name of the root folder is yellowsub"

        @return: The path of the main configuration file as string.
        @rtype: str
        """
        p = os.path.dirname(os.path.realpath(__file__))
        config_p = p[:p.find("yellowsub") + len("yellowsub")] + ProjectUtils.get_config_path_env_var_resolved()
        return config_p

    @staticmethod
    def __setup_root_logger(config: dict = None):
        """
        Setup the root logger as per the config.yml parsed dictionary. This method should be considered private

        @param config: Dictionary containing the parsed config.yml
        @type config: dict
        @return: None
        @rtype: None
        """
        root_logger = logging.getLogger("yellowsub")
        if len(root_logger.handlers) == 0:
            if "logging" not in config.keys():
                raise RuntimeError("the global logger is not defined in the config")
            else:
                formatter = logging.Formatter('%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s')
                logger_config = config["logging"]
                log_level = logger_config["loglevel"]
                handlers = []

                for h in logger_config["handlers"]:
                    handler_config = h["handler"]
                    if handler_config["type"] != "TimedRotatingFileHandler":
                        raise NotImplementedError("the only supported logging handler is TimedRotatingFileHandler")
                    h_type = handler_config["type"]
                    h_output = handler_config["output"]
                    h_log_level = handler_config["loglevel"]
                    handler = getattr(logging.handlers, h_type)(h_output, when="midnight", interval=1,
                                                                backupCount=30)
                    handler.setLevel(h_log_level)
                    handler.setFormatter(formatter)
                    handlers.append(handler)

                root_logger.setLevel(log_level)
                root_logger.propagate = False
                for h in handlers:
                    root_logger.addHandler(h)

    # TODO: DG_Comment: break the parsing of the config in a different function this should be actually implemented
    #       entirely in the "orchestrator" in order to parse config in one place only. The only method implemented in
    #       this class should be the get_logger method
    @staticmethod
    def configure_logger(config: dict = None, processor_class: str = None, processor_id: str = None):
        """
        Configure a logger as per the config.yml parsed dictionary

        @param config: Dictionary containing the parsed config.yml
        @type config: dict
        @param processor_class: Processor class as returned by self.__class__.__name__ from within the calling class.
                                This must match case-insensitive with the processor name inside the config.yml
        @type processor_class: str
        @param processor_id: The ID of the processor that this logger is being set up for as returned by self.id from
                                withing the calling class
        @type processor_id: str
        @return: None
        @rtype: None
        """
        if type(config) != dict:
            raise TypeError("config parameter should be of type dict")
        elif len(config.keys()) == 0:
            raise RuntimeError("The config dictionary supplied for configuring loggers is empty")

        # DG_Comment: If called without a type it will setup the root logger unless previously set up
        if processor_class is None:
            ProjectUtils.__setup_root_logger(config)
        # DG_Comment: Check if the config contains configuration for the processor(safety check)
        elif processor_class.lower() not in config["processors"]:
            raise RuntimeError("The processor class is not defined in the config")
        # DG_Comment: set individual loggers per processor
        else:
            ProjectUtils.__setup_root_logger(config)
            processor_config = config["processors"][processor_class.lower()]
            # If there is not a specific processor level logger setup the root logger
            if "logging" not in processor_config.keys():
                ProjectUtils.__setup_root_logger(config)
            # DG_Comment: If there is a specific processor level logger set it up
            else:
                processor_logger = logging.getLogger("yellowsub." + processor_class.lower() + "." + processor_id)
                if len(processor_logger.handlers) == 0:
                    formatter = logging.Formatter('%(asctime)s|%(created)s|%(name)s|%(levelname)s: %(message)s')
                    logger_config = processor_config["logging"]
                    log_level = logger_config["loglevel"]
                    handlers = []
                    for h in logger_config["handlers"]:
                        handler_config = h["handler"]
                        if handler_config["type"] != "TimedRotatingFileHandler":
                            raise NotImplementedError(
                                "the only supported logging handler is TimedRotatingFileHandler")
                        h_type = handler_config["type"]
                        h_output = handler_config["output"]
                        h_log_level = handler_config["loglevel"]
                        handler = getattr(logging.handlers, h_type)(h_output, when="midnight", interval=1,
                                                                    backupCount=30)
                        handler.setLevel(h_log_level)
                        handler.setFormatter(formatter)
                        handlers.append(handler)

                    processor_logger.setLevel(log_level)
                    for h in handlers:
                        processor_logger.addHandler(h)

    @staticmethod
    def get_logger(logger_name: str = None):
        """
        Return the configured logger as described by the logger name. The caller should call this using
        "yellowsub." + self.__class__.__name__ + "." + self.id.
        If a logger is not defined for the processor (identified by class and id) the root "yellowsub" logger will
        be returned
        @param logger_name: The name of the logger requested
        @type logger_name: str
        @return: An instance of the logger that was requested
        @rtype: logging.Logger
        """
        normalized_logger_name = logger_name.lower()
        process_logger = logging.getLogger("yellowsub." + normalized_logger_name)
        root_logger = logging.getLogger("yellowsub")

        # DG_Comment: if no class name is provided return the root logger
        if logger_name is None:
            if len(root_logger.handlers) != 0:
                return logging.getLogger()
        if len(process_logger.handlers) != 0:
            return process_logger
        elif len(root_logger.handlers) != 0:
            return root_logger
        else:
            raise RuntimeError("Root logger not initialized and no specific logger is configured for the {}"
                               "processor".format(logger_name))
