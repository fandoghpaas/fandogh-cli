import click
from .base_presenter import present
from fandogh_cli.utils import TextStyle, format_text


def present_service_detail(details):
    if details.get('env'):
        click.echo('Environment Variables:')
        click.echo(present(lambda: details.get('env'), renderer='table',
                           headers=['Name', 'Value'],
                           columns=['name', 'value'])
                   )

    if details.get('urls'):
        click.echo('Domains:')

        for url in details['urls']:
            click.echo(' - {}'.format(url))

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
