# Architecture Vision

This document shall give a high level architecture of the yellowsub framework.
It can also serve as a check list against which to plan sprints / epics.
It tries to answer the question "what shall yellowsub be capable of doing?"

yellowsub is a *meta-SOAR* framework:

* it shall _easily_ allow to integrate with SOAR systems
* it shall talk with multiple automation frameworks (TheHive/Cortex, intelmq, AIL, OpenCTI)
* it shall support multiple datamodels (STIX 2.1, intelMQ DHO, AIL exchange format)
* it was originally developed for threat hunting automation needs and has a strong focus on CTI

**To emphasize: yellowsub is all about RE-USING existing standards, solutions, open source existing tools which are 
already used in the organization. Yellowsub bridges the gap with the fewest number of lines of code as possible.**.


# OO-Architecture

The object oriented architecture is described in [this document](OO-Architecture.md).
The OO-architecture is inspired by [Abusehelper](https://en.wikipedia.org/wiki/AbuseHelper), [n6](https://github.com/CERT-Polska/n6) and [IntelMQ](https://github.com/certtools/intelmq).
The following sub-sections describe the OO-architecture.

## Processors

Processors all inherit from the ``AbstractProcessor`` class.
The AbstractProcessor class defines the following interface:

### Processor ID
* each Processor MUST have an ID (unique string). The ID of a processor serves as the instance ID of a 
  particularly configured processor.
* The ID also serves as the key for finding a _specific_ configuration for the processor in 
  ``etc/processors/<id>.yml``.
* Therefore, one ID = one particularly configured processor. 
* NOTE well: multiple unix processes may have the same processor ID (and hence the same config), but they will 
  have different PIDs. To repeat: **one ID == one configuration** for a processor.
* the ID MUST be given to the constructor:

Example:

```python
class MyProcessor(Enricher):
    
    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        ...
        pass

myproc = MyProcessor(id="the-quick-brown-fox")         # <-- **Note the id= parameter here!**
myproc.start()
```

### Abstract Interface

Every processor MUST support the following interface, as defined in the AbstractProcessor class:

```python
class MyProcessor(AbstractProcessor):

    def __init__(self):
        # make sure we call the __init__ of the superclass:
        super().__init__()          # this will load the configuration (see below)
        # now initialize any local stuff such as connections to MISP, databases, etc.
        ...
        
    def start(self):
        """
        Start processing incoming messages. Calling start() makes the processor ready to accept incoming message,
        process them and send them top the output exchanges.
        This means, start() will connect the processor to its output exchanges and its input queue.

        The start function will then signal the orchestrator, that this processor is running.

        The difference to the __init__() function is that, __init__() shall deal with loading of the config,
        connecting to DBs, reading in supporting data sets, etc.
        Therefore, the assumption here is that the config for this processor is already loaded at this stage.

        """
        pass

    def reload(self):
        """
        Reload the config. Possibly also reconnect to different input queues and/or output exchanges.
        """
        pass

    def pause(self):
        """
        Pause processing of infos. Connections to incoming MQs and outgoing exchanges will remain open.
        """
        pass

    def stop(self):
        """
        Stop processing, disconnect from incoming MQs, outgoing exchanges. Tear down DB connections etc.
        """
        pass

    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        """
        Process a msg. msg is a python dict representing the message. See Datamodel.md
        
        YOU NEED TO OVERRIDE THIS. This is the main function that you need to implement in your subclass of processor.
        """
```

## Configuration

There are two types of configurations: global and per processor specific config.
The global config file resides in ``etc/config.yml`` and is in [YAML format](https://en.wikipedia.org/wiki/YAML).

The per processor specific config files reside in ``etc/processors/<id>.yml``, where  
_id_ is the processor ID (i.e. the unique identifier for a set of configs for a processor).
The specific per processor config MAY override the global config.

For details of the allowed contents of the config files, see [Config.md](Config.md)



### Configuration environment variables

The ENV variable `YELLOWSUB_CONFIG_DIR` = `/etc/yellowsub/` by default. **Note* the config path MUST be absolute.
You can override it in case you need to specify a test config.

The config directory structure is as follows (assuming  `YELLOWSUB_CONFIG_DIR` = `/etc/yellowsub`):

```
/etc/yellowsub
  config.yml               # the global config file: global settings
  workflow.yml             # definitons of the workflows
  datamodels.yml          # definition of the internal data format
  processors/             # the directory for the processor specific configs
    <id>.yml     # individual config files
```

If there is a specific config for a processor, then it should only be in the specific config subdirectory.

For the workflows, we have the `workflow.yml` config.
Datamodels (i.e. the internal data format) are defined in `datamodels.yml`
Every workflow file contains workflow definitions, which in turn need to reference the processor IDs.


## Logger

The logger is responsible for logging each processor potentially to a separate log handler and/or log destination.

Each processor may override the default logger config (given in `config.yml`) in its own specific config.
This way, developers and users can send the output of processors to a separate log file.

## Orchestrator

A set of scripts which can start/stop/restart whole workflows and individual processors.
Resides in ``bin/``.

The orchestrators duties are defined in [Orchestrator.md](Orchestrator.md)


# Integrations with other systems

Integrations are usually done via Collectors (for input) or OutputProcessors (for sending to some other system/SOAR).


# Testing and Unit Tests

``tests/`` contains the unit tests (runnable via nosetests or pytest). See [TESTING.md](TESTING.md) for details.

# CI/CD

We support both gitlab runners via the $ROOTDIR/.gitlab.yml as well as github workflows (.github/workfows/*.yml).
Note that unit tests MUST be run in CI/CD runs.

 
