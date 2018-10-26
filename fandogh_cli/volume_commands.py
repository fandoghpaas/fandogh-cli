import click

from .presenter import present
from .base_commands import FandoghCommand
from .fandogh_client import create_pvc, delete_pvc, list_volumes


@click.group('volume')
def volume():
    """Volume management commands"""


@click.command('create', help='Create new pvc', cls=FandoghCommand)
@click.option('--name', '-n', help='Name of the volume', prompt='Volume Name')
@click.option('--capacity', '-c', help='Volume capacity', prompt='Storage Capacity')
def create_volume(name, capacity):
    click.echo(create_pvc(name, capacity))


@click.command('delete', help='Delete pvc', cls=FandoghCommand)
@click.option('--name', '-n', help='Name of the volume', prompt='Volume Name')
def delete_volume(name):
    click.echo(delete_pvc(name))


@click.command('list', help='Volume list', cls=FandoghCommand)
def volume_list():
    table = present(lambda: list_volumes(),
                    renderer='table',
                    headers=['Name', 'Status', 'Volume', 'Capacity', 'Editable', 'Age'],
                    columns=['name', 'status', 'volume', 'capacity', 'editable', 'age'])

    if table:
        click.echo(table)


volume.add_command(create_volume)
volume.add_command(delete_volume)
volume.add_command(volume_list)
