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
    print(result)

    def transform_response(response: dict):
        current_used_resources = response['current_used_resources']
        transformed_result = []
        for key, value in current_used_resources.get('deployments', {}).items():
            transformed_result.append({
                "name": key,
                "memory": value.get('memory', 'N/A'),
                "cpu": value.get('cpu', 'N/A'),

            })
        transformed_result.append(
            {
                "name": "Total",
                "memory": current_used_resources.get('memory', 'N/A'),
                "cpu": current_used_resources.get('cpu', 'N/A'),
            })
        return transformed_result

    click.echo("{}: {}".format(
        format_text("Name", TextStyle.HEADER),
        format_text(result['name'], TextStyle.OKGREEN)
    ))
    click.echo("{}: {}".format(
        format_text("Memory Limit", TextStyle.HEADER),
        format_text(result.get('quota', {}).get("memory_limit", "N/A"), TextStyle.OKGREEN)
    ))

    click.echo(present(lambda: transform_response(result),
                       renderer='table',
                       headers=['Service', 'Memory', 'CPU'],
                       columns=['name', 'memory', 'cpu']))


namespace.add_command(status)
