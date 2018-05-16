#!/usr/bin/env python

import click

from fandogh_cli.image_commands import image
from .base_commands import FandoghCommand
from .utils import login_required
from .presenter import present
from .config import *
from .fandogh_client import *

# TODO: better description for state field





@click.group("cli")
@click.version_option()
def base():
    pass





@click.group("service")
def service():
    pass


base.add_command(image)
base.add_command(service)





@click.command('logs', cls=FandoghCommand)
@click.option('--service_name', prompt='service_name', help="Service name")
@login_required
def service_logs(service_name):
    token_obj = load_token()
    logs = present(lambda: get_logs(service_name, token_obj))
    click.echo(logs)


@click.command(cls=FandoghCommand)
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


@click.command('list', cls=FandoghCommand)
@click.option('-a', 'show_all', is_flag=True, default=False,
              help='show all the services regardless if it\'s running or not')
@login_required
def service_list(show_all):
    token = load_token()
    table = present(lambda: list_services(token, show_all),
                    renderer='table',
                    headers=['name', 'start date', 'state'],
                    columns=['name', 'start_date', 'state'])
    click.echo(table)


@click.command('destroy', cls=FandoghCommand)
@login_required
@click.option('--name', 'service_name', prompt='Name of the service you want to destroy', )
def service_destroy(service_name):
    token = load_token()
    message = present(lambda: destroy_service(service_name, token))
    click.echo(message)


@click.command(cls=FandoghCommand)
@click.option('--username', prompt='username', help='your username')
@click.option('--password', prompt='password', help='your password', hide_input=True)
def login(username, password):
    def handle_token():
        token_obj = get_token(username, password)
        persist_token(token_obj)

    message = present(lambda: handle_token(), post='Logged in successfully')
    click.echo(message)



service.add_command(deploy)
service.add_command(service_list)
service.add_command(service_destroy)
service.add_command(service_logs)

base.add_command(login)

if __name__ == '__main__':
    base()
