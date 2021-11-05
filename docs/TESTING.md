# TEST HOWTO

## Unit tests

Every commit shall have an automatic unit test run.
The unit tests will run via gitlab's runners and/or github's actions.

### What is a unit test?

A unit test will test your code, more specifically it can test your python modules,
classes and functions in the modules.

It helps to first read the [pytest tutorial](https://docs.pytest.org/en/6.2.x/contents.html).

**Important**: DO NOT TEST network functionality in unit tests. [mock](https://changhsinlee.com/pytest-mock/) their input and output please.
The goal of these unit tests is to test your code and not to test another networked service if it is up and running and returning the right answers.
That's their problem not yours. Your problem is to check if (mocked) answers to these network services would be parseable by you.

### How are the unit tests run, what triggers them?

Every commit to the main branch triggers the exeution of the tests.

You can change the behaviour of the gitlab runner via the [.gitlab-ci.yml](/.gitlab-ci.yml)
file. Please be sure to read the [gitlab-ci.yml documentation](https://docs.gitlab.com/ee/ci/yaml/) before you change anything!

The following tests will be run in sequence:
1. syntax and code style checks via [flake8](https://flake8.pycqa.org/en/latest/). 
2. unit tests via [pytest](https://docs.pytest.org/en/6.2.x/). You are *highly encouraged* to *create your own unit tests* and test these unit tests before committing them.


### How to write unit tests

Basically, you want to test every function and every method of your classes.

#### Testing a class

Create a testclass. An example can be found in [tests/test_cache.py](/tests/test_cache.py). 
A testclass must start with the name prefix ``Test`` (example: ``TestCache``). 
All method names prefixed with ``test_`` will be called in turn by pytest.

#### Testing a module / testing functions

Simply create a test file ``test_myfile.py`` within ``tests/`` and prefix every 
function which should be called by pytest.


### How to check if your unit tests are working

You can check the success of the unit in two ways:

1. execute them locally first. See the ``.gitlab-ci.yml`` file and search for the ``pytest`` line. Execute that line and observe if there are any errors.
2. Commit code to the gitlab server and have the runner run the unit tests for you. You will get an email if things break. Also, please observe the [README.md](/README.md) file. It has banners which indicate if the unit tests were successful.

It pays off (i.e. it is much faster) to iterate over your unit tests locally before git committing them.
Why? Because the runner starts a docker image for every commit, configures it (apt install...), installs all
python dependencies (``pip install -r requirements.txt``), etc. That's slow.
Run it locally first. 
Ensure that they work and that they cover as much as possible before committing the unit tests.

## Test coverage
What's a good test coverage?

Ideally we should aim for a test coverage of > 75%. 
You can see the test coverage via:

```bash
 export ROOTDIR=$(pwd); pytest --cov=./ --cov-report=term  tests
```

Example output:

```
==================================================================== test session starts =====================================================================
platform linux -- Python 3.9.2, pytest-6.2.5, py-1.10.0, pluggy-1.0.0
rootdir: /home/aaron/git/yellowsub
plugins: cov-2.12.1
collected 5 items                                                                                                                                            

tests/test_cache.py ...                                                                                                                                [ 60%]
tests/test_config.py .                                                                                                                                 [ 80%]
tests/test_utils.py .                                                                                                                                  [100%]

----------- coverage: platform linux, python 3.9.2-final-0 -----------
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
lib/__init__.py                          0      0   100%
lib/config.py                           29      7    76%
lib/dataformat.py                       62     62     0%
lib/mq.py                              118    118     0%
lib/processor/__init__.py                0      0   100%
lib/processor/abstractProcessor.py      36     36     0%
lib/processor/collector.py               4      4     0%
lib/processor/enricher.py                4      4     0%
lib/processor/filter.py                  4      4     0%
lib/processor/output.py                  4      4     0%
lib/processor/parser.py                  4      4     0%
lib/processor/processor.py              32     32     0%
lib/utils/__init__.py                    4      0   100%
lib/utils/cache.py                      31      0   100%
lib/utils/projectutils.py               18      4    78%
lib/workflow.py                         10     10     0%
tests/__init__.py                        0      0   100%
tests/test_cache.py                     21      2    90%
tests/test_config.py                     9      0   100%
tests/test_utils.py                      6      0   100%
--------------------------------------------------------
TOTAL                                  396    291    27%
```
## Integration tests

... coming...