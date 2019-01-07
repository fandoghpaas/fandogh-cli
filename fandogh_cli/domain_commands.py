#!/usr/bin/env python
import click

from .fandogh_client.domain_client import *
from .base_commands import FandoghCommand
from .presenter import present
from .utils import format_text, TextStyle


@click.group('domain')
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


@click.command('add', cls=FandoghCommand)
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
                    headers=['Domain name', 'Verified', 'Certificate', 'Certificate status'],
                    columns=['name', 'verified', 'certificate', 'certificate_status'])

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
    command = format_text("fandogh domain details --name {}".format(name), TextStyle.OKBLUE)
    click.echo("Your request has been submitted and we are trying to get a certificate from Let's Encrypt for your"
               "domain, it might get a few minutes to complete.\n"
               "you can follow up your request using {}".format(command))


@click.command('details', cls=FandoghCommand)
@click.option('--name', 'name', prompt='Domain name', help='The domain name')
def details(name):
    """
    Get details of a domain
    """
    _display_domain_details(details_domain(name), clear=False)


@click.command('revoke-certificate', cls=FandoghCommand)
@click.option('--name', 'name', prompt='Domain name', help='The domain name')
def revoke_certificate(name):
    """
    Revoke a certificate
    """
    if click.confirm("You're about to revoke {} certificate and delete the secret, are you sure?".format(name)):
        result = delete_certificate(name)
        click.echo(result['message'])
    else:
        click.echo("Revoking certificate has been canceled")


@click.command('delete', cls=FandoghCommand)
@click.option('--name', '-n', 'name', prompt='Domain name', help='The domain name')
def delete(name):
    click.echo(delete_domain(name))


def _display_domain_details(domain_details, clear=True):
    if clear:
        click.clear()
    click.echo('Domain: {}'.format(format_text(domain_details['name'], TextStyle.HEADER)))
    if domain_details['verified'] is True:
        click.echo('\tVerified: {}'.format(format_text("Yes", TextStyle.OKGREEN)))
    else:
        click.echo('\tVerified: {}'.format(format_text("Yes", TextStyle.FAIL)))
    if domain_details.get('certificate', None) is None:
        click.echo("\tCertificate: {}".format(format_text("Not requested", TextStyle.OKBLUE)))
    else:
        certificate_details = domain_details['certificate'].get('details')
        status = certificate_details['status']
        if status == 'PENDING':
            click.echo("\tCertificate: {}".format(format_text('Trying to get a certificate', TextStyle.OKBLUE)))
        elif status == 'ERROR':
            click.echo("\tCertificate: {}".format(format_text('Getting certificate failed', TextStyle.FAIL)))
        elif status == 'READY':
            click.echo("\tCertificate: {}".format(format_text('Certificate is ready to use', TextStyle.OKGREEN)))
        else:
            click.echo('\tCertificate: {}'.format(format_text('Certificate status is unknown', TextStyle.WARNING)))

        info = certificate_details.get("info", False)
        if info:
            click.echo('\tInfo: {}'.format(format_text(info, TextStyle.WARNING)))
        if len(certificate_details.get('events', [])) > 0:
            click.echo("\tEvents:")
            for condition in certificate_details.get("events", []):
                click.echo("\t + {}".format(condition))


domain.add_command(add)
domain.add_command(list)
domain.add_command(verify)
domain.add_command(details)
domain.add_command(request_certificate)
domain.add_command(revoke_certificate)
domain.add_command(delete)
