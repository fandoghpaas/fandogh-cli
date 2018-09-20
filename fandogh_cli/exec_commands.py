import click

from .fandogh_client.exec_client import post_exec
from .fandogh_client import get_details
from .base_commands import FandoghCommand


@click.command("exec", cls=FandoghCommand)
@click.argument('command', nargs=1)
@click.option('-s', '--service', 'service', prompt='Service Name')
@click.option('-r', '--replica')
def exec(command, service, replica):
    """Exec management commands"""
    if not replica:
        details = get_details(service)
        pods = details['pods']
        pod_names = [pod['name'] for pod in pods]
        for pod_name in pod_names:
            click.echo('- {}'.format(pod_name))

        replica = click.prompt('Please choose one of the replicas above', type=click.Choice(pod_name))
    response = post_exec(replica, command)
    click.echo(response['message'])
