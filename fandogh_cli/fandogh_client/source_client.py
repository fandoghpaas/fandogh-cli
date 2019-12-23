import click

from fandogh_cli.utils import TextStyle, format_text
from requests_toolbelt.multipart import encoder

from fandogh_cli.fandogh_client import base_url, get_exception, get_session, get_manifest_document

base_sources_url = '{}sources'.format(base_url)


def upload_source(workspace_path, manifest, monitor_callback):
    with open(workspace_path, 'rb') as file:
        e = encoder.MultipartEncoder(
            fields={
                'source': ('workspace', file, 'text/plain'),
                'manifest': manifest
            }
        )
        m = encoder.MultipartEncoderMonitor(e, monitor_callback)

        response = get_session().post(base_sources_url, data=m, headers={'Content-Type': m.content_type})

        if response.status_code != 200:
            if response.status_code == 400:
                document = get_manifest_document(list(response.json().keys())[0])
                click.echo(format_text(document, TextStyle.WARNING))
            raise get_exception(response)
        else:
            return response.json()


def get_project_types():
    response = get_session().get(base_sources_url + '/project-types')
    if response.status_code != 200:
        raise get_exception(response)
    return response.json()
