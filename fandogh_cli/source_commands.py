from .image_commands import show_image_logs
from .fandogh_client.source_client import upload_source
from .base_commands import FandoghCommand
from .config import ConfigRepository
from .fandogh_client import *
from .workspace import Workspace


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
def run():
    workspace = Workspace()
    manifestRepository = ConfigRepository(os.path.join(os.getcwd(), 'fandogh.yml'))

    bar = click.progressbar(length=int(workspace.zip_file_size_kb), label='Uploading the workspace')
    shared_values = {'diff': 0}

    def monitor_callback(monitor):
        progress = monitor.bytes_read - shared_values['diff']
        bar.update(progress)
        shared_values['diff'] += progress

    try:
        name = manifestRepository.get('name')
        response = upload_source(str(workspace), name, manifestRepository.get('spec', {}).get('project_type'), monitor_callback)
        bar.render_finish()
    finally:
        workspace.clean()

    show_image_logs(name, 'latest')


def prompt_project_types():
    project_types = ['static_website',
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
    if project_type == 'static_website':
        setup_manifest(name, project_type)
        setup_sample(name, project_type)


def setup_manifest(name, project_type):
    if project_type == 'static_website':
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
