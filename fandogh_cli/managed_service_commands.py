import click

from .fandogh_client import *
from .utils import login_required
from .config import get_project_config, get_user_config
from .presenter import present
from .base_commands import FandoghCommand


@click.group("managed-service")
def managed_service():
    """Service management commands"""
    pass


@click.command("deploy", cls=FandoghCommand)
@click.argument('name', nargs=1)
@click.argument('version', nargs=1)
@click.option('-c', '--configuration', 'config', help='Managed service configuration (format: VARIABLE_NAME=VARIABLE_VALUE)', multiple=True)
@login_required
def deploy(name, version, config):
    """Deploy Managed Service"""
    token = get_user_config().get('token')
    response = deploy_managed_service(name, version, config, token)
    click.echo(response.get('message'))


managed_service.add_command(deploy)
