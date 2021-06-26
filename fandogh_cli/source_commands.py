from time import sleep

import yaml
import json
import os
from .source import key_hints, manifest_builders
from .presenter import present_service_detail
from .image_commands import show_image_logs
from .fandogh_client.source_client import upload_source, get_project_types, get_ignore_files_from_server
from .base_commands import FandoghCommand
from .config import ConfigRepository
from .fandogh_client import *
from .utils import read_manifest
from .workspace import Workspace
import sys
import re
import itertools

base_sources_url = '{}sources'.format(base_url)


@click.group("source")
def source():
    """Source management commands"""


@click.command('init', cls=FandoghCommand)
@click.option('-n', '--name', 'name', prompt='Service Name')
def init(name):
    """Initializes a project based on the selected framework"""
    service_name_pattern = re.compile("^([a-z]+(-*[a-z0-9]+)*){1,100}$")
    if not service_name_pattern.match(name):
        click.echo(
            format_text(
                'manifest.name:service names must match regex "[a-z]([-a-z0-9]*[a-z0-9])?" '
                'and length lower than 100 char.',
                TextStyle.FAIL), err=True)
        return

    project_types = get_project_types()
    project_type = prompt_project_types(project_types)
    project_type_hint = key_hints.get(project_type['name'])
    if project_type_hint:
        project_type_hint()

    chosen_params = {'context': click.prompt('The context directory', default='.')}
    if project_type.get('parameters', None):

        for param in project_type.get('parameters'):
            hint = key_hints.get(param['key'], None)
            if hint:
                hint()
            chosen_params[param['key']] = click.prompt(param['name'], default=param.get('default', None))

    initialize_project(name, project_type, chosen_params)
    create_fandoghignore_file(project_type.get('name'))

    click.echo(format_text('Your source has been initialized.\n'
                           'Please consider to run `fandogh source run` command whenever you are going to deploy your changes',
                           TextStyle.OKGREEN))


@click.command('run', cls=FandoghCommand)
@click.option('--with_timestamp', 'with_timestamp', is_flag=True, default=False,
              help='timestamp for each line of image build process')
@click.option('-p', '--parameter', 'parameters', help='Manifest parameters', multiple=True)
def run(with_timestamp, parameters):
    # to implicitly check whether user's token is still valid or not
    get_images()
    fandogh_yml_path = os.path.join(os.getcwd(), 'fandogh.yml')
    with open(fandogh_yml_path, 'r') as config_file:
        new_manifest = config_file.read()
    if parameters:
        new_manifest = read_manifest(fandogh_yml_path, parameters)
    manifest_repository = ConfigRepository(configurations=yaml.safe_load(new_manifest))
    context_pth = manifest_repository.get('spec', {}).get('source', {}).get('context', '.')
    workspace = Workspace(context=context_pth)
    click.echo(message='workspace size is : {} MB'.format(round(workspace.tar_file_size)))
    if workspace.tar_file_size > max_workspace_size:
        click.echo(format_text(
            "The workspace size should not be larger than {}MB, its {}MB.".format(max_workspace_size,
                                                                                  round(workspace.tar_file_size, 2)),
            TextStyle.WARNING
        ))

    bar = click.progressbar(length=int(workspace.tar_file_size_kb), label='Uploading the workspace')
    shared_values = {'diff': 0}

    def monitor_callback(monitor):
        progress = monitor.bytes_read - shared_values['diff']
        bar.update(progress)
        shared_values['diff'] += progress

    try:
        name = manifest_repository.get('name')
        upload_source(str(workspace),
                      json.dumps(manifest_repository.get_dict()),
                      monitor_callback)
        bar.render_finish()
    finally:
        workspace.clean()

    show_image_logs(name.lower(), 'latest', with_timestamp)

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
            click.echo(format_text(
                "You project deployed successfully.\nWill be available in a few seconds via domains you setup.",
                TextStyle.OKGREEN))
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


def setup_manifest(name, project_type_name, chosen_params):
    manifest_builder = manifest_builders.get(project_type_name, None)
    if manifest_builder is None:
        source = {
            'context': chosen_params.get('context', '.'),
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
    else:
        manifest = manifest_builder(name, project_type_name, chosen_params)

    manifest_repository = ConfigRepository(os.path.join(os.getcwd(), 'fandogh.yml'), manifest)
    manifest_repository.save()


def create_fandoghignore_file(project_name):
    exist_ignore_list = []
    if os.path.exists('.fandoghignore'):
        exist_ignore_list = [line.rstrip() for line in open('.fandoghignore')]
        os.remove('.fandoghignore')
    exist_ignore_list = itertools.chain.from_iterable(
        (exist_ignore_list, get_ignore_files_from_server(project_type=project_name)))
    unique_ignore_list = set(exist_ignore_list)
    with open('.fandoghignore', 'w+') as file:
        for item in unique_ignore_list:
            file.write("{}\n".format(item))


source.add_command(init)
source.add_command(run)
