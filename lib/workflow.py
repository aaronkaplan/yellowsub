"""
Workflow generator

This python module reads in a workflow.yml config file and will instantiate all required
processors and connect them to the right queues and exchanges.
"""

import yaml
import logging

from lib.config import GLOBAL_WORKFLOW_PATH


def load_workflows(file: str = GLOBAL_WORKFLOW_PATH) -> dict:
    """Load the wokflow.yml file and iterate over all workflows which are defined there.
    yields back a dict : { "from_q": <q>, "to_q": <dst q>, "to_ex": <dest exchange> }

    @param file: the path to the workflow.yml file, defaults to the default etc/workflow.yml
    """
    try:
        with open(file, 'r') as _f:
            workflows = yaml.safe_load(_f)
    except (OSError, FileNotFoundError) as ex:
        logging.error('Could not load workflow config file %s. Reason: %s' % (file, str(ex)))
        raise ValueError('File not found: %r.' % file)
        # FIXME: here, we might also have other exceptions maybe? Catch them!

    retval = dict()
    # see workflow.yml for an example of how it looks like
    for name, settings in workflows.items():

        if 'flow' not in settings:
            continue

        for flow in settings["flow"]:

            if 'processor' not in flow:
                continue

            retval['workflow_name'] = name
            retval['processor'] = flow.get('processor')
            retval['from_q'] = flow.get('from_q', None)
            retval['to_ex'] = flow.get('to_ex', None)
            retval['to_q'] = flow.get('to_q', None)
            retval['parallelism'] = flow.get('parallelism', 1)

            yield retval


class Workflow():       # FIXME: need to rethink this class
    workflow_config = ""
    workflows = []

    def __init__(self, workflow_config: str = GLOBAL_WORKFLOW_PATH):
        with open(workflow_config, 'r') as f:
            wfs = yaml.safe_load(f)
            # validate against a schema
            print(wfs)

    def plot_graph(self):
        pass


if __name__ == "__main__":
    wf = Workflow()
