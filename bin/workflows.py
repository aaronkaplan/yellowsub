"""Workflows orchestrator"""

import click
import sys


@click.group()
@click.option('--config', default='etc/config.yml', type=click.Path(exists=True), help='The main config file.')
@click.option('--rootdir', default='.', type=click.Path(exists=True), help='The root directory')
@click.option('--verbose', is_flag=True)
@click.pass_context
def cli(ctx, config, rootdir, verbose):
    ctx.ensure_object(dict)

    if verbose:
        click.echo('VERBOSE is on')
        ctx.obj['verbose'] = True
    if config:
        click.echo('using config file {}'.format(config))
        ctx.obj['config'] = config
    if rootdir:
        click.echo('using rootdir {}'.format(rootdir))
        ctx.obj['rootdir'] = rootdir

    pass


@cli.command(short_help='Start workflows')
@click.option('--workflow-id', type=str, help='Start a specific workflow ID. Default: *', default='*', required=False)
@click.pass_context
def start(ctx, workflow_id):
    """
    Start all (default) or a specific workflow by ID.
    """

    if id != '*':
        click.echo("Starting workflows ID {} using {}".format(workflow_id, ctx.obj['config']))
    else:
        click.echo("Starting all workflows in {}".format(ctx.obj['config']))


@cli.command(short_help='Stop workflows')
@click.option('--workflow-id', type=str, help='Stop a specific workflow ID. Default: *', default='*', required=False)
@click.pass_context
def stop(ctx, workflow_id):
    """
    Stop all (default) or a specific workflow by ID.
    """

    if id != '*':
        click.echo("Stopping workflows ID {} using {}".format(workflow_id, ctx.obj['config']))
    else:
        click.echo("Stopping all workflows in {}".format(ctx.obj['config']))


@cli.command(short_help='List workflows')
@click.pass_context
def list(ctx):
    """
    List all (default) workflows.
    """

    click.echo("Listing all workflows in {}".format(ctx.obj['config']))


# ###############################
# Sample workflow. Take this as a basis on how to create workflows via reading workflow.yml
@cli.command(short_help='Start DEMO workflows')
@click.pass_context
def start(ctx):
    """
    Start a very simple DEMO workflow: filecollector -> parser -> enricher -> fileOutput
                                                   ex1       ex2         ex3
    """
    click.echo("Starting DEMO workflows")
    try:
        from processors.collectors.fileCollector.filecollector import FileCollector
        from processors.parsers.flatlisttostixbundleparser import  HashListToStixBundleParser
        from processors.enrichers.null.nullEnricher import nullEnricher
        from processors.outputProcessors.fileOutput.fileoutput import FileOutput
    except Exception as ex:
        click.echo("Could not find processors.")
        sys.exit(255)
    fcollector = FileCollector(processor_id = "MyFileCollector")
    parser = HashListToStixBundleParser(processor_id = "MyParser")
    enricher = nullEnricher(processor_id = "MyEnricher")
    output = FileOutput(processor_id = "MyOutput")

    output.start(from_ex = "ex3", to_ex = None)     # missing popen here!
    enricher.start(from_ex = "ex2", to_ex = "ex3")
    parser.start(from_ex = "ex1", to_ex = "ex2")
    fcollector.start(to_ex = "ex1")

if __name__ == '__main__':
    cli(obj={})
