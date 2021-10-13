# Developer Guide

## Where is what?  Code repository overview

``lib/`` contains the core components of the framework:
  * ``lib/mq/*`` the minimalistic message queue (mq) abstraction layer. Used py processor
  * ``lib/processor/*`` the definition of processors, enrichers, filters, parser, etc.. All of these classes here are abstract classes and will be instantiated by the actual processors
  * ``lib/utils/*`` all utilities libraries such as redis cache, password santization for printing passwords/API keys in logs etc.
  * ``processors/*`` concrete implementations of collectors, parsers, enrichers, filters, outputProcessors. See the corresponding subdirs.
  * ``docs/`` documentation
  * ``tests/`` unit tests
  * ``etc/*`` the config sample directory
  



## How do I write my own processor?




