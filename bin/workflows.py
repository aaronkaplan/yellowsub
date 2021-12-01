"""Workflows orchestrator"""

import click


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
        click.echo("Stoping workflows ID {} using {}".format(workflow_id, ctx.obj['config']))
    else:
        click.echo("Stoping all workflows in {}".format(ctx.obj['config']))


@cli.command(short_help='List workflows')
@click.pass_context
def list(ctx):
    """
    List all (default) workflows.
    """

    click.echo("Listing all workflows in {}".format(ctx.obj['config']))


if __name__ == '__main__':
    cli(obj={})
