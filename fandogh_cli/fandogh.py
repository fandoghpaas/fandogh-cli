#!/usr/bin/env python
from time import sleep

import click

from fandogh_cli.utils import login_required, do_every
from .presenter import present
from .config import *
from .fandogh_client import *

# TODO: better description for state field
from .workspace import build_workspace, cleanup_workspace


@click.group("cli")
@click.version_option()
def base():
    pass


@click.group("app")
def app():
    pass


@click.group("service")
def service():
    pass


base.add_command(app)
base.add_command(service)


@click.command()
@click.option('--name', prompt='application name', help='your application name')
@login_required
def init(name):
    token = load_token()
    response = create_app(name, token)
    persist_config(name)
    click.echo(response)


@click.command('list')
@login_required
def list_apps():
    token = load_token()
    table = present(lambda: get_apps(token),
                    renderer='table',
                    headers=['Name', 'Create Date'],
                    columns=['name', 'created_at'])

    click.echo(table)


app.add_command(init)


def show_build_logs(app, version):
    token = load_token()
    if not app:
        config = load_config()
        app = config.app_name
    while True:
        response = get_build(app, version, token)
        click.clear()
        click.echo(response.get('logs'))
        if response.get('state') != 'BUILDING':
            break
        sleep(1)


@click.command('inspect')
@click.option('--app', help='The application name', default=None)
@click.option('--version', '-v', prompt='application version', help='your application version')
@login_required
def build_inspect(app, version):
    show_build_logs(app, version)


@click.command()
@click.option('--version', '-v', prompt='application version', help='your application version')
@click.option('-d', 'detach', is_flag=True, default=False, help='detach terminal, by default the image build logs will be shown synchronously.')
def publish(version, detach):
    config = load_config()
    app_name = config.app_name
    workspace_path = build_workspace({})
    try:
        response = create_version(app_name, version, workspace_path)
        click.echo(response)
    finally:
        cleanup_workspace({})
    if detach:
        return
    else:
        show_build_logs(app_name, version)


@click.command()
@click.option('--app', help='The application name', default=None)
def versions(app):
    if not app:
        config = load_config()
        app = config.app_name
    table = present(lambda: list_versions(app),
                    renderer='table',
                    headers=['version', 'state'],
                    columns=['version', 'state'])
    click.echo(table)


@click.command('logs')
@click.option('--service_name', prompt='service_name', help="Service name")
@login_required
def service_logs(service_name):
    token_obj = load_token()
    logs = present(lambda: get_logs(service_name, token_obj))
    click.echo(logs)


@click.command()
@click.option('--app', help='The image name', default=None)
@click.option('--version', '-v', prompt='The image version', help='The application version you want to deploy')
@click.option('--name', prompt='Your service name', help='Choose a unique name for your service')
@click.option('--env', '-e', 'envs', help='Environment variables (format: VARIABLE_NAME=VARIABLE_VALUE)', multiple=True)
@login_required
def deploy(app, version, name, envs):
    token = load_token()
    if not app:
        config = load_config()
        app = config.app_name
        if not app:
            click.echo('please declare the application name', err=True)

    pre = '''Your service deployed successfully.
The service is accessible via following link:
'''
    message = present(lambda: deploy_service(app, version, name, envs, token), pre=pre, field='url')
    click.echo(message)


@click.command('list')
@login_required
def service_list():
    token = load_token()
    table = present(lambda: list_services(token),
                    renderer='table',
                    headers=['name', 'start date', 'state'],
                    columns=['name', 'start_date', 'state'])
    click.echo(table)


@click.command('destroy')
@click.option('--name', 'service_name', prompt='Name of the service you want to destroy', )
@login_required
def service_destroy(service_name):
    token = load_token()
    message = present(lambda: destroy_service(service_name, token))
    click.echo(message)


@click.command()
@click.option('--username', prompt='username', help='your username')
@click.option('--password', prompt='password', help='your password', hide_input=True)
def login(username, password):
    def handle_token():
        token_obj = get_token(username, password)
        persist_token(token_obj)

    message = present(lambda: handle_token(), post='Logged in successfully')
    click.echo(message)


app.add_command(publish)
app.add_command(versions)
app.add_command(list_apps)
app.add_command(build_inspect)
service.add_command(deploy)
service.add_command(service_list)
service.add_command(service_destroy)
service.add_command(service_logs)

base.add_command(login)

if __name__ == '__main__':
    base()
