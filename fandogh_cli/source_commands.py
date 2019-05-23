from time import sleep

import yaml

from .source import key_hints
from .presenter import present_service_detail
from .image_commands import show_image_logs
from .fandogh_client.source_client import upload_source, get_project_types
from .base_commands import FandoghCommand
from .config import ConfigRepository
from .fandogh_client import *
from .workspace import Workspace
import sys


@click.group("source")
def source():
    """Source management commands"""


@click.command('init', cls=FandoghCommand)
@click.option('-n', '--name', 'name', prompt='Service Name')
def init(name):
    """Initializes a project based on the selected framework"""
    project_types = get_project_types()
    project_type = prompt_project_types(project_types)
    project_type_hint = key_hints.get(project_type['name'])
    if project_type_hint:
        project_type_hint()

    chosen_params = {}
    if project_type.get('parameters', None):

        for param in project_type.get('parameters'):
            hint = key_hints.get(param['key'], None)
            if hint:
                hint()
            chosen_params[param['key']] = click.prompt(param['name'])

    initialize_project(name, project_type, chosen_params)
    click.echo(format_text('Your source has been initialized.\n'
                           'Please consire to run `fandogh source run` command whenever you are going to deploy your changes',
                           TextStyle.OKGREEN))


@click.command('run', cls=FandoghCommand)
def run():
    workspace = Workspace()
    manifest_repository = ConfigRepository(os.path.join(os.getcwd(), 'fandogh.yml'))

    bar = click.progressbar(length=int(workspace.zip_file_size_kb), label='Uploading the workspace')
    shared_values = {'diff': 0}

    def monitor_callback(monitor):
        progress = monitor.bytes_read - shared_values['diff']
        bar.update(progress)
        shared_values['diff'] += progress

    try:
        name = manifest_repository.get('name')
        response = upload_source(str(workspace), name,
                                 manifest_repository.get('spec', {}).get('source', {}).get('project_type'),
                                 monitor_callback)
        bar.render_finish()
    finally:
        workspace.clean()

    show_image_logs(name, 'latest')

    def hide_manifest_env_content(content):
        if 'spec' not in content:
            return content
        if 'env' not in content['spec']:
            return content

        from copy import deepcopy
        temp_content = deepcopy(content)
        for env in temp_content['spec']['env']:
            if env.get('hidden', False):
                env['value'] = '***********'
        return temp_content

    click.echo(
        yaml.safe_dump(hide_manifest_env_content(manifest_repository.get_dict()),
                       default_flow_style=False),
    )

    while True:
        details = get_details(name)

        if not details:
            sys.exit(302)

        click.clear()

        if details.get('state') == 'RUNNING':
            present_service_detail(details)
            # click.echo(message)
            sys.exit(0)

        elif details.get('state') == 'UNSTABLE':
            present_service_detail(details)
            click.echo(
                'You can press ctrl + C to exit details service state monitoring')
            sleep(3)


def prompt_project_types(project_types):
    for idx, project_type in enumerate(project_types):
        click.echo('-[{}] {}'.format(idx + 1, project_type['label']))

    project_type_index = click.prompt('Please choose one of the project types above',
                                      type=click.Choice(list(map(lambda i: str(i), range(1, len(project_types) + 1)))),
                                      show_choices=False
                                      )

    selected_project_type = project_types[int(project_type_index) - 1]

    return selected_project_type


def initialize_project(name, project_type, chosen_params):
    project_type_name = project_type['name']
    setup_manifest(name, project_type_name, chosen_params)
    if project_type_name == 'static_website':
        setup_sample(name, project_type_name, chosen_params)


def setup_manifest(name, project_type_name, chosen_params):
    source = {
        'context': '.',
        'project_type': project_type_name
    }

    source.update(chosen_params)
    manifest = {
        'kind': 'ExternalService',
        'name': name,
        'spec': {
            'source': source,
            'port': 80,
            'image_pull_policy': 'Always'
        }
    }

    manifest_repository = ConfigRepository(os.path.join(os.getcwd(), 'fandogh.yml'), manifest)
    manifest_repository.save()


def setup_sample(name, project_type_name, chosen_params):
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
