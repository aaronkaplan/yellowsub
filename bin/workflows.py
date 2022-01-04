"""Workflows orchestrator"""

import copy
import sys
import os
from pathlib import Path
import subprocess
import signal

import click
from lib.config import ROOT_DIR, PID_FILES_DIR, Config
import lib.workflow as workflow

def pid_filename(workflow, processor, pid):
    return f"{workflow}.{processor}.{pid}.pid"


@click.group()
@click.option('--config', default = 'etc/config.yml', type = click.Path(exists = True), help = 'The global config file.')
@click.option('--workflow-config', default = 'etc/workflow.yml', type = click.Path(exists = True), help = 'The workflows config file.')
@click.option('--rootdir', default = '.', type = click.Path(exists = True), help = 'The root directory')
@click.option('--verbose', is_flag = True)
@click.pass_context
def cli(ctx, config, workflow_config, rootdir, verbose):
    ctx.ensure_object(dict)

    if verbose:
        click.echo('VERBOSE is on')
        ctx.obj['verbose'] = True
    if config:
        click.echo('using config file {}'.format(config))
        ctx.obj['config'] = config
    if workflow_config:
        click.echo('using workflow_config file {}'.format(workflow_config))
        ctx.obj['workflow_config'] = workflow_config
    if rootdir:
        click.echo('using rootdir {}'.format(rootdir))
        ctx.obj['rootdir'] = rootdir
    pass


@cli.command(short_help='Start workflows')
@click.option('--workflow-id', type=str, help='Start a specific workflow ID. Default: *', default=None, required=False)
@click.pass_context
def start(ctx, workflow_id):
    """
    Start all (default) or a specific workflow by ID.
    """

    if workflow_id:
        click.echo(f"Attempting to starting workflow ID {workflow_id} using {ctx.obj['config']}")
    else:
        click.echo("Starting all workflows in {}".format(ctx.obj['config']))

    workflows = []
    for flow in workflow.load_workflows(ctx.obj['workflow_config']):
        if workflow_id and workflow_id != flow['workflow_name']:
            continue
        workflows.append(copy.deepcopy(flow))

    if len(workflows) == 0:
        click.echo("No workflow have been loaded from workflows config file.")
        sys.exit(254)

    for flow in workflows:
        processor = flow.get('processor')
        click.echo(f"Starting {processor} ...")

        # find the module name based on the processor
        # check if the specific config file exists:
        config_file = Path(ROOT_DIR, f"etc/processors/{processor}.yml")
        if not os.path.exists(config_file):
            click.echo(f"Could not find specific config file for {processor}")
            continue

        config = Config().load(config_file)
        module = config['module']
        proc = subprocess.Popen([module, processor])
        Path(PID_FILES_DIR, pid_filename(flow['workflow_name'], processor, proc.pid)).touch()



@cli.command(short_help='Stop workflows')
@click.option('--workflow-id', type=str, help='Stop a specific workflow ID. Default: *', default=None, required=False)
@click.pass_context
def stop(ctx, workflow_id):
    """
    Stop all (default) or a specific workflow by ID.
    """

    if workflow_id:
        click.echo(f"Attempting to stop workflow ID {workflow_id} using {ctx.obj['config']}")
    else:
        click.echo("Stopping all workflows in {}".format(ctx.obj['config']))

    workflows = []
    for flow in workflow.load_workflows(ctx.obj['workflow_config']):
        if workflow_id and workflow_id != flow['workflow_name']:
            continue
        workflows.append(copy.deepcopy(flow))

    if len(workflows) == 0:
        click.echo("No workflow have been loaded from workflows config file.")
        sys.exit(254)

    directory = Path(PID_FILES_DIR)

    for flow in workflows:
        for item in directory.iterdir():

            if not item.is_file():
                continue

            workflow_name = item.name.split('.')[0]

            if workflow_name == flow["workflow_name"]:
                pid = int(item.name.split('.')[-2])
                os.kill(pid, signal.SIGKILL)
                item.unlink()

    click.echo("All processors stopped.")


@cli.command(short_help = 'List workflows')
@click.pass_context
def list(ctx):
    """
    List all workflows.
    """

    wf_config_file = ctx.obj['workflow_config']
    click.echo("Listing all workflows in {}".format(wf_config_file))
    for wf in workflow.load_workflows(wf_config_file):
        click.echo(wf)


if __name__ == '__main__':
    cli(obj = {})
