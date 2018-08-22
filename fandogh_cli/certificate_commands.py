import click
from fandogh_cli.fandogh_client.certificate_client import detail_certificate, create_certificate
from .utils import format_text, TextStyle
from .base_commands import FandoghCommand
import time


@click.group("ssl")
def ssl():
    """SSL Certificate management commands"""


def _display_domain_details(domain_details, clear=True):
    # {'created_at': '2018-08-22T20:49:15.687698Z', 'domain_name': 'foo', 'state': 'PENDING', 'id': 4}
    if clear:
        click.clear()
    click.echo("Domain name: " + format_text(domain_details.get("domain_name", "---"), TextStyle.HEADER))
    if domain_details.get("state") == "ERROR":
        state_color = TextStyle.FAIL
    elif domain_details.get("state") == "READY":
        state_color = TextStyle.OKGREEN
    else:
        state_color = TextStyle.OKBLUE
    click.echo("   State: " + format_text(domain_details.get("state", "UNKNOWN"), state_color))
    click.echo("   Created at: " + format_text(domain_details.get("created_at", "UNKNOWN"), TextStyle.BOLD))


@click.command("details", cls=FandoghCommand)
@click.option('--domain', '-d', 'domain_name', help='domain name', prompt='Domain name')
def details(domain_name):
    """Display details of a certificate"""
    _display_domain_details(detail_certificate(domain_name), clear=False)


@click.command("create", cls=FandoghCommand)
@click.option('--domain', '-d', 'domain_name', help='domain name', prompt='Domain name')
def create(domain_name):
    """Request a certificate for a domain"""
    result = create_certificate(domain_name)
    while True:
        _display_domain_details(result)
        time.sleep(5)
        result = detail_certificate(domain_name)
        if result['state'] != "PENDING":
            break


ssl.add_command(create)
ssl.add_command(details)
