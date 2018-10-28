import click

from .presenter import present
from .base_commands import FandoghCommand
from .fandogh_client import create_volume_claim, delete_volume_claim, list_volumes


@click.group('volume')
def volume():
    """Volume management commands"""


@click.command('add', help='Add new volume', cls=FandoghCommand)
@click.option('--name', '-n', help='Name of the volume', prompt='Volume Name')
@click.option('--capacity', '-c', help='Volume capacity', prompt='Storage Capacity')
@click.option('--detach', '-d', help='Execute request in background')
def create_volume(name, capacity):
    click.echo('Creating volume may take some times, please wait...')
    click.echo(create_volume_claim(name, capacity))


@click.command('delete', help='Delete specific volume', cls=FandoghCommand)
@click.option('--name', '-n', help='Name of the volume', prompt='Volume Name')
def delete_volume(name):
    click.echo('Volume delete may take some times, please wait...')
    click.echo(delete_volume_claim(name))


@click.command('list', help='Volume list', cls=FandoghCommand)
def volume_list():
    table = present(lambda: list_volumes(),
                    renderer='table',
                    headers=['Name', 'Status', 'Volume', 'Capacity', 'Editable', 'Creation Date'],
                    columns=['name', 'status', 'volume', 'capacity', 'editable', 'age'])

    if table:
        click.echo(table)


volume.add_command(create_volume)
volume.add_command(delete_volume)
volume.add_command(volume_list)
