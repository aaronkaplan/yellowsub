# Developer Guide


## Where is what?  Code repository overview

``lib/`` contains the core components of the framework:
  * ``lib/mq/*`` the minimalistic message queue (mq) abstraction layer. Used by the Processor classes.
  * ``lib/processor/*`` the definition of processors, enrichers, filters, parser, etc.. classes. All of these classes
  here are abstract classes and will be instantiated by the actual processors. See ``processors/*`` for the concrete
  implementations.
  * ``lib/utils/*`` all utilities libraries such as redis cache, password sanitization for printing passwords/API keys in logs etc.

Processors:
  * ``processors/*`` _concrete_ implementations of collectors, parsers, enrichers, filters, outputProcessors. See the
  corresponding subdirs.
  * ``bin/``  orchestrator: starting and stopping processors and workflows
  * ``docs/`` documentation
  * ``tests/`` unit tests
  * ``etc/*`` the config sample directory


## Setting up your developing environment

### git pre-commit hook
The git client hooks are stored inside /yellowsub/contrib/hooks.

You need to make sure these are executable in your local repo.

Example:
```chmod +x contrib/hooks/pre-commit```

In addition you need to create symlinks for them inside your local yellowsub/.git/hooks/ folder. By convention the files
under yellowsub/.git/hooks have to have no extension and be executable in order to be run. **Make sure your 
symlink is properly set up**

Example:
```ln -s ./contrib/hooks/pre-commit ./.git/hooks/pre-commit```



## How do I write my own processor?

Get started with the examples in ``processors/*``. Depending on what you need (Collector, Parser, Enricher, Filter, Output),
you might want to get inspired by one of these processors.


### A simple hello world enricher example

[processor.py](lib/processor/processor.py) contains the code for instantiating processors. Processors are small units of
code, which do *one thing* (and focus on doing it will). Example: enrich a SHA256 hash with the results of Virustotal.

Each processor gets data in the [common data format]() on its input queue. It gets called (callback function!) via its
process() function which will receive amongst other things the message. It then does something with the message (for example add
VT infos to it in our example) and passes it on to the next message queue on the output side.

Enrichers are specific Processors (subclasses of the Processor class, see the [OO-Architecture](OO-Architecture.md)),
which are side-effect free (think: "lambda functions" from functional programming). They will take some value from the
message, do a lookup in some external dataset or do some scoring on it and then *add* a new key-value pair to the message
(or modify an existing key-value pair) and finally, pass on the new message with the key-values to the next exchange.

Your own enricher is quite easy to write: you create a class which inherits from the ``Enricher`` class.
Then you overwrite the ``process()`` method.
*Optionally*, you might want override the ``__init()__`` method (for example if you need to load a dataset or so).

Example:

```python
class MyGetHostByName(Enricher):
    dns_recursor = "8.8.8.8"        # some default attributes. These may be overwritten by the Processor's config file

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


# Style

We will adhere to PEP8.

## String formatting

Please use the f-string syntax: print(f"foo {}".format("xyz"))

## Docstrings

We use Epytext docstring formats. Please make sure that 

* every class has a docstring 
* every method
* every function has docstring
* every module MUST have a docstring







