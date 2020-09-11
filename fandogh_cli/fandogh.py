#!/usr/bin/env python

from fandogh_cli.namespace_commands import namespace
from fandogh_cli.secret_commands import secret
from .base_commands import FandoghCommand
from .domain_commands import domain
from .exec_commands import exec_command
from .fandogh_client import *
from .image_commands import image
from .managed_service_commands import managed_service
from .presenter import present
from .service_commands import service
from .source_commands import source
from .volume_commands import volume
from .cluster_commands import cluster
from .config import get_user_token, get_cluster_config, set_cluster_config
from .cluster_commands import fandogh as fandogh_cluster


@click.group("cli")
@click.version_option()
def base():
    pass


@click.command(cls=FandoghCommand)
@click.option('--username', prompt='username', help='your username')
@click.option('--password', prompt='password', help='your password', hide_input=True)
def login(username, password):
    """Login to fandogh server"""

    def handle_token():
        token_obj = get_token(username, password)
        clusters = get_cluster_config()
        get_user_config().set('token', token_obj['token'])
        if clusters is None:
            fandogh_cluster[0]['token'] = token_obj['token']
            set_cluster_config(fandogh_cluster)
        else:
            for index, cluster in enumerate(clusters):
                if cluster['active']:
                    del clusters[index]
                    custom_dict = [
                        dict(name=cluster['name'], url=cluster['url'], active=True, token=token_obj['token']),
                    ]
                    custom_dict.extend(clusters)
                    set_cluster_config(custom_dict)

    message = present(lambda: handle_token(), post='Logged in successfully')

    click.echo(" ___  _   _  _  __   _   __  _ _    __  _   _  _ _  __  ")
    click.echo("| __|/ \ | \| ||  \ / \ / _|| U |  / _|| | / \| | ||  \ ")
    click.echo("| _|| o || \  || o | o | |_n|   | ( (_ | |( o ) U || o )")
    click.echo("|_| |_n_||_|\_||__/ \_/ \__/|_n_|  \__||___\_/|___||__/ ")
    click.echo("                                                        ")
    click.echo(message + '\n')
    click.echo('Welcome to Fandogh Cloud, you can start using our PaaS as quickly as a link click, Try it below:\n')
    click.echo('https://docs.fandogh.cloud/docs/getting-started.html\n')


base.add_command(login)
base.add_command(image)
base.add_command(source)
base.add_command(service)
base.add_command(managed_service)
base.add_command(domain)
base.add_command(secret)
base.add_command(namespace)
base.add_command(exec_command)
base.add_command(volume)
base.add_command(cluster)
if __name__ == '__main__':
    base()
