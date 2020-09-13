import click
from fandogh_cli.config import get_user_config, set_cluster_namespace, get_cluster_namespace

from fandogh_cli.fandogh_client.namespace_client import *
from .base_commands import FandoghCommand
from .utils import format_text, TextStyle


@click.group("namespace")
def namespace():
    """Namespace management commands"""


@click.command("list", cls=FandoghCommand)
def list():
    namespaces = list_namespaces()
    default_name_space = get_cluster_namespace()
    if default_name_space is None and len(namespaces) > 1:
        click.echo(format_text(
            'You already have more than 1 namespace and none selected as default namespace.\n Please select a namespace as default one',
            TextStyle.FAIL))
    click.echo('Your namespaces: ')
    for namespace in namespaces:
        message = ' * {}'.format(namespace['name'])
        if namespace['name'] == default_name_space:
            message += ' (active)'
        click.echo(message)


@click.command("active", cls=FandoghCommand)
@click.option('--name', '-n', 'name', prompt='Namespace name', help='Namespace name that should be default',
              default=None)
def active(name):
    namespaces = list_namespaces()
    if name in map(lambda n: n['name'], namespaces):
        click.echo("Setting the active namespace to {}".format(name))
        set_cluster_namespace(name)
    else:
        click.echo(format_text('Namespace not found', TextStyle.FAIL))


@click.command("status", cls=FandoghCommand)
def status():
    """list secrets filtered by type"""
    result = details_namespace()

    def print_value(name, current, total):
        click.echo("{}: {} of {}".format(
            format_text(name, TextStyle.HEADER),
            format_text(current, TextStyle.OKGREEN),
            format_text(total, TextStyle.OKGREEN),
        ))

    click.echo('Namespace: {}'.format(result['name']))
    print_value('Service count', result['current_used_resources'].get('service_count'),
                result['quota'].get('service_limit',
                                    'N/A'))
    print_value(
        name='Memory',
        current="{} MB".format(result['current_used_resources'].get('memory_usage')),
        total="{} MB".format(result['quota'].get('memory_limit', 'N/A'))
    )

    print_value(
        name='Volume',
        current="{} GB".format(result['current_used_resources'].get('volume_usage')),
        total="{} GB".format(result['quota'].get('volume_limit', 'N/A'))
    )
    # print_value('CPU', result['current_used_resources'].get('cpu_usage'), result['quota'].get('cpu_limit', 'N/A'))


namespace.add_command(list)
namespace.add_command(active)
namespace.add_command(status)
