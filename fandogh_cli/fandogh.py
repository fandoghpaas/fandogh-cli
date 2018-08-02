#!/usr/bin/env python

import click

from .domain_commands import domain
from .image_commands import image
from .service_commands import service
from .managed_service_commands import managed_service

from .base_commands import FandoghCommand
from .presenter import present
from .config import *
from .fandogh_client import *


@click.group("cli")
@click.version_option()
def base():
    pass


@click.command(cls=FandoghCommand)
@click.option('--username', prompt='username', help='your username')
@click.option('--password', prompt='password', help='your password', hide_input=True)
def login(username, password):
    """Login to fandogh server"""
    def handle_token():
        token_obj = get_token(username, password)
        get_user_config().set('token', token_obj['token'])

    message = present(lambda: handle_token(), post='Logged in successfully')
    click.echo(message)


base.add_command(login)
base.add_command(image)
base.add_command(service)
base.add_command(managed_service)
base.add_command(domain)

if __name__ == '__main__':

    base()
