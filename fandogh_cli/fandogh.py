#!/usr/bin/env python
import click

from config import persist_config, load_config
from fandogh_client import create_app, create_version, list_versions, deploy_service, list_services
from beautifultable import BeautifulTable


# TODO: better description for state field
from workspace import build_workspace


def create_table(columns):
    table = BeautifulTable()
    table.column_headers = columns
    table.row_separator_char = ''
    return table


@click.group("cli")
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
    response = create_app(name)
    persist_config(name)
    click.echo(response)


app.add_command(init)


@click.command()
@click.option('--version', prompt='application version', help='your application version')
def publish(version):
    config = load_config()
    app_name = config.get('app.name')
    workspace_path = build_workspace({})
    response = create_version(app_name, version, workspace_path)
    click.echo(response)


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
@click.option('--app', help='The application name', default=None)
@click.option('--version', prompt='application version', help='The application version you want to deploy')
def deploy(app, version):
    if not app:
        config = load_config()
        app = config.get('app.name')
    response = deploy_service(app, version)
    click.echo(response)


@click.command('list')
def service_list():
    services = list_services()
    table = create_table(['name', 'start date', 'state'])
    for item in services:
        table.append_row([item.get('name'), item.get('start_date'), item.get('state')])
    click.echo(table)

app.add_command(publish)
app.add_command(versions)
service.add_command(deploy)
service.add_command(service_list)

if __name__ == '__main__':
    base()