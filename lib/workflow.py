"""Workflow generator. This python module reads in a workflow.yml config file and will instantiate all required
processors and connect them to the right queues and exchanges."""

import yaml

# from config import config


DEFAULT_WORKFLOW_FILE = "etc/workflow.yml"


class Workflow():
    workflow_config = ""
    workflows = []

    def __init__(self, workflow_config: str = DEFAULT_WORKFLOW_FILE):
        with open(workflow_config, 'r') as f:
            wfs = yaml.safe_load(f)
            # validate against a schema
            print(wfs)

    def plot_graph(self):
        pass


if __name__ == "__main__":
    wf = Workflow()
