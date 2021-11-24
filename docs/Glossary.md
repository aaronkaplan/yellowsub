# Glossary

| Term                             | Meaning                                        | Example | Documentation |
|----------------------------------| ---------------------------------------------- | ------- | ------------- | 
| Processor                        | a unit of code which shall pull data in on its left side, process (parse, enrich, filter, etc) it and send to _n_ different output message queues | an enricher adding an ip address for an incoming hostname | [OO-Architecture.md](OO-Architecture.md)
| AbstractProcessor                | An abstract base class for the processor class | n/a |[OO-Architecture.md](OO-Architecture.md)
| Enricher                         | A special (in OO-oriented lingo: a subclass) Processor, which shall expect a certain data field of a specific type coming in the message (which MUST be in the *internal data format*), do some lookup or modification to that data and which shall produce a new key-value pair (or modify the existing one) and add it to the message and pass it on to the next output queues. | IP to country lookup |
| Parser / Mapper                  | The terms "parser" and "mapper" may be used interchangeably. Such a Processor shall convert the external data format (as sent by the collector) to the internal data format and pass it on to the output queues | stix to internal data format | 
| Filter                           | Similar to an enricher, however, it may output nothing, if the filter condition (set as run time parameter) is not met. | a filter which filters out any message which does not match our IP ranges | 
| OutputProcessor                  | A processor which shall send (and convert to the respective output format) the message to some output system, possibly triggering an action | the pipeline filtered out alerts on IPs which need immediate action: these shall be sent to the proxy blocklist | 
| Workflow                         | a network, more specifically a [directed acyclic graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph) of Processors (which are the nodes) and message queues inbetween (which are the edges). | collector from IMAP -> Parser -> Filter out non-relevant alerts -> enrich -> send to Jira |
| Message                          | payload (in JSON format) plus standardized header. Note that messages may contain more complex objects such as STIX data |  See XXX |
| Message Queue                    | A FIFO | See [AMQP](https://www.rabbitmq.com/tutorials/amqp-concepts.html) for an intro. | 
| Exchange                         | A router for messages to selected message queues | See [AMQP](https://www.rabbitmq.com/tutorials/amqp-concepts.html) for an intro. | 
| Config                           | A processor has its own config (for example for API keys) and the Workflow is also specified in a config. | See ``etc/*`` | | [Config.md](Config.md)
| Datamodel                        | a.k.a "Data format" - a definiton of the payload of a message | STIX-2.1 | 
