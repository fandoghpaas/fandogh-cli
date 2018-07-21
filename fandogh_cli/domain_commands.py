#!/usr/bin/env python
import click

from .base_commands import FandoghCommand
from .config import *
from .fandogh_client import *
from .presenter import present
from .utils import login_required, format_text, TextStyle


@click.group("domain")
def domain():
    """
    Domain management commands
    """
    pass


@click.command("add", cls=FandoghCommand)
@click.option('--name', prompt='domain name', help='your domain name')
@login_required
def add(name):
    """
    Upload project on the server
    """
    token = get_user_config().get('token')
    try:
        response = add_domain(name, token)
    except FandoghBadRequest as exp:
        if name in {x['name'].split("/")[1] if '/' in x['name'] else x['name'] for x in get_images(token)}:
            click.echo(
                format_text("You already have an image named '{}', "
                            "choose another name if this is not the same workspace".format(name), TextStyle.WARNING)
            )
        else:
            raise
    except Exception:
        raise
    else:
        click.echo(response)

    get_project_config().set('image.name', name)


@click.command('list', cls=FandoghCommand)
@login_required
def list():
    """
    List images
    """
    token = get_user_config().get('token')
    table = present(lambda: get_images(token),
                    renderer='table',
                    headers=['Name', 'Creation Date'],
                    columns=['name', 'created_at'])

    click.echo(table)


@click.command('verify', cls=FandoghCommand)
@click.option('--name', 'name', prompt='Domain name', help='The domain name')
@login_required
def verify(name):
    """
    Verify domain ownership
    """
    token = get_user_config().get('token')
    result = verify_domain(name, token)
    if result['verified']:
        click.echo('Domain {} ownership verified successfully.'.format(name))



domain.add_command(add)
domain.add_command(list)
domain.add_command(verify)
