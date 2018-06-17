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
@click.option('-c', '--configuration', 'config', 'Managedd service dependent configuration (format: VARIABLE_NAME=VARIABLE_VALUE)', multiple=True)
@login_required
def deploy(name, version, config):
    click.echo('deploying... {} {}'.format(name, version))


managed_service.add_command(deploy)
