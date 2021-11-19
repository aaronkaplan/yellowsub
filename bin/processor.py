"""Workflows orchestrator"""

import click
import lib.config


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


@cli.command(short_help='Start processor')
@click.option('--id', type=str, help='Start a specific workflow ID. Default: *', default='*', required=False)
@click.pass_context
def start(ctx, id):
    """
    Start all (default) or a specific processor by ID. 
    """

    if id != '*':
        click.echo("Starting processor ID {} using {}".format(id, ctx.obj['config']))
    else:
        click.echo("Starting all processor in {}".format(ctx.obj['config']))


@cli.command(short_help='Stop processor')
@click.option('--id', type=str, help='Stop a specific processor ID.', default='*', required=True)
@click.pass_context
def stop(ctx, id):
    """
    Stop a specific processor given by ID. 
    """

    click.echo("Stoping processor ID {}".format(id))


@cli.command(short_help='List processors')
@click.pass_context
def list(ctx):
    """
    List all processors.
    """

    click.echo("Listing all processors")


if __name__ == '__main__':
    cli(obj={})
