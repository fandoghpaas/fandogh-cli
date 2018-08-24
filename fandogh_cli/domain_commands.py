#!/usr/bin/env python
import click
import time

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
                    headers=['Domain name', 'Verified', 'Certificate'],
                    columns=['name', 'verified', 'certificate'])

    click.echo(table)


@click.command('verify', cls=FandoghCommand)
@click.option('--name', 'name', prompt='Domain name', help='The domain name')
def verify(name):
    """
    Verify domain ownership
    """
    _verify_ownership(name)


@click.command('request-certificate', cls=FandoghCommand)
@click.option('--name', 'name', prompt='Domain name', help='The domain name')
def request_certificate(name):
    """
    Request a Let's Encrypt SSL/TLS Certificate for a domain
    """
    create_certificate(name)
    while True:
        details = details_domain(name)
        _display_domain_details(details)
        if details['certificate']['status'] != "PENDING":
            break
        time.sleep(2)


@click.command('details', cls=FandoghCommand)
@click.option('--name', 'name', prompt='Domain name', help='The domain name')
def details(name):
    """
    Get details of a domain
    """
    _display_domain_details(details_domain(name), clear=False)


def _display_domain_details(domain_details, clear=True):
    if clear:
        click.clear()
    click.echo("Domain: {}".format(format_text(domain_details['name'], TextStyle.HEADER)))
    if domain_details['verified'] is True:
        click.echo("\tVerified: {}".format(format_text("Yes", TextStyle.OKGREEN)))
    else:
        click.echo("\tVerified: {}".format(format_text("Yes", TextStyle.FAIL)))
    if domain_details['certificate'] is None:
        click.echo("\tCertificate: {}".format(format_text("Not requested", TextStyle.OKBLUE)))
    else:
        status = domain_details['certificate']['status']
        if status == "PENDING":
            click.echo("\tCertificate: {}".format(format_text("Trying to get a certificate", TextStyle.OKBLUE)))
        elif status == "ERROR":
            click.echo("\tCertificate: {}".format(format_text("Getting certificate failed", TextStyle.FAIL)))
            info = domain_details['certificate'].get("info", False)
            if info:
                click.echo("\tInfo: {}".format(format_text(info, TextStyle.FAIL)))
        elif status == "READY":
            click.echo("\tCertificate: {}".format(format_text("Certificate is ready to use", TextStyle.OKGREEN)))
        else:
            click.echo("\tCertificate: {}".format(format_text("Certificate status is unknown", TextStyle.WARNING)))
            info = domain_details['certificate'].get("info", False)
            if info:
                click.echo("\tInfo: {}".format(format_text(info, TextStyle.WARNING)))


domain.add_command(add)
domain.add_command(list)
domain.add_command(verify)
domain.add_command(details)
domain.add_command(request_certificate)
