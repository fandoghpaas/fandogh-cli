from .base_commands import FandoghCommand
from .fandogh_client import *
from .utils import format_text, TextStyle, parse_key_values


@click.group("managed-service")
def managed_service():
    """Service management commands"""


@click.command("deploy", cls=FandoghCommand)
@click.argument('name', nargs=1)
@click.argument('version', nargs=1)
@click.option('-c', '--config', 'configs', help='Managed service configuration (format: VARIABLE_NAME=VARIABLE_VALUE)',
              multiple=True)
@click.option('-m', '--memory', 'memory', help='Managed service memory', default='200Mi')
def deploy(name, version, configs, memory):
    """Deploy Managed Service"""
    try:
        response = deploy_manifest(_generate_managed_manifest(name, version, configs, memory))
        help_message = response.get("help_message", None)
        if help_message:
            click.echo(help_message)
        else:
            service_urls = response.get('urls', [])
            if len(service_urls) > 0:
                click.echo(
                    "If your service has any web interface, "
                    "it will be available via the following urls in few seconds:\n{}".format(
                        "".join([" - {}\n".format(u) for u in service_urls])
                    ))
    except FandoghBadRequest:
        click.echo(format_text(
            "please check `fandogh managed-service help` for more information "
            "regarding fandogh managed services",
            TextStyle.FAIL))
        raise


@click.command("help", cls=FandoghCommand)
def help():
    """Display Help for Managed Service"""
    managed_services = help_managed_service()
    click.echo(format_text(
        "List of Fandogh managed services:", TextStyle.OKBLUE
    ))
    for managed_service in managed_services:
        click.echo("\t* Service name: {}".format(managed_service['name']))
        for parameter_name, description in managed_service['options'].items():
            click.echo("\t\t. {}:\t{}".format(parameter_name.ljust(20), description))


def _generate_managed_manifest(service_type, version, config, memory):
    manifest = dict()
    manifest['kind'] = 'ManagedService'

    spec = dict()
    manifest['name'] = spec['service_name'] = service_type
    spec['version'] = version

    param_list = []
    service_parameters = parse_key_values(config)
    for key in service_parameters:
        if key == 'service_name':
            manifest['name'] = service_parameters[key]
        else:
            param_list.append({'name': key, 'value': service_parameters[key]})

    spec['parameters'] = param_list
    spec['resources'] = {'memory': memory}
    manifest['spec'] = spec
    return manifest


managed_service.add_command(help)
managed_service.add_command(deploy)
