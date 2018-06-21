import click

from .fandogh_client import *
from .utils import login_required
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
    token = get_user_config().get('token')
    response = deploy_managed_service(name, version, configs, token)
    click.echo(response.get('message'))


managed_service.add_command(deploy)
