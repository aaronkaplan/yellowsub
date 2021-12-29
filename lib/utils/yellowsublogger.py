import logging
import logging.handlers
import inspect


class YellowsubLogger:
    """Class that offers utility functions around project organisation"""

    def __init__(self):
        pass

    @staticmethod
    def delete_loggers():
        logger_names = [name for name in logging.root.manager.loggerDict.keys() if name.startswith("yellowsub")]
        for name in logger_names:
            del logging.root.manager.loggerDict[name]

    @staticmethod
    def setup_handler(handler_config: dict = None) -> logging.Handler:
        if handler_config is None:
            raise RuntimeError("No handler config has been passed nothing to do")
        if handler_config["type"] != "TimedRotatingFileHandler":
            raise NotImplementedError("the only supported logging handler is TimedRotatingFileHandler")

        h_type = handler_config["type"]
        h_output = handler_config["output"]
        h_log_level = handler_config["loglevel"]  # FIXME: if a handler_config dict is passed but no level, ... boom!
        handler = getattr(logging.handlers, h_type)(h_output, when = "midnight", interval = 1,
                                                    backupCount = 30)
        handler.setLevel(h_log_level)

        formatter = logging.Formatter('%(asctime)s|%(created)s|logger_name:%(name)s|process_pid:%(process)d|'
                                      'file:%(filename)s|line_no:%(lineno)d|%(levelname)s: %(message)s')
        handler.setFormatter(formatter)

        return handler

    @staticmethod
    def setup_loggers(config: dict = None):
        """
        Setup the loggers as per the passed on configuration of the project.
        This method will reinitialize the entire logging architecture after a call to this method the entire logging
        architecture will reflect the configuration passed in as parameters.
        The config param should have the structure described below.
        The name of the processors must match case_insensitive with the class name in which they are implemented as
        per the project convention

        @param config: Dictionary containing the parsed config.yml
        @type config: dict
        @return: None
        @rtype: None

        config example a concatenation of all the configs in the project both global and specific
        config =
        {global_config:{global config}
         procesor_configs:[{processor specific config}]
        }

        {'global_config': {'general': {'mq': 'rabbitmq'},
                   'http': {'http_proxy': 'http://my.example.com:8080/',
                            'https_proxy': 'https://my.example.com:8080/',
                            'verify_ssl': False},
                   'logging': {'facility': 'yellowsub',
                               'handlers': [{'handler': {'loglevel': 'DEBUG',
                                                         'output': '/var/log/yellowsub.DEBUG.log',
                                                         'type': 'TimedRotatingFileHandler'}},
                                            {'handler': {'loglevel': 'INFO',
                                                         'output': '/var/log/yellowsub.INFO.log',
                                                         'type': 'TimedRotatingFileHandler'}},
                                            {'handler': {'loglevel': 'WARN',
                                                         'output': '/var/log/yellowsub.WARN.log',
                                                         'type': 'TimedRotatingFileHandler'}}],
                               'loglevel': 'DEBUG'},
                   'rabbitmq': {'host': 'localhost', 'port': 5672},
                   'redis': {'cache_ttl': 86400,
                             'db': 2,
                             'host': 'localhost',
                             'port': 6379}},
         'processor_configs': [{'description': 'The MISPattributesearcher enricher '
                                               'will search for events in MISP for a '
                                               'given IoC (IP address, etc..)',
                                'enabled': True,
                                'group': 'enricher',
                                'groupname': 'enricher',
                                'logging': {'handlers': [{'handler':
                                                            {'loglevel': 'INFO',
                                                            'output': '/tmp/yellowsub.mispattributesearcher.INFO.log',
                                                            'type': 'TimedRotatingFileHandler'}},
                                                         {'handler':
                                                            {'loglevel': 'WARN',
                                                            'output': '/tmp/yellowsub.mispattributesearcher.WARN.log',
                                                            'type': 'TimedRotatingFileHandler'}}],
                                            'loglevel': 'DEBUG'},
                                'module': 'processors.enrichers.mispattributesearcher',
                                'name': 'mispattributesearcher',
                                'parameters': {'misp_api_key': '',
                                               'misp_uri': 'https://192.168.5.108/'},
                                'run_mode': 'continuous'}]}
        """

        if type(config) != dict:
            raise TypeError("config parameter should be of type dict")
        elif len(config.keys()) == 0:
            raise RuntimeError("The config dictionary supplied for configuring loggers is empty")

        # Delete all configured loggers
        YellowsubLogger.delete_loggers()

        # Parse the config and setup loggers
        # Define root logger
        root_logger = logging.getLogger("yellowsub")

        # if there already is a root_logger handler it means that something is wrong with the setup as it should have
        # been deleted
        if len(root_logger.handlers) != 0:
            raise RuntimeError("the global logger is already defined something is wrong with the YellowsubLogger "
                               "class as it should have been deleted by this point in time")

        logger_config = config["global_config"]["logging"]
        log_level = logger_config["loglevel"]
        handlers = []
        for h in logger_config["handlers"]:
            handler = YellowsubLogger.setup_handler(h["handler"])
            handlers.append(handler)

        root_logger.setLevel(log_level)
        root_logger.propagate = False
        for h in handlers:
            root_logger.addHandler(h)

        # Define all other handlers as per the config if any
        if "processor_configs" not in config.keys():
            return

        for processor_config in config["processor_configs"]:
            processor_logger = logging.getLogger("yellowsub." + processor_config["name"])
            logger_config = processor_config["logging"]
            log_level = logger_config["loglevel"]
            handlers = []
            for h in logger_config["handlers"]:
                handler = YellowsubLogger.setup_handler(h["handler"])
                handlers.append(handler)

            processor_logger.setLevel(log_level)
            for h in handlers:
                processor_logger.addHandler(h)

    @staticmethod
    def get_logger() -> logging.Logger:
        """
        Return the configured logger as described by the logger name. The caller should call this using
        "yellowsub." + self.__class__.__name__ + "." + self.processor_name.
        If a logger is not defined for the processor (identified by class and processor_name) the root "yellowsub" logger will
        be returned
        @return: An instance of the logger that was requested
        @rtype: logging.Logger
        """
        root_logger = logging.getLogger("yellowsub")

        # FIXME: this check broke everything (aaron)
        # DG_Comment: if the root logger is not setup it means we are trying to get loggers before setting them up
        # so we fail
        if len(root_logger.handlers) == 0:
            raise RuntimeError("Root logger not initialized most likely this execution path did not initialize loggers"
                               "using YellowsubLogger.setup_loggers()")

        stack = inspect.stack()
        caller_class_name = stack[1][0].f_locals["self"].__class__.__name__
        # this can be used at a later time if needed
        # caller_method = stack[1][0].f_code.co_name
        specific_logger = logging.getLogger("yellowsub." + caller_class_name.lower())

        if len(specific_logger.handlers) != 0:
            return specific_logger
        else:
            return root_logger
