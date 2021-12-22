# Orchestrator

It MUST offer its services as RESTful API.

## Purpose

The Orchestrator's purpose is to read the relevant config YAML file(s) and to:

### I. Facilitate the Workflows' startup: 

1. instantiate (read: create a python process) each [Processor](/docs/Glossary#Processor)
2. Connect the newly instantiated Processor to their incoming message queue and outgoing exchanges.
3. Call the processor's `start()` method
4. Register the Processor's PID in a `/var/run/yellowsub/<processor_name>.pid` file

#### who creates which exchanges and queues?
Since it is important to know who is responsible for initially creating exchanges and binding queues to that, we came up with the following
schema:

``` 
                                                                                               /---> queue2 (downstream)
    Processor_A -> upstream exchange ----> queue1 --> Processor_B --> to_exchange (downstream) - --> queue 3 (downstream)
                                                                                               \ --> queue 4 (downstream)
```

Case 1: Enricher - we have an upstream and downstream queue and exchanges.

This is the case above. All cases covered by the rules below.
   
Case 2: Collector - no upstream queues

Here there is no upstream queue configured. Rule 1 does not apply. Rules 2-3 apply, all good.

Case 3: OutputProcessor - no downstream queues.

Here there is no downstream exchange nor queue configured. Rule 1 does apply. Rules 2-4 don't apply.  If 
at a later stage an upstream processor (in this example, processor_A) will be created/start, then it is 
his responsibility to bind the upstream queue to his exchange.

A processor is responsible to:
1. create the upstream queues, if upstream queues are defined and not created
2. create the downstream queues, if downstream queues are defined and not created (the downstream queue name comes from the workflow.yml file)
3. create the downstream exchange, if downstream queues are defined
4. connect/bind downstream exchange to all downstream queues



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


