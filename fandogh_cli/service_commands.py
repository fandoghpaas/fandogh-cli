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
@click.option('--internal-port', '-m', 'internal_ports', help='Expose other ports internally', multiple=True)
@click.option('--hosts', '-h', 'hosts', help='Custom hosts that service should be accessible through', multiple=True)
@click.option('--port', '-p', 'port', help='The service port that will be exposed on port 80 to worldwide', default=80)
@click.option('--registry-secret', '-s', 'registry_secret',
              help='Name of the secret containing require credentials to access registry', default=None)
@click.option('--internal', help='This is an internal service like a DB and the port should '
                                 'not be exposed publicly', default=False, is_flag=True)
@click.option('--image-pull-policy', 'image_pull_policy', default='IfNotPresent')
def deploy(image, version, name, port, envs, hosts, internal, registry_secret, image_pull_policy, internal_ports):
    """Deploy service"""
    if not image:
        image = get_project_config().get('image.name')
        if not image:
            click.echo(format_text("You're not in a fandogh directory and didn't provide an image name using --image"
                                   ", please provide an image name, it could \nbe a full image name tagged with a "
                                   "repository or simply name of one of the images you already published.\nfor example:\n"
                                   "- myprivate.repository.com:5000/mynamespace/imagename <-- full image name\n"
                                   "- some-image-name <-- image you already published on fandogh\n"
                                   "- myusername/image-name <-- image from docker hub\n", TextStyle.OKBLUE))
            image = click.prompt("Image name: ").strip()
            if not image:
                click.echo(
                    format_text("It's not possible to perform deploy operation withou image name", TextStyle.FAIL),
                    err=True)
                exit(-1)
    deployment_result = deploy_service(image, version, name, envs, hosts, port, internal, registry_secret, image_pull_policy, internal_ports)
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
def service_list():
    """List all services for this image"""
    table = present(lambda: list_services(),
                    renderer='table',
                    headers=['Service Name', 'URL', 'Service Type', 'Started at', 'State'],
                    columns=['name', 'url', 'service_type', 'start_date', 'state'])
    if table:
        click.echo(table)
    else:
        click.echo('\nYou have no running services right now, why don\'t you try deploying one? \n'
                   'have fun and follow the link below:\n')
        click.echo('https://docs.fandogh.cloud/docs/services.html\n')


@click.command('destroy', cls=FandoghCommand)
@click.option('--name', 'service_name', prompt='Service name', help='Name of the service you want to destroy')
def service_destroy(service_name):
    """Destroy service"""
    message = present(lambda: destroy_service(service_name))
    click.echo(message)


@click.command('logs', cls=FandoghCommand)
@click.option('--name', 'service_name', prompt='Service name', help="Service name")
def service_logs(service_name):
    """Display service logs"""
    logs_response = get_logs(service_name)
    click.echo(logs_response['logs'])


@click.command('details', cls=FandoghCommand)
@click.option('--name', 'service_name', prompt='Service name')
def service_details(service_name):
    """Display service details"""
    details = get_details(service_name)

    if not details:
        return

    click.echo('Pods:')
    for pod in details['pods']:
        click.echo('  Name: {}'.format(pod['name']))
        click.echo('  Phase: {}'.format(
            format_text(pod['phase'], TextStyle.OKGREEN)
            if pod['phase'] == 'Running'
            else format_text(pod['phase'], TextStyle.WARNING)
        ))
        click.echo('  Containers:')
        for container in pod['containers']:
            click.echo('    Name: {}'.format(container['name']))
            click.echo('    Image: {}'.format(container['image']))
            click.echo('    Staus: {}'.format(format_text('Ready', TextStyle.OKGREEN) if container['ready']
                                              else format_text(container['waiting']['reason'], TextStyle.WARNING)))
            click.echo('    ---------------------')


service.add_command(deploy)
service.add_command(service_list)
service.add_command(service_destroy)
service.add_command(service_logs)
service.add_command(service_details)
