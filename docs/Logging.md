The loggers in the project have the following structure:

```
- python root logger
    - yellowsub root logger
        - individual loggers per processor
```

The loggers follow a tiered architecture as can be seen above.

Each individual logger has one or more handlers that define:
* where a message is logged
* in what format the message is logged
* what messages get logged (which log level)

When considering the tiered hierarchy each log message gets passed from the children towards the root logger.

All the loggers used in yellowsub always pass on the information to their parent loggers. 
The exception is the project root logger (always named yellowsub) which does not forward anything to the python root logger. 
This is done in order for the logs to be contained


Eg:
```
python_root_logger = logging.getLogger() 
#returns the root logger

project_root_logger = logging.getLogger("yellowsub") 
#returns a logger named yellowsub (which we consider the project root_logger)
#which is a child of the root logger

project_specific_logger = logging.getLogger("yellowsub.mispattributesearcher") 
#returns the logger named mispattributesearcher
#which is a child of the yellowsub logger

python_root_logger.warning("Test")
#would log the message according to the handlers and configuration of the python root logger

project_root_logger.warning("Test")
#would log the message according to the handlers and configuration of the "yellowsub" root logger

project_specific_logger.warning("Test")
#would log the message according to the handlers and configuration 
#of the "yellowsub.mispatributesearcher" root logger however it will also send the same message
#to the project root logger "yellowsub" which will then evaluate its handlers and log if matched
```

For more information on how the logging system in python works check: https://docs.python.org/3/howto/logging.html

And more specifically: https://docs.python.org/3/howto/logging.html#logging-flow

In terms of logging from a processor/enricher/collector class the framework should handle logger setup for you. 
You must only specify the specific logging configuration and handlers you want inside you .etc/[processor_name].yml

Logging setup is handled in one of the classes the processor classes extends and can be used inside your implementation 
via self.logger.msg_level(msg)where msg_level is your desired level for logging the message

Sample config:
```buildoutcfg
# Minimum required config for a processor:
name: mispattributesearcher
description: "The MISPattributesearcher enricher will search for events in MISP for a given IoC (IP address, etc..)"
enabled: true         # enable it or not
group: enricher       # ignored for now
groupname: enricher   # this field is ignored for now
module: "processors.enrichers.mispattributesearcher"    # where the python module resides
run_mode: continuous   # ignored for now. "continuous is the default"

# Needed specific parameters for this processor: API keys, etc...
parameters:
  misp_uri: "https://192.168.5.108/"
  misp_api_key: ""

# Section to override global config (note that this needs to be at the top nesting level!):
logging: # override any of the settings of the global logger here if needed
  loglevel: 'DEBUG'
  handlers:
    - handler:
        type: 'TimedRotatingFileHandler'
        output: 'var/log/yellowsub.mispattributesearcher.INFO.log'
        loglevel: 'INFO'
    - handler:
        type: 'TimedRotatingFileHandler'
        output: 'var/log/yellowsub.mispattributesearcher.WARN.log'
        loglevel: 'WARN'
```

When you don't have the specific logging information specified inside your .etc/[processor_name].yml the "yellowsub" 
project root logger will be used for logging purposes

The entire logging infrastructure is exposed via the YellowsubLogger class defined inside lib/utils/yellowsublogger.py
The class exposes 2 static methods which can be used to allocate and gain access to the required loggers:

The YellowsubLogger.def setup_loggers(config: dict = None) method receives as parameter a dict containing the entire 
project config and sets up the required loggers as per the specification.

Example for structure dict expected for setup_loggers(config):
```buildoutcfg
{'global_config': {'general': {'mq': 'rabbitmq'},
                   'http': {'http_proxy': 'http://my.example.com:8080/',
                            'https_proxy': 'https://my.example.com:8080/',
                            'verify_ssl': False},
                   'logging': {'facility': 'yellowsub',
                               'handlers': [{'handler': {'loglevel': 'DEBUG',
                                                         'output': '/tmp/yellowsub.DEBUG.log',
                                                         'type': 'TimedRotatingFileHandler'}},
                                            {'handler': {'loglevel': 'INFO',
                                                         'output': '/tmp/yellowsub.INFO.log',
                                                         'type': 'TimedRotatingFileHandler'}},
                                            {'handler': {'loglevel': 'WARN',
                                                         'output': '/tmp/yellowsub.WARN.log',
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
                        'logging': {'handlers': [{'handler': {'loglevel': 'INFO',
                                                              'output': '/tmp/yellowsub.mispattributesearcher.INFO.log',
                                                              'type': 'TimedRotatingFileHandler'}},
                                                 {'handler': {'loglevel': 'WARN',
                                                              'output': '/tmp/yellowsub.mispattributesearcher.WARN.log',
                                                              'type': 'TimedRotatingFileHandler'}}],
                                    'loglevel': 'DEBUG'},
                        'module': 'processors.enrichers.mispattributesearcher',
                        'name': 'mispattributesearcher',
                        'parameters': {'misp_api_key': '',
                                       'misp_uri': 'https://192.168.5.108/'},
                        'run_mode': 'continuous'}]}
```

You can use the following excerpt for testing purposes in your code:
```buildoutcfg
config = json.loads('{"global_config": {"general": {"mq": "rabbitmq"}, "rabbitmq": {"host": "localhost", "port": 5672}, "redis": {"cache_ttl": 86400, "host": "localhost", "port": 6379, "db": 2}, "logging": {"loglevel": "DEBUG", "facility": "yellowsub", "handlers": [{"handler": {"type": "TimedRotatingFileHandler", "output": "/tmp/yellowsub.DEBUG.log", "loglevel": "DEBUG"}}, {"handler": {"type": "TimedRotatingFileHandler", "output": "/tmp/yellowsub.INFO.log", "loglevel": "INFO"}}, {"handler": {"type": "TimedRotatingFileHandler", "output": "/tmp/yellowsub.WARN.log", "loglevel": "WARN"}}]}, "http": {"http_proxy": "http://my.example.com:8080/", "https_proxy": "https://my.example.com:8080/", "verify_ssl": false}}, "processor_configs": [{"name": "mispattributesearcher", "description": "The MISPattributesearcher enricher will search for events in MISP for a given IoC (IP address, etc..)", "enabled": true, "group": "enricher", "groupname": "enricher", "module": "processors.enrichers.mispattributesearcher", "run_mode": "continuous", "parameters": {"misp_uri": "https://192.168.5.108/", "misp_api_key": ""}, "logging": {"loglevel": "DEBUG", "handlers": [{"handler": {"type": "TimedRotatingFileHandler", "output": "/tmp/yellowsub.mispattributesearcher.INFO.log", "loglevel": "INFO"}}, {"handler": {"type": "TimedRotatingFileHandler", "output": "/tmp/yellowsub.mispattributesearcher.WARN.log", "loglevel": "WARN"}}]}}]}'))
```

Calling the logger_setup function will erase all loggers and create new ones as per the configuration supplied.


The second static method YellowsubLogger.getlogger() can be called from anywhere in the code to get the logger required 
for the context you are calling it from.

If this method is called from within a processor class it will supply the logger yellowsub.processor_name if such a 
logger was defined or the yellowsub root logger if no specific one was defined.

Be mindful when you define the specific loggers as the name for the logger as can be found inside the yaml config, 
the name of the class for the processor as well as the processor_name has to match
  