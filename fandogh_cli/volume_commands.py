import click
from .base_commands import FandoghCommand
from .fandogh_client import create_pvc, delete_pvc


@click.group('volume')
def volume():
    """Volume management commands"""


@click.command('create', help='creates new pvc', cls=FandoghCommand)
@click.option('--name', '-n', help='name of the volume', prompt='Volume Name')
@click.option('--capacity', '-c', help='volume capacity', prompt='Storage Capacity')
def create_volume(name, capacity):
    click.echo(create_pvc(name, capacity))


@click.command('delete', help='delete pvc', cls=FandoghCommand)
@click.option('--name', '-n', help='name of the volume', prompt='Volume Name')
def delete_volume(name):
    click.echo(delete_pvc(name))


volume.add_command(create_volume)
volume.add_command(delete_volume)
