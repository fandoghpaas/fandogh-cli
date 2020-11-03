import click
import yaml
import sys
from .fandogh_client import *
from .config import get_project_config
from .utils import format_text, TextStyle, read_manifest
from .base_commands import FandoghCommand
from time import sleep
from .presenter import present_service_detail, present


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
@click.option('-d', 'detach', is_flag=True, default=False,
              help='detach terminal.')
def deploy(image, version, name, port, envs, hosts, internal, registry_secret, image_pull_policy, internal_ports,
           detach):
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
                    format_text(
                        "It's not possible to perform deploy operation withou image name", TextStyle.FAIL),
                    err=True)
                sys.exit(301)
    deployment_result = deploy_service(image, version, name, envs, hosts, port, internal, registry_secret,
                                       image_pull_policy, internal_ports)

    if detach:
        message = "\nCongratulation, Your service is running ^_^\n\n"
        if str(deployment_result['service_type']).lower() == 'external':
            message += "Your service is accessible using the following URLs:\n{}".format(
                "\n".join([" - {}".format(url)
                           for url in deployment_result['urls']])
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
    else:
        while True:
            details = get_details(name)

            if not details:
                sys.exit(302)

            click.clear()

            if details.get('state') == 'RUNNING':
                present_service_detail(details)
                message = "\nCongratulation, Your service is running ^_^\n\n"
                if str(deployment_result['service_type']).lower() == 'external':
                    message += "Your service is accessible using the following URLs:\n{}".format(
                        "\n".join([" - {}".format(url)
                                   for url in deployment_result['urls']])
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
                sys.exit(0)
            elif details.get('state') == 'UNSTABLE':
                present_service_detail(details)
                click.echo(
                    'You can press ctrl + C to exit details service state monitoring')
                sleep(3)
            else:
                sys.exit(303)


@click.command('list', cls=FandoghCommand)
def service_list():
    """List all services for this image"""
    data = list_services()
    table = present(lambda: data,
                    renderer='table',
                    headers=['Service Name', 'URLS', 'Service Type', "Memory Usages", 'Replicas', 'Started at',
                             'Updated at',
                             'State', 'Restarts'],
                    columns=['name', 'urls', 'service_type', 'memory', 'replicas', 'start_date', 'last_update', 'state',
                             'service_restarts'])
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
    click.echo(
        'you are about to destroy service with name {}.'.format(service_name))
    click.echo('It might take a while!')
    message = present(lambda: destroy_service(service_name))
    click.echo(message)


@click.command('logs', cls=FandoghCommand)
@click.option('--name', 'service_name', prompt='Service name', help="Service name")
@click.option('--follow', '-f', 'follow', is_flag=True, default=False, help='Monitoring service real-time logs')
@click.option('--max', '-m', 'max_logs', default=100, help='max log count from 100 to 2000')
@click.option('--with-timestamp', 'with_timestamp', is_flag=True, default=False, help='enable timestamp for logs')
@click.option('--previous', 'previous', is_flag=True, default=False, help='fetch service previous logs')
def service_logs(service_name, follow, max_logs, with_timestamp, previous):
    """Display service logs"""
    last_logged_time = 0

    while True:
        logs_response = get_logs(service_name, last_logged_time, max_logs, with_timestamp, previous)

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

    present_service_detail(details)


@click.command('apply', cls=FandoghCommand)
@click.option('-f', '--file', 'file', prompt='File address')
@click.option('-p', '--parameter', 'parameters', help='Manifest parameters', multiple=True)
@click.option('-d', 'detach', is_flag=True, default=False,
              help='detach terminal.')
@click.option('-h', '--hide', 'hide_manifest', is_flag=True, default=False,
              help='Hide manifest content.')
def service_apply(file, parameters, detach, hide_manifest):
    """Deploys a service defined as a manifest"""
    manifest_content = read_manifest(file, parameters)

    if manifest_content is None:
        return

    from yaml import load_all
    manifests = list(load_all(manifest_content))

    def hide_manifest_env_content(content):
        if 'spec' not in content:
            return content
        if 'env' not in content['spec']:
            return content

        from copy import deepcopy
        temp_content = deepcopy(content)
        for env in temp_content['spec']['env']:
            if env.get('hidden', False):
                env['value'] = '***********'
        return temp_content

    for index, service_conf in enumerate(manifests):
        click.echo(
            'service {} - {} is being deployed'.format(index + 1, len(manifests)))

        click.echo(
            yaml.safe_dump(hide_manifest_env_content(service_conf) if hide_manifest else service_conf,
                           default_flow_style=False),
        )

        deployment_result = deploy_manifest(service_conf)
        service_name = service_conf.get('name', '')
        message = "\nCongratulation, Your service is running ^_^\n"
        service_type = str(deployment_result.get('service_type', '')).lower()
        service_urls = deployment_result['urls']
        help_message = deployment_result.get('help_message', "")
        if help_message:
            message += help_message
        else:
            if service_type == 'external':
                message += "Your service is accessible using the following URLs:\n{}".format(
                    "\n".join([" - {}".format(url) for url in service_urls])
                )
            elif service_type == 'internal':
                message += """
            Since your service is internal, it's not accessible from outside your fandogh private network,
            but other services inside your private network will be able to find it using it's name: '{}'
                    """.strip().format(
                    deployment_result['name']
                )
            elif service_type == 'managed':
                message += """Managed service deployed successfully"""

                if len(service_urls) > 0:
                    message += "If your service has any web interface, it will be available via the following urls in few seconds:\n{}".format(
                        "".join([" - {}\n".format(u) for u in service_urls])
                    )

        if detach:
            click.echo(message)
        else:
            while True:
                details = get_details(service_name)

                if not details:
                    sys.exit(302)

                click.clear()

                if details.get('state') == 'RUNNING':
                    present_service_detail(details)
                    click.echo(message)
                    if index == len(manifest_content) - 1:
                        sys.exit(0)
                    else:
                        break
                elif details.get('state') == 'UNSTABLE':
                    present_service_detail(details)
                    click.echo(
                        'You can press ctrl + C to exit details service state monitoring')
                    sleep(3)
                else:
                    if index == len(manifest_content) - 1:
                        sys.exit(304)
                    else:
                        break


@click.command('dump', cls=FandoghCommand)
@click.option('-s', '--service', '--name', 'name', prompt='Service name')
def service_dump(name):
    click.echo(yaml.safe_dump(dump_manifest(name), default_flow_style=False))


@click.command('rollback', cls=FandoghCommand)
@click.option('-s', '--service', '--name', 'name', prompt='Service Name')
@click.option('--version', '-v', 'version', prompt='History Version')
def service_rollback(name, version):
    """Rollback Service to a Specific Selected Version"""
    if click.confirm(format_text('Rolling back a quick solution but it does not mean that selected version is healthy\n'
                                 'this is your responsibility to check desired version manifest to prevent unwanted '
                                 'issues!\ndo you want to proceed to rollback?',
                                 TextStyle.WARNING)):
        response = request_service_rollback(name, version)
        present_service_detail(response)

        while True:
            details = get_details(name)

            if not details:
                sys.exit(302)

            click.clear()

            if details.get('state') == 'RUNNING':
                present_service_detail(details)
                message = "\nCongratulation, Your service is running ^_^\n\n"
                if str(response['service_type']).lower() == 'external':
                    message += "Your service is accessible using the following URLs:\n{}".format(
                        "\n".join([" - {}".format(url)
                                   for url in response['urls']])
                    )
                    message += '\n'
                    click.echo(message)
                else:
                    message += """
              Since your service is internal, it's not accessible from outside your fandogh private network, 
              but other services inside your private network will be able to find it using it's name: '{}'
                      """.strip().format(
                        response['name']
                    )
                    message += '\n'
                    click.secho(message, bold=True, fg='yellow')
                sys.exit(0)
            elif details.get('state') == 'UNSTABLE':
                present_service_detail(details)
                click.echo(
                    'You can press ctrl + C to exit details service state monitoring')
                sleep(3)
            else:
                sys.exit(303)


@click.command('reset', cls=FandoghCommand)
@click.option('-s', '--service', '--name', 'name', prompt='Service Name')
def service_reset(name):
    """Restart Service"""
    _RESTART_SERVICE = 'RESTART'
    if click.confirm(format_text('Restarting service may cause downtime, are you sure about this action?',
                                 TextStyle.WARNING)):
        response = request_service_action(name, _RESTART_SERVICE)
        click.echo(response['message'])


@click.group('history')
def history():
    """Service History Commands"""


@click.command('list', cls=FandoghCommand)
@click.option('-s', '--service', '--name', 'name', prompt='Service name')
def history_list(name):
    """List of Service Deployments"""
    service_histories = request_service_history(name)
    table = present(lambda: service_histories,
                    renderer='table',
                    headers=['History Version', 'Service Name', 'Date Created', 'Manifest'],
                    columns=['id', 'name', 'created_at', 'manifest'])
    if table:
        click.echo(table)
    else:
        click.echo('There is no record of your service deployments available.')
        # click.echo('https://docs.fandogh.cloud/docs/services.html\n')


@click.command('delete', cls=FandoghCommand)
@click.option('-s', '--service', '--name', 'name', prompt='Service Name')
@click.option('--version', '-v', 'version', prompt='History Version')
def history_delete(name, version):
    """Delete Service History Item"""
    if click.confirm(format_text('Deleting service history is a permanent action, are you sure you want to delete '
                                 'this record?',
                                 TextStyle.WARNING)):
        click.echo(remove_service_history(name, version))


service.add_command(deploy)
service.add_command(service_apply)
service.add_command(service_list)
service.add_command(service_destroy)
service.add_command(service_logs)
service.add_command(service_details)
service.add_command(service_dump)
service.add_command(service_rollback)
service.add_command(service_reset)

service.add_command(history)
history.add_command(history_list)
history.add_command(history_delete)
