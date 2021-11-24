# Architecture Vision

This document shall give a high level architecture of the yellowsub framework.
It can also serve as a check list against which to plan sprints / epics.
It tries to answer the question "what shall yellowsub be capable of doing?"

yellowsub is a *meta-SOAR* framework:

* it shall _easily_ allow to integrate with SOAR systems
* it shall talk with multiple automation frameworks (TheHive/Cortex, intelmq, AIL, OpenCTI)
* it shall support multiple datamodels (STIX 2.1, intelMQ DHO, AIL exchange format)
* it was originally developed for threat hunting automation needs and has a strong focus on CTI

# OO-Architecture

The object oriented architecture is described in [this document](OO-Architecture.md).
The OO-architecture is inspired by [Abusehelper](https://en.wikipedia.org/wiki/AbuseHelper), [n6](https://github.com/CERT-Polska/n6) and [IntelMQ](https://github.com/certtools/intelmq).
The following sub-sections describe the OO-architecture.

## Processors

Processors all inherit from the ``AbstractProcessor`` class.
The AbstractProcessor class defines the following interface:

### Processor ID
* each Processor MUST have an ID (unique string). The ID of a processor serves as the instance ID of a particularly configured processor.
* The ID also serves as the key for finding a _specific_ configuration for the processor in ``etc/processors/<id>.yml``.
* Therefore, one ID == one particularly configured processor. 
* NOTE well: multiple unix processes may have the same processor ID (and hence the same config), but they will have different PIDs.
* the ID MUST be given to the constructor:

Example:

```python
class MyProcessor(Enricher):
    
    def process(self, channel=None, method=None, properties=None, msg: dict = {}):
        ...
        pass

myproc = MyProcessor(id="the-quick-brown-fox")
myproc.start()
```
### 

## Configuration

## Logger

The logger is responsible for logging each processor potentially to a separate log handler and/or log destination.

## Orchestrator

A set of scripts which can start/stop/restart whole workflows and individual processors.
Resides in ``bin/``.


# Integrations with other systems

Integrations are usually done via Collectors (for input) or OutputProcessors (for sending to some other system/SOAR).


# Testing and Unit Tests

``tests/`` contains the unit tests (runnable via nosetests or pytest). See [TESTING.md](TESTING.md) for details.

# CI/CD

We support both gitlab runners via the $ROOTDIR/.gitlab.yml as well as github workflows (.github/workfows/*.yml).
Note that unit tests MUST be run in CI/CD runs.

 
