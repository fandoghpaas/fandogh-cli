from time import sleep

import yaml
import json
import os
from .source import key_hints, manifest_builders
from .presenter import present_service_detail
from .image_commands import show_image_logs
from .fandogh_client.source_client import upload_source, get_project_types
from .base_commands import FandoghCommand
from .config import ConfigRepository
from .fandogh_client import *
from .workspace import Workspace
import sys
import re


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
def run(with_timestamp):
    # to implicitly check whether user's token is still valid or not
    get_images()
    manifest_repository = ConfigRepository(os.path.join(os.getcwd(), 'fandogh.yml'))
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


project_type_ignore_dict = {
    'django': ['.git', '*.log', '*.pot', '*.pyc', '__pycache__/', 'local_settings.py', '.env', 'db.sqlite3', '*.mo',
               '*.pot', 'venv', 'venv/'],
    'laravel': [
        '.git', 'node_modules', '/public/hot', '/public/storage', '/storage/*.key', '/vendor', '.env', '.env.backup',
        '.phpunit.result.cache', 'Homestead.json', 'Homestead.yaml', 'npm-debug.log', 'yarn - error.log',
        'node_modules', 'node_modules/', 'vendor', 'vendor/'],
    'static_website': ['.tern-port', '.dynamodb/', '.fusebox/', '.serverless/', 'serverless', 'public', '.cache/',
                       '.nuxt',
                       '.next', '.cache', '.env.test', '.env', '.yarn-integrity', '*.tgz', '.node_repl_history',
                       '.rts2_cache_umd/', '.rts2_cache_es/', '.rts2_cache_cjs/', '.rpt2_cache/', '.eslintcache',
                       '.npm',
                       '*.tsbuildinfo', 'typings/', 'jspm_packages/', 'build/Release', '.lock-wscript',
                       'bower_components',
                       '.grunt', '.nyc_output', '*.lcov', 'coverage', 'lib-cov', '*.pid.lock', '*.seed', '*.pid',
                       'pids',
                       'logs', '*.log', 'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*', 'lerna-debug.log*'],
    'aspnetcore': ['.git', '.vs/', '[Dd]ebug/', '[Dd]ebugPublic/', '[Rr]elease/', '[Rr]eleases/', 'x64/', 'x86/',
                   'build/',
                   'bld/',
                   '[Bb]in/', '[Oo]bj/', '[Oo]ut/', 'msbuild.log', 'msbuild.err', 'msbuild.wrn', '.idea', '*.pyc',
                   '.vscode', 'nupkg/'],
    'nodejs': ['.git', '.tern-port', '.dynamodb/', '.fusebox/', '.serverless/', 'serverless', '.cache/',
               '.nuxt',
               '.next', '.cache', '.env.test', '.env', '.yarn-integrity', '*.tgz', '.node_repl_history',
               '.rts2_cache_umd/', '.rts2_cache_es/', '.rts2_cache_cjs/', '.rpt2_cache/', '.eslintcache', '.npm',
               '*.tsbuildinfo', 'typings/', 'jspm_packages/', 'build/Release', '.lock-wscript', 'bower_components',
               '.grunt', '.nyc_output', '*.lcov', 'coverage', 'lib-cov', '*.pid.lock', '*.seed', '*.pid', 'pids',
               'logs', '*.log', 'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*', 'lerna-debug.log*',
               'node_modules', 'node_modules/', ],
    'spring_boot': [
        '.git', '*.iml', '*.ipr', '*.iws', '*.jar', '*.sw?', '*~', '.#*', '.*.md.html', '.DS_Store', '.classpath',
        '.factorypath', '.gradle', '.idea', '.metadata', '.project', '.recommenders', '.settings',
        '.springBeans', '/build', '/code', 'MANIFEST.MF', '_site/', 'activemq-data', 'bin', 'build', 'build.log',
        'dependency-reduced-pom.xml', 'dump.rdb', 'interpolated*.xml', 'lib/', 'manifest.yml', 'overridedb.*',
        'target', 'transaction-logs', '.flattened-pom.xml', 'secrets.yml', '.gradletasknamecache', '.sts4-cache']
}


def create_fandoghignore_file(project_name):
    exist_ignore_list = []
    if os.path.exists('.fandoghignore'):
        exist_ignore_list = [line.rstrip() for line in open('.fandoghignore')]
        os.remove('.fandoghignore')
    total_ignore_list = exist_ignore_list + project_type_ignore_dict.get(project_name)
    unique_ignore_list = set(total_ignore_list)
    with open('.fandoghignore', 'w+') as file:
        for item in unique_ignore_list:
            file.write("{}\n".format(item))


source.add_command(init)
source.add_command(run)
