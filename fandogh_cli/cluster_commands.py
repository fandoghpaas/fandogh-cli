import click
from .base_commands import FandoghCommand

from .config import *

fandogh = [{'name': 'fandogh', 'url': 'https://api.fandogh.cloud', 'active': True}]


@click.group("cluster")
def cluster():
    pass


@click.command("add", cls=FandoghCommand)
@click.option('--name', prompt='name', help="Enter name for cluster url")
@click.option('--url', prompt='url', help="Enter cluster URL")
def add(name, url):
    old_clusters = get_cluster_config().get('clusters')
    if not old_clusters:
        custom_dict = [dict(name=name, url=url, active=False),
                       *fandogh]
    else:
        custom_dict = [dict(name=name, url=url, active=False), *old_clusters]
    get_cluster_config().set('clusters', custom_dict)


@click.command("list", cls=FandoghCommand)
def cluster_list():
    if get_cluster_config().get('clusters') is None:
        get_cluster_config().set('clusters', fandogh)
    for zone in get_cluster_config().get('clusters'):
        message = f' * {zone["name"]}'
        if zone['active']:
            message += ' (active)'
        click.echo(message)


@click.command('active')
@click.option('--name', prompt='name', help='Enter name of Cluster')
def cluster_active(name):
    clusters = get_cluster_config().get('clusters')
    for index, zone in enumerate(clusters):
        if zone['name'] == name:
            zone.update(active=True)
            [d.update(active=False) for d in clusters]
            clusters[index]['active'] = True
            get_cluster_config().set('clusters', clusters)
            return
    click.echo(message='This cluster Does not exist please select from cluster list')


cluster.add_command(add)
cluster.add_command(cluster_list)
cluster.add_command(cluster_active)
