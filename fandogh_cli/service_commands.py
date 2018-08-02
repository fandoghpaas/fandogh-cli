import click
from .fandogh_client import *
from .config import get_project_config
from .presenter import present
from .utils import format_text, TextStyle
from .base_commands import FandoghCommand


@click.group("service")
def service():
    """Service management commands"""


@click.command("deploy", cls=FandoghCommand)
@click.option('--image', help='The image name', default=None)
@click.option('--version', '-v', prompt='The image version', help='The image version you want to deploy')
@click.option('--name', prompt='Your service name', help='Choose a unique name for your service')
@click.option('--env', '-e', 'envs', help='Environment variables (format: VARIABLE_NAME=VARIABLE_VALUE)', multiple=True)
@click.option('--hosts', '-h', 'hosts', help='Custom hosts that service should be accessible through', multiple=True)
@click.option('--port', '-p', 'port', help='The service port that will be exposed on port 80 to worldwide', default=80)
@click.option('--internal', help='This is an internal service like a DB and the port should '
                                 'not be exposed publicly', default=False, is_flag=True)
def deploy(image, version, name, port, envs, hosts, internal):
    """Deploy service"""
    if not image:
        image = get_project_config().get('image.name')
        if not image:
            click.echo(format_text('please declare the image name', TextStyle.FAIL), err=True)

    deployment_result = deploy_service(image, version, name, envs, hosts, port, internal)
    message = "\nCongratulation, Your service is running ^_^\n"
    if str(deployment_result['service_type']).lower() == "external":
        message += "Your service is accessible using the following URLs:\n{}".format(
            "\n".join([" - {}".format(url) for url in deployment_result['urls']])
        )
    else:
        message += """
Since your service is internal, it's not accessible from outside your fandogh private network, 
but other services inside your private network will be able to find it using it's name: '{}'
        """.strip().format(
            deployment_result['name']
        )
    click.echo(message)


@click.command('list', cls=FandoghCommand)
@click.option('-a', 'show_all', is_flag=True, default=False,
              help='show all the services regardless if it\'s running or not')
def service_list(show_all):
    """List available service for this image"""
    table = present(lambda: list_services(show_all),
                    renderer='table',
                    headers=['Service Name', 'URL', 'Service Type', 'Started at', 'State'],
                    columns=['name', 'url', 'service_type', 'start_date', 'state'])
    click.echo(table)


@click.command('destroy', cls=FandoghCommand)
@click.option('--name', 'service_name', prompt='Name of the service you want to destroy', )
def service_destroy(service_name):
    """Destroy service"""
    message = present(lambda: destroy_service(service_name))
    click.echo(message)


@click.command('logs', cls=FandoghCommand)
@click.option('--name', 'service_name', prompt='service_name', help="Service name")
def service_logs(service_name):
    """Display service logs"""
    logs = present(lambda: get_logs(service_name))
    click.echo(logs)


service.add_command(deploy)
service.add_command(service_list)
service.add_command(service_destroy)
service.add_command(service_logs)
