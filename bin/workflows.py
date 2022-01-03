"""Workflows orchestrator"""

import sys
import os
from pathlib import Path
import subprocess

import click
from config import ROOT_DIR, Config
import lib.workflow as workflow


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


@cli.command(short_help = 'Start workflows')
@click.option('--workflow_id', type = str, help = 'Start a specific workflow ID. Default: *', default = '*',
              required = False)
@click.pass_context
def start(ctx, workflow_id):
    """
    Start all (default) or a specific workflow by ID.
    """

    wf_config_file = ctx.obj['workflow_config']
    wfs = workflow.load_workflows(wf_config_file)
    wf_names = [f['workflow_name'] for f in wfs]
    if id != '*':
        click.echo(f"Attempting to starting workflows ID {workflow_id} using {wf_config_file}")
        if workflow_id not in wf_names:
            click.echo("Could not find workflow. Not starting anything.")
        else:
            # for every line in the wf, start the processor
            for flow in wfs:
                if workflow_id not in flow['workflow_name']:
                    continue
                processor_name = flow.get('processor')
                # from_q = flow.get('from_q', None)
                # to_ex = flow.get('to_ex', None)
                # to_q = flow.get('to_q', None)
                # parallelism = flow.get('parallelism', 1)
                # find the module name based on the processor_name
                # check if the specific config file exists:
                specific_config = Path(ROOT_DIR / 'etc' / 'processors' / f"{processor_name}.yml")
                if not os.path.exists(specific_config):
                    click.echo(f"Could not find specific config file for {processor_name}")
                    continue
                _c = Config()
                c = _c.load(specific_config)
                module_name = c['module']
                subprocess.Popen([module_name, processor_name])
    else:
        click.echo("Starting all workflows in {}".format(ctx.obj['config']))


@cli.command(short_help = 'Stop workflows')
@click.option('--workflow-id', type = str, help = 'Stop a specific workflow ID. Default: *', default = '*',
              required = False)
@click.pass_context
def stop(ctx, workflow_id):
    """
    Stop all (default) or a specific workflow by ID.
    """

    if id != '*':
        click.echo("Stopping workflows ID {} using {}".format(workflow_id, ctx.obj['config']))
    else:
        click.echo("Stopping all workflows in {}".format(ctx.obj['config']))


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


# ###############################
# Sample workflow. Take this as a basis on how to create workflows via reading workflow.yml
# XXX FIXME!!
@cli.command(short_help = 'Start DEMO workflows')
@click.pass_context
def start_demo(ctx):
    """
    Start a very simple DEMO workflow: filecollector -> parser -> enricher -> fileOutput
                                                   ex1       ex2         ex3
    """
    click.echo("Starting DEMO workflows")
    try:
        from processors.collectors.fileCollector.filecollector import FileCollector
        from processors.parsers.listOfHashesParser.parser import HashListToStixBundleParser
        from processors.enrichers.null.nullEnricher import nullEnricher
        from processors.outputs.fileOutput.fileoutput import FileOutput
    except Exception as ex:
        click.echo("Could not find processors. Reason: {}".format(str(ex)))
        sys.exit(255)
    fcollector = FileCollector(processor_name = "MyFileCollector")
    parser = HashListToStixBundleParser(processor_name = "MyParser")
    enricher = nullEnricher(processor_name = "MyEnricher")
    output = FileOutput(processor_name="MyOutput")

    output.start(from_ex = "ex3", to_ex = None)  # missing popen here!
    enricher.start(from_ex = "ex2", to_ex = "ex3")
    parser.start(from_ex = "ex1", to_ex = "ex2")
    fcollector.start(to_ex = "ex1")


if __name__ == '__main__':
    cli(obj = {})
