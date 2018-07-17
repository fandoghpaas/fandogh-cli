import click

from .fandogh_client import *
from .utils import login_required, format_text, TextStyle
from .config import get_user_config
from .base_commands import FandoghCommand


@click.group("managed-service")
def managed_service():
    """Service management commands"""
    pass


@click.command("deploy", cls=FandoghCommand)
@click.argument('name', nargs=1)
@click.argument('version', nargs=1)
@click.option('-c', '--config', 'configs', help='Managed service configuration (format: VARIABLE_NAME=VARIABLE_VALUE)',
              multiple=True)
@login_required
def deploy(name, version, configs):
    """Deploy Managed Service"""
    try:
        token = get_user_config().get('token')
        response = deploy_managed_service(name, version, configs, token)
        click.echo(response.get('message'))
    except FandoghBadRequest:
        click.echo(format_text(
            "please check `fandogh managed-service help` for more information "
            "regarding fandogh managed services",
            TextStyle.FAIL))
        raise



@click.command("help", cls=FandoghCommand)
@login_required
def help():
    """Display Help for Managed Service"""
    token = get_user_config().get('token')
    managed_services = help_managed_service(token)
    click.echo(format_text(
        "List of Fandogh managed services:", TextStyle.OKBLUE
    ))
    for managed_service in managed_services:
        click.echo("\t* Service name: {}".format(managed_service['name']))
        for parameter_name, description in managed_service['options'].items():
            click.echo("\t\t. {}:\t{}".format(parameter_name.ljust(20), description))


managed_service.add_command(help)
managed_service.add_command(deploy)
