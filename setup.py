import os
from pathlib import Path
from setuptools import find_packages, setup

from version import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as handle:
    README = handle.read()

PROCESSORS = []

base_path = Path(__file__).parent / 'processors'
processorfiles = [processorfile for processorfile in Path(base_path).glob('**/*.py') if
                  processorfile.is_file() and not processorfile.name.startswith('_')]
for file in processorfiles:
    file = Path(str(file).replace(str(base_path), 'processors'))
    module = '.'.join(file.with_suffix('').parts)
    PROCESSORS.append('{0} = {0}:PROCESSOR.run'.format(module))

print("DEBUG: PROCESSORS={}".format(PROCESSORS))

setup(
        name = 'yellowsub',
        version = __version__,
        maintainer = 'L. Aaron Kaplan',
        maintainer_email = 'aaron@lo-res.org',
        python_requires = '>=3.9',
        license = 'AGPLv3',
        description = 'yellowsub is a Threat Intelligence Platform (TIP) which can automate incident response workflows '
                      'as well as Cyber Threat Intelligence and hunting. It is flexible in the formats it supports and '
                      'can connect to multiple ',
        long_description = README,
        packages = find_packages(),
        include_package_data = True,
        install_requires = [
            'Click',
        ],
        entry_points = {
            'console_scripts': [
                                   'workflows = bin.workflows:cli',
                                   'processors = bin.processors:cli',
                               ] + PROCESSORS,
        },
)
