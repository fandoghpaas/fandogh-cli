import click
from .base_commands import FandoghCommand
from .fandogh_client import deploy_volume


@click.group('volume')
def volume():
    """Volume management commands"""


@click.command('create', help='creates new pvc', cls=FandoghCommand)
@click.option('--name', '-n', help='name of the volume', prompt='PVC Name')
@click.option('--capacity', '-c', help='volume capacity', prompt='Storage Capacity')
def create_volume(name, capacity):
    click.echo(deploy_volume(name, capacity))


volume.add_command(create_volume)
