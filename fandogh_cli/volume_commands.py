import click
from fandogh_cli.utils import format_text, TextStyle

from .presenter import present
from .base_commands import FandoghCommand
from .fandogh_client import create_volume_claim, delete_volume_claim, list_volumes

'''
    This class is for volume commands
    all cli commands related to volume CRUD and etc 
    are written here
    
    method list:
    
    - volume: parent
    - create_volume
    - delete volume
    - volume_list
    
'''

'''

  Volume parent command
  This command should be called before any sub commands
  
'''


@click.group('volume')
def volume():
    """Volume management commands"""


'''
  Fandogh user calls this cli command
  in order to create a new volume.
  it will show the resulting value in table format
  
  command name:
  
  - add 
  
  options:
  
  . --name or -n : this option is required and will be used as the volume name
  . --capacity or -c: this option is required and will be used as the volume size
  . --detach or -d: using this command user will imply that whether the request
      should be executed in background or not. default value is False. 
'''


@click.command('add', help='Add new volume', cls=FandoghCommand)
@click.option('--name', '-n', help='Name of the volume', prompt='Volume Name')
@click.option('--capacity', '-c', help='Volume capacity', prompt='Storage Capacity')
@click.option('--detach', '-d', help='Execute request in background', default=False, is_flag=True)
def create_volume(name, capacity, detach):
    click.echo('Creating volume may take some times, please wait...')
    if detach:
        create_volume_claim(name, capacity)
    else:
        data = create_volume_claim(name, capacity)
        click.echo('volume \'{}\' was built successfully and is ready to attach'.format(data.get('name')))
        table = present(lambda: [data],
                        renderer='table',
                        headers=['Name', 'Status', 'Mounted To', 'Volume', 'Capacity', 'Creation Date'],
                        columns=['name', 'status', 'mounted_to', 'volume', 'capacity', 'age'])
        click.echo(table)


'''
  Fandogh user calls this cli command
  in order to delete an existing volume.
  
  command name:
  
  - delete
  
  options:
  
  . --name or -n: this option is required and will be used as volume name
  
'''


@click.command('delete', help='Delete specific volume', cls=FandoghCommand)
@click.option('--name', '-n', help='Name of the volume', prompt='Volume Name')
def delete_volume(name):
    if click.confirm(format_text('If you proceed all your data will be deleted, do you want to continue?',
                                 TextStyle.WARNING)):
        click.echo('Volume delete may take some times, please wait...')
        click.echo(delete_volume_claim(name))


'''
  Fandogh user calls this cli command
  in order to get the list of volumes available
  in her/his namespace
  
  command:
  
  - volume_list
  
  options:
    
    None required
    
'''


@click.command('list', help='Volume list', cls=FandoghCommand)
def volume_list():
    table = present(lambda: list_volumes(),
                    renderer='table',
                    headers=['Name', 'Status', 'Mounted To', 'Volume', 'Capacity', 'Creation Date'],
                    columns=['name', 'status', 'mounted_to', 'volume', 'capacity', 'age'])

    if table:
        click.echo(table)
    else:
        click.echo('You have no volumes in your namespace!')


volume.add_command(create_volume)
volume.add_command(delete_volume)
volume.add_command(volume_list)
