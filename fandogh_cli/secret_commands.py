import click

from fandogh_cli.fandogh_client.secrets_client import list_secret, create_secret
from .fandogh_client import *
from .config import get_project_config
from .presenter import present
from .utils import format_text, TextStyle
from .base_commands import FandoghCommand


@click.group("secret")
def secret():
    """Service management commands"""


@click.command("list", cls=FandoghCommand)
@click.option('--type', '-t', 'secret_type', help='type of secret to list', default="dockerconfigjson")
def list(secret_type):
    """list secrets filtered by type"""
    data = list_secret(secret_type)
    print(data)


@click.command("create", cls=FandoghCommand)
@click.option('--name', '-n', 'secret_name', help='a unique name for secret', prompt='Name for the secret', )
@click.option('--type', '-t', 'secret_type', help='type of secret to list', prompt='Type of the secret',
              default="REGISTRY_SECRET")
@click.option('--field', '-f', 'fields', help='fields to store in secret', multiple=True)
def create(secret_type, fields, secret_name):
    """list secrets filtered by type"""
    create_secret(secret_name, secret_type, fields, )


secret.add_command(list)
secret.add_command(create)
