#!/usr/bin/env python
import click

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
def init(name):
    token = load_token()
    if not token:
        click.echo('In order to see your apps you need to login first')
        return
    response = create_app(name, token)
    persist_config(name)
    click.echo(response)


@click.command('list')
def list_apps():
    token = load_token()
    if not token:
        click.echo('In order to see your apps you need to login first')
        return

    table = present(lambda: get_apps(token),
                    renderer='table',
                    headers=['Name', 'Create Date'],
                    columns=['name', 'created_at'])

    click.echo(table)


app.add_command(init)


@click.command('inspect')
@click.option('--app', help='The application name', default=None)
@click.option('--version', '-v', prompt='application version', help='your application version')
def build_inspect(app, version):
    token = load_token()
    if not token:
        click.echo('In order to see your apps you need to login first')
        return

    if not app:
        config = load_config()
        app = config.get('app.name')
    response = get_build(app, version, token)
    click.echo(response.get('logs'))


@click.command()
@click.option('--version', '-v', prompt='application version', help='your application version')
def publish(version):
    config = load_config()
    app_name = config.get('app.name')
    workspace_path = build_workspace({})
    try:
        response = create_version(app_name, version, workspace_path)
        click.echo(response)
    finally:
        cleanup_workspace({})


@click.command()
@click.option('--app', help='The application name', default=None)
def versions(app):
    if not app:
        config = load_config()
        app = config.get('app.name')
    table = present(lambda: list_versions(app),
                    renderer='table',
                    headers=['version', 'state'],
                    columns=['version', 'state'])
    click.echo(table)


@click.command()
@click.option('--app', help='The image name', default=None)
@click.option('--version', '-v', prompt='The image version', help='The application version you want to deploy')
@click.option('--name', prompt='Your service name', help='Choose a unique name for your service')
@click.option('--env', '-e', 'envs', help='Environment variables (format: VARIABLE_NAME=VARIABLE_VALUE)', multiple=True)
def deploy(app, version, name, envs):
    token = load_token()
    if not token:
        click.echo('In order to see your services you need to login first')
        return
    if not app:
        config = load_config()
        app = config.get('app.name')

    pre = '''Your service deployed successfully.
The service is accessible via following link:
'''
    message = present(lambda: deploy_service(app, version, name, envs, token), pre=pre, field='url')
    click.echo(message)


@click.command('list')
def service_list():
    token = load_token()
    if not token:
        click.echo('In order to see your services you need to login first')
        return

    table = present(lambda: list_services(token),
                    renderer='table',
                    headers=['name', 'start date', 'state'],
                    columns=['name', 'start_date', 'state'])
    click.echo(table)


@click.command('destroy')
@click.option('--name', 'service_name', prompt='Name of the service you want to destroy', )
def service_destroy(service_name):
    token = load_token()
    if not token:
        click.echo('In order to see your services you need to login first')
        return
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
base.add_command(login)

if __name__ == '__main__':
    base()
