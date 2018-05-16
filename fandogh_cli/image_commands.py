#!/usr/bin/env python
import click

from .base_commands import FandoghCommand
from .utils import login_required
from .presenter import present
from .config import *
from .fandogh_client import *
from time import sleep
from .workspace import build_workspace, cleanup_workspace


@click.group("image")
def image():
    pass


@click.command(cls=FandoghCommand)
@click.option('--name', prompt='image name', help='your image name')
@login_required
def init(name):
    token = load_token()
    response = create_image(name, token)
    persist_config(name)
    click.echo(response)


@click.command('list', cls=FandoghCommand)
@login_required
def list_images():
    token = load_token()
    table = present(lambda: get_images(token),
                    renderer='table',
                    headers=['Name', 'Creation Date'],
                    columns=['name', 'created_at'])

    click.echo(table)


def show_image_logs(app, version):
    token = load_token()
    if not app:
        config = load_config()
        app = config.app_name
    while True:
        response = get_image_build(app, version, token)
        click.clear()
        click.echo(response.get('logs'))
        if response.get('state') != 'BUILDING':
            break
        sleep(1)


@click.command('logs', cls=FandoghCommand)
@click.option('-i', '--image', 'image', help='The image name', default=None)
@click.option('--version', '-v', prompt='application version', help='your application version')
@login_required
def logs(image, version):
    show_image_logs(image, version)


@click.command(cls=FandoghCommand)
@click.option('--version', '-v', prompt='Image version', help='your image version')
@click.option('-d', 'detach', is_flag=True, default=False,
              help='detach terminal, by default the image build logs will be shown synchronously.')
def publish(version, detach):
    config = load_config()
    app_name = config.app_name
    workspace_path = build_workspace({})
    try:
        response = create_version(app_name, version, workspace_path)
        click.echo(response)
    finally:
        cleanup_workspace({})
    if detach:
        return
    else:
        show_image_logs(app_name, version)


@click.command(cls=FandoghCommand)
@click.option('--image', help='The image name', default=None)
def versions(image):
    if not image:
        config = load_config()
        image = config.app_name
    table = present(lambda: list_versions(image),
                    renderer='table',
                    headers=['version', 'state'],
                    columns=['version', 'state'])
    if len(table.strip()):
        click.echo(table)
    else:
        click.echo("There is no version available for this image")


image.add_command(init)
image.add_command(publish)
image.add_command(versions)
image.add_command(list_images)
image.add_command(logs)
