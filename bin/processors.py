"""Workflows orchestrator"""

import click
# import lib.config     # FIXME, should YELLOWSUB_ROOT_DIR here...


@click.group()
@click.option('--config', default='etc/config.yml', type=click.Path(exists=True), help='The main config file.')
@click.option('--rootdir', default='.', type=click.Path(exists=True), help='The root directory')        # FIXME: YELLOWSUB_ROOT_DIR
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
@click.option('--processor-name', type=str, help='Start a specific processor. Default: *', default='*', required=False)
@click.pass_context
def start(ctx, processor_name):
    """
    Start all (default) or a specific processor by name.
    """

    if processor_name != '*':
        click.echo("Starting processor {} using {}".format(processor_name, ctx.obj['config']))
    else:
        click.echo("Starting all processor in {}".format(ctx.obj['config']))


@cli.command(short_help='Stop processor')
@click.option('--processor-name', type=str, help='Stop a specific processor.', default='*', required=True)
@click.pass_context
def stop(ctx, processor_name):
    """
    Stop a specific processor given by name.
    """

    click.echo("Stoping processor {}".format(processor_name))


@cli.command(short_help='List processors')
@click.pass_context
def list(ctx):
    """
    List all processors.
    """

    click.echo("Listing all processors")


if __name__ == '__main__':
    cli(obj={})
