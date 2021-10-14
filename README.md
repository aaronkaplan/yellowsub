[![unittests](https://github.com/aaronkaplan/yellowsub/actions/workflows/unittests.yml/badge.svg)](https://github.com/aaronkaplan/yellowsub/actions/workflows/unittests.yml)
[![codecov](https://codecov.io/gh/aaronkaplan/yellowsub/branch/main/graph/badge.svg?token=FCBLQ8FNP0)](https://codecov.io/gh/aaronkaplan/yellowsub)

# Proof of concept for a message queue based automation framework

Author: aaron kaplan <aaron@lo-res.org>, <Leon-Aaron.Kaplan@ext.ec.europa.eu>

## What?

![yellowsub icon](docs/Submarine-icon.png | width=200)

Yellowsub is a proof of concept message queue based automation framework.
It was developed to automate the tasks of our Cyber Threat Hunting team.

It strictly follows the **KISS principle** (Keep it Simple and Stupid). It's an intentionally
minimalistic system which emphasizes *re-use* of best-of-breed concepts and software frameworks such as
TheHive, Cortex, RESTful APIs, SOAR integrations, etc.
You can imagine it as a meta-[SOAR](https://en.wikipedia.org/wiki/Computer_security_incident_management#Initial_incident_management_process)

It follows the "Harmonized Automation Architecture" document.


It uses:

- RabbitMQ (but the MQ system is replaceable, if needed)
- A very simple code base and object oriented [class hierarchy](docs/OO-Architecture.md) which helps you add integrations
- A simple "orchestrator" script to create the rabbitMQ message queues
- YAML config files
- Integrations with [TheHive's Cortex's Analyzers](https://github.com/TheHive-Project/Cortex-Analyzers) to achieve many more
integrations.



## Quick start

Getting it installed:
```bash
git clone ...<this repo>
apt install virtualenv
virtualenv --python=python3.8 venv
source venv/bin/activate
pip install -r requirements.txt

# get rabbitMQ and redis installed via docker and listening on localhost. See docs/Getting-Started.md
...
# start an example workflow
# python bin/orchestrate.py -c etc/example-workflow.yml
```

Make sure your config.yml is correct, look at it and adapt the settings for redis and rabbitmq

Start a producer:
```bash
python -m lib.mq --producer --exchange CTH --id producer1
```

In a different window (or multiple windows) start a (or multiple) consumers:
```bash
python -m lib.mq --consumer --exchange CTH --id queue1
```

**Note**: if you use multiple consumers and they all have the same ID, then they will all consume from the same message
queue. Which means, they will get the data from this queue in a round-robin fashion.exchange


## Overview

### Basic ideas

* Please also see the [code philosophy](docs/ZEN.md) page to understand some design principles behind this system.
* The [Nomenclature](docs/Nomenclature.md) page contains the used terminology.
* For an overview of the object-oriented class hierarchy, please see the [OO-Architecture](docs/OO-Architecture) page.
* The [Developer Guide](docs/Developer-Guide.md) will walk you through writing your first Processor/Enricher.

Next, it makes sense, to dive into the individual directories to understand, where you will find what in the code.Developer

### Where is what?  Code repository overview

``lib/`` contains the core components of the framework:
  * ``lib/mq/*`` the minimalistic message queue (mq) abstraction layer. Used by the Processor classes.
  * ``lib/processor/*`` the definition of processors, enrichers, filters, parser, etc.. classes. All of these classes
  here are abstract classes and will be instantiated by the actual processors. See ``processors/*`` for the concrete
  implementations.
  * ``lib/utils/*`` all utilities libraries such as redis cache, password sanitization for printing passwords/API keys in logs etc.
  * ``processors/*`` concrete implementations of collectors, parsers, enrichers, filters, outputProcessors. See the
  corresponding subdirs.
  * ``docs/`` documentation
  * ``tests/`` unit tests
  * ``etc/*`` the config sample directory


## More info

Please have a look at the [docs](docs/) folder.