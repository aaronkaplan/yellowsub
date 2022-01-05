[![unittests](https://github.com/aaronkaplan/yellowsub/actions/workflows/unittests.yml/badge.svg)](https://github.com/aaronkaplan/yellowsub/actions/workflows/unittests.yml)
[![codecov](https://codecov.io/gh/aaronkaplan/yellowsub/branch/main/graph/badge.svg?token=FCBLQ8FNP0)](https://codecov.io/gh/aaronkaplan/yellowsub)
[![pipeline status](https://git.s.cec.eu.int/automation/yellowsub/badges/main/pipeline.svg)](https://git.s.cec.eu.int/automation/yellowsub/-/commits/main)
[![coverage report](https://git.s.cec.eu.int/automation/yellowsub/badges/main/coverage.svg)](https://git.s.cec.eu.int/automation/yellowsub/-/commits/main)

# Proof of concept for a message queue based automation framework

Author: aaron kaplan <aaron@lo-res.org>, <Leon-Aaron.Kaplan@ext.ec.europa.eu>

## What?

![yellowsub icon](docs/Submarine-icon.png)

Yellowsub is a Threat Intelligence Platform for automation. It can automate incidence response and 
Cyber Threat Intelligence (CTI) tasks.

It's current status is 'proof of concept'.
It was developed to automate the tasks of our Cyber Threat Hunting team.

It strictly follows the **KISS principle** (_Keep it Simple and Stupid_). It's an intentionally
minimalistic system which emphasizes *re-use* of best-of-breed concepts and software frameworks such as
TheHive, Cortex, RESTful APIs, SOAR integrations, etc. It tries to *invent as little as possible*, while still being
able to automate all the needs of Cyber Threat Hunting.

You can imagine it as a meta-[SOAR](https://en.wikipedia.org/wiki/Computer_security_incident_management#Initial_incident_management_process)

It follows the "Harmonized Automation Architecture" document.

As an underlying principle it uses the internal [common data format](docs/Datamodel.md) (which is extensible).

It consists of / uses:

- RabbitMQ (but the MQ system is replaceable, if needed)
- A very simple code base and object oriented [class hierarchy](docs/OO-Architecture.md) which helps you add integrations
- A simple "orchestrator" script to create the rabbitMQ message queues
- YAML config files
- Integrations with [TheHive's Cortex's Analyzers](https://github.com/TheHive-Project/Cortex-Analyzers) to achieve many more
integrations.

It supports massive parallelism.

## Quick start

Getting it installed:
```bash
git clone ...<this repo>
apt install virtualenv
virtualenv --python=python3.9 venv
source venv/bin/activate
pip install -r requirements.txt
export YELLOWSUB_ROOT_DIR=`pwd`            # set ROOTDIR to the place where everything is installed
# get rabbitMQ and redis installed via docker and listening on localhost. See docs/Getting-Started.md
...
# use setup.py to install a locally editable version of all commands:
pip install -e .
# start an example workflow
workflows start 
```

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
