# Developer Guide

## Where is what?  Code repository overview

``core/`` contains the core components of the framework:
  * ``core/mq/*`` the minimalistic message queue (mq) abstraction layer. Used py processor
  * ``core/processor/*`` the definition of processors, enrichers, filters, parser, etc.. All of these classes here are abstract classes and will be instantiated by the actual processors
  * ``core/utils/*`` all utilities libraries such as redis cache, config parser, password santization for printing passwords/API keys in logs etc.
  * ``processors/*`` concrete implementations of collectors, parsers, enrichers, filters, outputProcessors. See the corresponding subdirs.
  * ``docs/`` documentation
  * ``tests/`` unit tests
  * ``etc/*`` the config sample directory
  



## How do I write my own processor?




