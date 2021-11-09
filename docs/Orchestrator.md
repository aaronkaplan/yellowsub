# Orchestrator

## Purpose

The Orchestrator's purpose is to read the relevant config YAML file(s) and to:

* Facilitate the Workflows' startup: 

 1. instantiate (read: create a python process) each [Processor](/Nomenclature#Processor).
 2. Connect the newly instantiated Processor to their incoming message queue and outgoing exchanges.
 3. Register the Processor's PID in a `/var/run/yellowsub/<processor_id>.pid` file

* Help in stopping all or individual processors

* Querying liveliness of Processors

* Re-configure and re-load Processors
  

## Example

