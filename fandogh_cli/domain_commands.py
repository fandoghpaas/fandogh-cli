#!/usr/bin/env python
import click

from .fandogh_client.domain_client import *
from .base_commands import FandoghCommand
from .presenter import present
from .utils import format_text, TextStyle


@click.group("domain")
def domain():
    """
    Domain management commands
    """


def _verify_ownership(name):
    response = verify_domain(name)
    if response['verified']:
        click.echo('Domain {} ownership verified successfully.'.format(name))
    else:
        click.echo('It seems the key is not set correctly as value of a TXT record for domain {}.'.format(name))
        click.echo(
            'please add a TXT record with the following key to your name server in order to help us verify your ownership.')
        click.echo('Key:' + format_text(response['verification_key'], TextStyle.OKGREEN))
    return response


@click.command("add", cls=FandoghCommand)
@click.option('--name', prompt='domain name', help='your domain name')
def add(name):
    """
    Upload project on the server
    """
    response = add_domain(name)
    if response['verified'] is True:
        click.echo(format_text("Your domain has been added and doesn't need verification", TextStyle.OKGREEN))
        return
    click.echo('The domain has been added.')
    click.echo('Now you just need to help us that you have ownership of this domain.')
    click.echo(
        'please add a TXT record with the following key to your name server in order to help us verify your ownership.')
    click.echo('Key:' + format_text(response['verification_key'], TextStyle.OKGREEN))
    while not response['verified']:
        confirmed = click.confirm('I added the record')
        if confirmed:
            response = _verify_ownership(name)
        else:
            click.echo('You can verify the ownership later on')
            click.echo('Once you added the record please run the following command')
            click.echo(format_text('fandogh domain verify --name={}'.format(name), TextStyle.BOLD))
            return


@click.command('list', cls=FandoghCommand)
def list():
    """
    List images
    """
    table = present(lambda: list_domains(),
                    renderer='table',
                    headers=['Domain name', 'Verified'],
                    columns=['name', 'verified'])

    click.echo(table)


@click.command('verify', cls=FandoghCommand)
@click.option('--name', 'name', prompt='Domain name', help='The domain name')
def verify(name):
    """
    Verify domain ownership
    """
    _verify_ownership(name)


domain.add_command(add)
domain.add_command(list)
domain.add_command(verify)
