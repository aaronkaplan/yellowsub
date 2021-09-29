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


### Some preliminary thoughts on simplicity

This code follows a couple of principles which **MUST** be followed, in order to remain simple:

  * we *strictly* follow the **KISS** principle: keep it simple and stupid.
    * we **RE-USE** existing systems (RabbitMQ, SQS, etc.). NO NOT INVENT YOUR OWN.
    * the only reason for code is to interface-bridge these existing systems.
    * re-using existing systems should go via configuration settings.
    * if that's not possible, make **very simple** interface / glue code.
    * highly readable code is a MUST.
    * this means: less code is a MUST. Here are some rules of thumbs to check for simplicity:
      1. This interface code should not use more than 150 lines of code.
      2. It MUST have python docstyle explanations.
      3. It MUST be explainable to a newcomer but average python coder in 15 mins. max.
      4. As a test, this newcomer python coder should be able to adapt something in the code in half a day.

  * Remember: re-using existing systems and simply interfacing them wins.a

  Code tends to become too complex over time. Then it's time to re-factor and simplify. Don't shy away from
  not implementing things which no-one needs anyway. Observe carefully which functions are actually used in a system.a

### The Message Queue

The MQ is a [pubsub](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) system. Our code (see [mq.py](lib/mq.py))
uses [RabbitMQ](https://en.wikipedia.org/wiki/RabbitMQ) internally, but abstracts it away. We can easily replace it by ActiveMQ, Kafka, Redis, etc... basically any MQ.a

How to use the MQ interface?

First instantiate the Producer class:
```python
p = Producer(id="myProducerID", exchange="the-name-of-my-exchange")
p.produce({ "msg": "some values"})      # a python dict gets sent
```

Then instantiate the consumer:

```python
c = Consumer(id="myConsumerID", exchange="the-name-of-my-exchange")
c.consume()     # the callback function will get called. You can override this CB function by
        # inheriting Consumer and overriding the process() method. See the next example.
```





