import click
import yaml
import sys
from .fandogh_client import *
from .config import get_project_config, ConfigRepository
from .utils import format_text, TextStyle, read_manifest
from .base_commands import FandoghCommand
from time import sleep
from .presenter import present_service_detail, present


@click.group("source")
def source():
    """Source management commands"""


@click.command('init', cls=FandoghCommand)
@click.option('-n', '--name', 'name', prompt='Service Name')
def init(name):
    """Initializes a project based on the selected framework"""
    project_type = prompt_project_types()
    initialize_project(name, project_type)


@click.command('run', cls=FandoghCommand)
def run(service_name):
    """Destroy service"""
    click.echo(
        'you are about to destroy service with name {}.'.format(service_name))
    click.echo('It might take a while!')
    message = present(lambda: destroy_service(service_name))
    click.echo(message)


def prompt_project_types():
    project_types = ['Static Website',
                     'Laravel',
                     'Dango',
                     'ASP.net core'
                     ]
    for idx, project_type in enumerate(project_types):
        click.echo('-[{}] {}'.format(idx + 1, project_type))

    project_type_index = click.prompt('Please choose one of the project types above',
                                      type=click.Choice(list(map(lambda i: str(i), range(1, len(project_types) + 1)))),
                                      show_choices=False
                                      )

    selected_project_type = project_types[int(project_type_index) - 1]
    click.echo('You selected {}'.format(selected_project_type))
    return selected_project_type


def initialize_project(name, project_type):
    if project_type == 'Static Website':
        setup_manifest(name, project_type)
        setup_sample(name, project_type)


def setup_manifest(name, project_type):
    if project_type == 'Static Website':
        manifest = {
            'kind': 'ExternalService',
            'name': name,
            'spec': {
                'project_type': project_type,
                'context': '.',
                'port': 80
            }
        }

        manifestRepository = ConfigRepository(os.path.join(os.getcwd(), 'fandogh.yml'), manifest)
        manifestRepository.save()


def setup_sample(name, project_type):
    with open('index.html', 'w') as sample:
        sample.write('''
        <html>
            <head>
                <title> Welcome to {}</title>
            </head>
            <body>
            Project {}
            </br>
            Powered by Fandogh 
            </body>
        </html>
        '''.format(name, name))


source.add_command(init)
source.add_command(run)
