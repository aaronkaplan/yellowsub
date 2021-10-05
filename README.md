[![unittests](https://github.com/aaronkaplan/yellowsub/actions/workflows/unittests.yml/badge.svg)](https://github.com/aaronkaplan/yellowsub/actions/workflows/unittests.yml)
[![codecov](https://codecov.io/gh/aaronkaplan/yellowsub/branch/main/graph/badge.svg?token=FCBLQ8FNP0)](https://codecov.io/gh/aaronkaplan/yellowsub)

# Proof of concept for a message queue based automation framework

Author: aaron kaplan <aaron@lo-res.org>, <Leon-Aaron.Kaplan@ext.ec.europa.eu>

## Quick start

Getting it installed:
```bash
git clone ...<this repo>
apt install virtualenv
virtualenv --python=python3.8 venv
source venv/bin/activate
pip install -r requirements.txt
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

Please also see the [code philosophy](docs/ZEN.md) page to understand some design principles behind this system.

### A hello world example

[processor.py](lib/processor/processor.py) contains the code for instantiating processors. Processors are small units of
code, which do *one thing* (and focus on doing it will). Example: enrich a SHA256 hash with the results of Virustotal.

Each processor gets data in the [common data format]() on its input queue. It gets called (callback function!) via its
process() function which will receive amongst other things the message. It then does something with the message (for example add
VT infos to it in our example) and passes it on to the next message queue on the output side.

Example:

```python
class MyProcessor(Processor):

    def process(self, channel = None, method = None, properties = None, msg: dict = {}):

        self.msg = json.loads(msg)  # convert the binary representation to a python dict
        # validate the message here if needed

        logging.info("MyProcessor (ID: %s). Got msg %r" % (self.id, self.msg))
        # do something with the msg in the process() function, the msg is in self.msg
        # ...
        # then send it onwards to the outgoing exchange
        self.producer.produce(msg=self.msg, routing_key="")
```

All you will need to do, is to

1. ``import lib.processor.processor``
2. inherit from the Processor class:
``class MyProcessor(Processor):``
3. Implement a ``process()`` callback function as shown above.

That's it!

### Connecting everything

RabbitMQ builds upon the concepts of exchanges and queues. Both have names (unique strings).
A producer will always send to an exchange (by specifying the exchange's name). The exchange then usually fans-out the
messages (i.e. duplicate them) to all connected queues.

![RabbitMQ example with exchanges](https://www.rabbitmq.com/img/tutorials/python-three-overall.png)

In this picture (taken from the [RabbitMQ tutorial](https://www.rabbitmq.com/tutorials/tutorial-three-python.html)),
producer "P" sends to exchange "X" which duplicates (fans-out) the messages to the queues "amq.gen-*". Consumers "C1"
as well as "C2" get the messages in parallel.

So how do we create these exchanges and queues and tell the producers and consumers where to connect to?

Simple! We tell the processor class via its __init__() function:

```python

```


Next step:




