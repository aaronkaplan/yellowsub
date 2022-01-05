# Configuration files

## The global config   

This resides in `$YELLOWSUB_CONFIG_DIR/config.yml` - by default, the ENV variable `YELLOWSUB_CONFIG_DIR` points to `etc/`.

The global config consists of multiple YAML sections:

Syntax: 
```yaml
general:
  mq: rabbitmq

rabbitmq:
  host: localhost
  port: 5672
  user: guest 
  password: guest

redis:
  cache_ttl: 86400              # 1 day
  host: localhost
  port: 6379
  db: 2


logging:
  loglevel: 'DEBUG'             # optional, the actual loglevel will be set on the individual handlers, default=DEBUG
  facility: 'yellowsub'         # optional
  handlers:
    - handler:
        type: 'TimedRotatingFileHandler'
        output: 'var/log/yellowsub.INFO.log'
        loglevel: 'INFO'
    - handler:
        type: 'TimedRotatingFileHandler'
        output: 'var/log/yellowsub.WARN.log'
        loglevel: 'WARN'           # optional

http:
  http_proxy: "http://my.example.com:8080/"
  https_proxy: "https://my.example.com:8080/"
  verify_ssl: False
```

## Per processor specific config

This resides in `etc/processors/_name_.yml`, where *name* will be the *unique* processor name for a specific processor.

Example:

This is an example specific config file for name = "mispattributesearcher". 
It is called `etc/processors/mispattributesearcher.yml`

```yaml
# Minimum required config for a processor:
name: myMispattributesearcher1 
description: The MISPattributesearcher enricher will search for events in MISP for a given IoC (IP address, etc..)
enabled: true         # enable it or not
group: enricher       # ignored for now
groupname: enricher   # this field is ignored for now
module: processors.enrichers.mispattributesearcher    # where the python module resides
run_mode: continuous   # ignored for now. "continuous is the default"
input_datamodel: "..."      # the name of the input datamodel. See [Datamodels.md](Datamodels.md)
output_datamodel: "..."     # Detto...

# Needed specific parameters for this processor: API keys, etc...
parameters: 
  misp_uri: "https://192.168.5.108/"                                            
  misp_api_key: "123456789"                                                              
```

Explanation of the fields:

|Field   | Explanation | 
|:------ | ------------ | 
| name  | the processor name (also present in the filename) |
| description | a human readable description of what this processor should do |
| enabled | should this processor run ? |
| group | possible values: enricher, collector, parser, filter, outputProcessor |
| groupname | currently not used |
| module | the python module path where the code for this processor resides |
| run_mode | either "continuous" or "scheduled" (the latter would be for running it from cron(1)) |
| parameters | a yaml dict of arbitrary parameters specific to this processor. |


### Overriding global parameters

In case a specific processor ID config should use different settings than in the global config,
it may do so, by simply repeating (and changing) the relevant structure inside the `parameters` section.

Example:

```yaml
# Minimum required config for a processor:
name: mispattributesearcher
description: "The MISPattributesearcher enricher will search for events in MISP for a given IoC (IP address, etc..)"
enabled: true                  # enable it or not
group: enricher                # ignored for now
groupname: enricher            # this field is ignored for now
module: processors.enrichers.mispattributesearcher              # where the python module resides
run_mode: continuous           # ignored for now. "continuous is the default"
input_datamodel: "..."         # the name of the input datamodel. See [Datamodels.md](Datamodels.md)
output_datamodel: "..."        # Detto...

# Needed specific parameters for this processor: API keys, etc...
parameters: 
  misp_uri: "https://192.168.5.108/"                                            
  misp_api_key: "123456789"     

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

Note that in this example, the mispattributesearcher processor's log files
will be sent to different files than by default. This is due to the fact that (see [abstractProcessor.py](abstractProcessor.py)) 
the specific config will be copied over (on top of) the global config within a processor unix process context:

``python
            self.config = deep_update(self.config, self.specific_config)
``


# Workflow config file

This resides in `$YELLOWSUB_CONFIG_DIR/workflows.yml`.
A workflow is a Direct Acyclic Graph (DAG) between processors. Each processor will 
receive incoming data via its input_queue and send to its output_exchanges (a list).

The workflows.yml file MAY contain multiple workflows (DAGs) which may even be dis-joint.
A workflow has a `workflow_id`, description and some metadata.

Special cases:
* a collector does not have to specify a `from` 
* an outputProcessor does not have to specify a `to`
* all the other ones (enrichers, filters, parser) must have both a `from` and `to`.

Syntax:

```yaml
workflow1:
  description: "my workflow 1"
  author: "kaplale"
  flow:
  # simple linear example: get urls from somewhere (configured in the url_collector.yml) and do parallel lookups in safebrowsing, finally write the enriched results to a file.
  - { processor: "url_collector", to: ["ex1", "ex2"] }    # ex2 does nothing with it
  - { processor: "urllist_parser", from: "ex1", to: ["ex3"]}
  - { processor: "is_url_on_safebrowsing", from: "ex3", to: ["ex4"], paralellism: 3 }
  - { processor: "output_file_writer", from: "ex4"}
```

Multiple workflows may be defined in this way:

```yaml

workflow1:
  description: "my workflow 1"
  author: "kaplale"
  flow:
    ...
  
workflow2:
  description: "my workflow 2"
  author: "kaplale"
  flow:
    ... 
```

# Datamodel config file

XXX coming ... FIXME XXXX temporary file resides in `etc/datamodels.yml`

# Conditions which must be met

1. a processor `name` appearing in workflows.yml MUST appear and have a config file
   in `$YELLOWSUB_CONF_DIR/processors/_name_.yml`.
2. data models must be compatible / mappable in a flow.

