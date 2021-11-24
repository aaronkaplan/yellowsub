# Orchestrator

It MUST offer its services as RESTful API.


## Purpose

The Orchestrator's purpose is to read the relevant config YAML file(s) and to:

### I. Facilitate the Workflows' startup: 

 1. instantiate (read: create a python process) each [Processor](/docs/Glossary#Processor).
 2. Connect the newly instantiated Processor to their incoming message queue and outgoing exchanges.
 3. Register the Processor's PID in a `/var/run/yellowsub/<processor_id>.pid` file

### II. Help in stopping all or individual processors

Given a processor ID, it shall be possible to stop it and/or stop all processors.
Given  a processor class, it shall be possible to stop all instances (IDs) of this processor class.

### III. Querying liveliness of Processors

Every processor shall report its status to some monitoring instance. The orchestrator must be able to connect to this monitoring 
system and report back the liveliness status of each processor.

**Note**: this is different from monitoring the queue levels and performance levels of the MQ system.


### IV. Re-configure and re-load Processors
  
If a processor's config file changes, the orchestrator MUST be able to reload a processor and make it read its new config
file.

## Example


REST API endpoint for the orchestrator: ``https://.../orchestrator/api/v1/``


* ``HTTP GET .../orchestrator/api/v1/workflow/start`` ... start it all
* ``HTTP GET .../orchestrator/api/v1/workflow/stop``  ... stop  it all

* ``HTTP GET .../orchestrator/api/v1/processor/start/<ID>`` ... start a specific processor 
* ``HTTP GET .../orchestrator/api/v1/processor/stop/<ID>`` ...  stop a specific processor 
* ``HTTP GET .../orchestrator/api/v1/processor/reload/<ID>`` ... reload a specific processor

* ``HTTP GET .../orchestrator/api/v1/processor/status/<ID>`` ... get the liveliness status of a specific processor 


