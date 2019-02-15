import click
from fandogh_cli.fandogh_client.secrets_client import list_secret, create_secret, put_secret, delete_secret
from .utils import format_text, TextStyle
from .presenter import present
from .base_commands import FandoghCommand


@click.group("secret")
def secret():
    """Secret management commands"""


@click.command("list", cls=FandoghCommand)
def list():
    """list secrets filtered by type"""
    table = present(lambda: list_secret(),
                    renderer='table',
                    headers=['Name', 'Secret Type', 'Created at'],
                    columns=['name', 'type', 'created_at'])
    if len(table.strip()):
        click.echo(table)
    else:
        click.echo(format_text("There is no secret available", TextStyle.WARNING))


@click.command("create", cls=FandoghCommand)
@click.option('--name', '-n', 'secret_name', help='a unique name for secret', prompt='Name for the secret')
@click.option('--type', '-t', 'secret_type', help='type of secret to list', prompt="Secret Type")
@click.option('--field', '-f', 'fields', help='fields to store in secret', multiple=True)
def create(secret_type, fields, secret_name):
    """Create new secret"""
    result = create_secret(secret_name, secret_type, fields, )
    click.echo(result['message'])


@click.command("put", cls=FandoghCommand)
@click.option('--name', '-n', 'secret_name', help='a unique name for secret', prompt='Name for the secret')
@click.option('--type', '-t', 'secret_type', help='type of secret to list', prompt="Secret Type")
@click.option('--field', '-f', 'fields', help='fields to store in secret', multiple=True)
def put(secret_type, fields, secret_name):
    """Put new values for a secret """
    result = put_secret(secret_name, secret_type, fields)
    click.echo(result['message'])


@click.command("delete", cls=FandoghCommand)
@click.option('--name', '-n', 'secret_name', help='name of the secret to delete', prompt='Name for the secret')
def delete(secret_name):
    """Delete a secret by name"""
    if click.confirm("You are about to delete a secret named '{}', you cannot undo this action. Are sure?".format(
            secret_name
    )):
        result = delete_secret(secret_name)
        click.echo(result['message'])


secret.add_command(list)
secret.add_command(put)
secret.add_command(create)
secret.add_command(delete)
