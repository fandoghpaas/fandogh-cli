#!/usr/bin/env python
import click

from .config import *
from .fandogh_client import *
from beautifultable import BeautifulTable

# TODO: better description for state field
from .workspace import build_workspace, cleanup_workspace


def please_login_first():
    click.echo('In order to see your apps you need to login first')


def create_table(columns):
    table = BeautifulTable()
    table.column_headers = columns
    table.row_separator_char = ''
    return table


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
        please_login_first()
        return
    response = create_app(name, token)
    persist_config(name)
    click.echo(response)


@click.command('list')
def list_apps():
    token = load_token()
    if not token:
        please_login_first()
        return
    response = get_apps(token)
    table = create_table(['Name', 'Create Date'])
    for item in response:
        table.append_row([item.get('name'), item.get('created_at')])
    click.echo(table)


app.add_command(init)


@click.command('inspect')
@click.option('--app', help='The application name', default=None)
@click.option('--version', prompt='application version', help='your application version')
def build_inspect(app, version):
    token = load_token()
    if not token:
        please_login_first()
        return

    if not app:
        config = load_config()
        app = config.get('app.name')
    response = get_build(app, version, token)
    click.echo(response.get('logs'))


@click.command()
@click.option('--version', prompt='application version', help='your application version')
def publish(version):
    config = load_config()
    app_name = config.get('app.name')
    workspace_path = build_workspace({})
    try:
        response = create_version(app_name, version, workspace_path)
        click.echo(response)
    finally:
        cleanup_workspace({})


@click.command('logs')
@click.option('--service_name', prompt="service name", help="Your service name")
def logs(service_name):
    token_obj = load_token()
    if token_obj is None:
        please_login_first()
        return
    click.echo(get_logs(service_name, token_obj))


@click.command()
@click.option('--app', help='The application name', default=None)
def versions(app):
    if not app:
        config = load_config()
        app = config.get('app.name')
    response = list_versions(app)
    table = create_table(['version', 'state'])
    for item in response:
        table.append_row([item.get('version'), item.get('state')])
    click.echo(table)


@click.command()
@click.option('--app', help='The image name', default=None)
@click.option('--version', prompt='The image version', help='The application version you want to deploy')
@click.option('--name', prompt='Your service name', help='Choose a unique name for your service')
def deploy(app, version, name):
    token = load_token()
    if not token:
        please_login_first()
        return
    if not app:
        config = load_config()
        app = config.get('app.name')
    response = deploy_service(app, version, name, token)
    click.echo('Your service deployed successfully.')
    click.echo('The service is accessible via following link:')
    click.echo(response.get('url'))


@click.command('list')
def service_list():
    token = load_token()
    if not token:
        please_login_first()
        return
    services = list_services(token)
    table = create_table(['name', 'start date', 'state'])
    for item in services:
        table.append_row([item.get('name'), item.get('start_date'), item.get('state')])
    click.echo(table)


@click.command('destroy')
@click.option('--name', 'service_name', prompt='Name of the service you want to destroy', )
def service_destroy(service_name):
    token = load_token()
    if not token:
        please_login_first()
        return
    response = destroy_service(service_name, token)
    click.echo(response)


@click.command()
@click.option('--username', prompt='username', help='your username')
@click.option('--password', prompt='password', help='your password', hide_input=True)
def login(username, password):
    token_obj = get_token(username, password)
    persist_token(token_obj)
    click.echo('Logged in successfully')


app.add_command(publish)
app.add_command(versions)
app.add_command(list_apps)
app.add_command(build_inspect)
service.add_command(deploy)
service.add_command(service_list)
service.add_command(service_destroy)
service.add_command(logs)
base.add_command(login)

if __name__ == '__main__':
    base()
