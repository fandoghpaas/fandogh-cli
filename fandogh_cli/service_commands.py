import click
from .fandogh_client import *
from .config import get_project_config
from .presenter import present
from .utils import format_text, TextStyle, read_manifest
from .base_commands import FandoghCommand
from time import sleep


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
    deployment_result = deploy_service(image, version, name, envs, hosts, port, internal, registry_secret,
                                       image_pull_policy, internal_ports)
    message = "\nCongratulation, Your service is running ^_^\n\n"
    if str(deployment_result['service_type']).lower() == 'external':
        message += "Your service is accessible using the following URLs:\n{}".format(
            "\n".join([" - {}".format(url) for url in deployment_result['urls']])
        )
        message += '\n'
        click.echo(message)
    else:
        message += """
Since your service is internal, it's not accessible from outside your fandogh private network, 
but other services inside your private network will be able to find it using it's name: '{}'
        """.strip().format(
            deployment_result['name']
        )
        message += '\n'
        click.secho(message, bold=True, fg='yellow')


@click.command('list', cls=FandoghCommand)
def service_list():
    """List all services for this image"""
    table = present(lambda: list_services(),
                    renderer='table',
                    headers=['Service Name', 'URL', 'Service Type', "Memory Usages", 'Started at', 'Updated at',
                             'State'],
                    columns=['name', 'url', 'service_type', 'memory', 'start_date', 'last_update', 'state', ])
    if table:
        click.echo(table)
    else:
        click.echo('\nYou have no running services right now, why don\'t you try deploying one? \n'
                   'have fun and follow the link below:\n')
        click.echo('https://docs.fandogh.cloud/docs/services.html\n')


@click.command('destroy', cls=FandoghCommand)
@click.option('--name', '-s', '--service', 'service_name', prompt='Service name',
              help='Name of the service you want to destroy')
def service_destroy(service_name):
    """Destroy service"""
    message = present(lambda: destroy_service(service_name))
    click.echo(message)


@click.command('logs', cls=FandoghCommand)
@click.option('--name', 'service_name', prompt='Service name', help="Service name")
@click.option('--follow', '-f', is_flag=True, default=False, help='Monitoring service real-time logs')
def service_logs(service_name, follow):
    """Display service logs"""
    last_logged_time = 0

    while True:
        logs_response = get_logs(service_name, last_logged_time)

        if logs_response['logs']:
            click.echo(logs_response['logs'])

        if follow:
            last_logged_time = logs_response['last_logged_time']

        if not follow:
            break
        sleep(3)


@click.command('details', cls=FandoghCommand)
@click.option('--name', 'service_name', prompt='Service name')
def service_details(service_name):
    """Display service details"""
    details = get_details(service_name)

    if not details:
        return

    if details.get('env'):
        click.echo('Environment Variables:')
        click.echo(present(lambda: details.get('env'), renderer='table',
                           headers=['Name', 'Value'],
                           columns=['name', 'value'])
                   )
    click.echo('Pods:')
    for pod in details['pods']:
        click.echo('  Name: {}'.format(pod['name']))
        click.echo('  Created at: {}'.format(pod.get("created_at", "UNKNOWN")))
        click.echo('  Phase: {}'.format(
            format_text(pod['phase'], TextStyle.OKGREEN)
            if pod['phase'] == 'Running'
            else format_text(pod['phase'], TextStyle.WARNING)
        ))
        containers = pod.get('containers', [])
        containers_length = len(containers)
        ready_containers = list(filter(lambda c: c.get('ready', False), containers))
        ready_containers_length = len(ready_containers)
        if ready_containers_length != containers_length:
            pod_ready_message = '  Ready containers:' + format_text(
                ' {}/{}'.format(ready_containers_length, containers_length), TextStyle.WARNING)
        else:
            pod_ready_message = '  Ready containers:' + format_text(
                ' {}/{}'.format(containers_length, containers_length), TextStyle.OKGREEN)
        click.echo(pod_ready_message)
        click.echo('  Containers:')
        for container in pod['containers']:
            click.echo('    Name: {}'.format(container['name']))
            click.echo('    Image: {}'.format(container['image']))
            click.echo('    Staus: {}'.format(format_text('Ready', TextStyle.OKGREEN) if container['ready']
                                              else format_text(
                (container.get('waiting', {}) or {}).get('reason', 'Pending'),
                TextStyle.WARNING)))

        click.echo('    ---------------------')

        if pod.get('events', []) and containers_length != ready_containers_length:
            click.echo('    Events:')
            click.echo(
                present(lambda: pod.get('events'), renderer='table',
                        headers=['Reason', 'Message', 'Count', 'First Seen', 'Last Seen'],
                        columns=['reason', 'message', 'count', 'first_timestamp', 'last_timestamp'])
            )


@click.command('apply', cls=FandoghCommand)
@click.option('-f', '--file', 'file', prompt='File address')
@click.option('-p', '--parameter', 'parameters', help='Manifest parameters', multiple=True)
def service_apply(file, parameters):
    """Deploys a service defined as a manifest"""
    manifest_content = read_manifest(file, parameters)
    if manifest_content is None:
        return
    click.echo(manifest_content)
    from yaml import load

    yml = load(manifest_content)

    deployment_result = deploy_manifest(yml)
    message = "\nCongratulation, Your service is running ^_^\n"
    service_type = str(deployment_result.get('service_type', '')).lower()

    if service_type == 'external':
        message += "Your service is accessible using the following URLs:\n{}".format(
            "\n".join([" - {}".format(url) for url in deployment_result['urls']])
        )
    elif service_type == 'internal':
        message += """
    Since your service is internal, it's not accessible from outside your fandogh private network, 
    but other services inside your private network will be able to find it using it's name: '{}'
            """.strip().format(
            deployment_result['name']
        )
    elif service_type == 'managed':
        message += """
        Managed service deployed successfully
        """

    click.echo(message)


service.add_command(deploy)
service.add_command(service_apply)
service.add_command(service_list)
service.add_command(service_destroy)
service.add_command(service_logs)
service.add_command(service_details)
