import click
from fandogh_cli.fandogh_client.namespace_client import details_namespace
from .presenter import present
from .base_commands import FandoghCommand
from .utils import format_text, TextStyle


@click.group("namespace")
def namespace():
    """Namespace management commands"""


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
    # print_value('CPU', result['current_used_resources'].get('cpu_usage'), result['quota'].get('cpu_limit', 'N/A'))


namespace.add_command(status)
