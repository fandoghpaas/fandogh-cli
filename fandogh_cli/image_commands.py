#!/usr/bin/env python
import click
from .base_commands import FandoghCommand
from .utils import format_text, TextStyle
from .presenter import present
from .config import *
from .fandogh_client import *
from time import sleep
from .workspace import Workspace
import sys


@click.group("image")
def image():
    """
    Image management commands
    """


def init_image(name):
    try:
        response = create_image(name)
    except FandoghBadRequest as exp:
        if name in {x['name'].split("/")[1] if '/' in x['name'] else x['name'] for x in get_images()}:
            click.echo(
                format_text("You already have an image named '{}', "
                            "choose another name if this is not the same workspace".format(name), TextStyle.WARNING)
            )
        else:
            raise
    except Exception:
        raise
    else:
        click.echo(response['message'])
    get_project_config().set('image.name', name)


@click.command("init", cls=FandoghCommand)
@click.option('--name', prompt='image name', help='your image name')
def init(name):
    """
    Upload project on the server
    """
    init_image(name)


@click.command('list', cls=FandoghCommand)
def list_images():
    """
    List images
    """
    table = present(lambda: get_images(),
                    renderer='table',
                    headers=['Name', 'Last Version', 'Last Version Publication Date'],
                    columns=['name', 'last_version_version', 'last_version_date'])
    if table:
        click.echo(table)
    else:
        click.echo('\nYou have no images to show, why don\'t you try building one? \n'
                   'have fun and follow the link below:\n')
        click.echo('https://docs.fandogh.cloud/docs/images.html\n')


def show_image_logs(image_name, version):
    image_offset = 0

    if not image_name:
        image_name = get_project_config().get('image.name')
    while True:
        response = get_image_build(image_name, version, image_offset)

        image_offset = response.get('lines_count')
        logs = response.get('logs')

        if logs.strip():
            click.echo(response.get('logs'))
        if response.get('state') != 'BUILDING' and \
                response.get('state') != 'PENDING':
            break
        sleep(1)
    if response.get('state') == 'FAILED':
        sys.exit(201)


@click.command('logs', cls=FandoghCommand)
@click.option('-i', '--image', 'image', prompt='Image name', help='The image name',
              default=lambda: get_project_config().get('image.name'))
@click.option('--version', '-v', prompt='Image version', help='your image version')
def logs(image, version):
    """
    Display image log
    """
    show_image_logs(image, version)


@click.command("publish", cls=FandoghCommand)
@click.option('--version', '-v', prompt='Image version', help='your image version')
@click.option('-d', 'detach', is_flag=True, default=False,
              help='detach terminal, by default the image build logs will be shown synchronously.')
def publish(version, detach):
    """
    Publish new version of image
    """
    image_name = get_project_config().get('image.name')
    if not image_name:
        click.echo("It looks you are either not in a fandogh workspace or you didn't init yet.")
        click.echo("If you are sure that you are in the right directory then please input the image name.")
        image_name = click.prompt("Image name")
        if image_name:
            init_image(image_name)
        else:
            return
    workspace = Workspace()

    if not workspace.has_docker_file:
        click.echo("In order to publish your image you must have a Dockerfile in the current directory")
        return
    if workspace.zip_file_size > max_workspace_size:
        click.echo(format_text(
            "The workspace size should not be larger than {}MB, its {}MB.".format(max_workspace_size,
                                                                                  round(workspace.zip_file_size, 2)),
            TextStyle.WARNING
        ))

        if not workspace.has_docker_ignore:
            click.echo(format_text(
                "[perhaps you may be able to take advantage of '.dockerignore' "
                "to reduce your worksspace size, check documentation for .dockerignore at: "
                "https://docs.docker.com/engine/reference/builder/#dockerignore-file]", TextStyle.BOLD
            ))

    bar = click.progressbar(length=int(workspace.zip_file_size_kb), label='Uploading the workspace')
    shared_values = {'diff': 0}

    def monitor_callback(monitor):
        progress = monitor.bytes_read - shared_values['diff']
        bar.update(progress)
        shared_values['diff'] += progress

    try:
        response = create_version(image_name, version, str(workspace), monitor_callback)
        bar.render_finish()
        click.echo(response['message'])
    finally:
        workspace.clean()
    if detach:
        return
    else:
        show_image_logs(image_name, version)


@click.command("versions", cls=FandoghCommand)
@click.option('-i', '--image', 'image', prompt='Image name', help='The image name',
              default=lambda: get_project_config().get('image.name'))
def versions(image):
    """
    List published versions of this image
    """
    if not image:
        image = get_project_config().get('image.name')
    table = present(lambda: list_versions(image),
                    renderer='table',
                    headers=['version', 'size', 'state'],
                    columns=['version', 'size', 'state'])
    if len(table.strip()):
        click.echo(table)
    else:
        click.echo("There is no version available for '{}'".format(image))


@click.command("delete", cls=FandoghCommand)
@click.option('-i', '--image', '--name', 'image', prompt='Image name', help='The image name',
              default=lambda: get_project_config().get('image.name'))
def delete(image):
    click.echo(delete_image(image)['message'])


image.add_command(init)
image.add_command(publish)
image.add_command(versions)
image.add_command(list_images)
image.add_command(logs)
image.add_command(delete)
