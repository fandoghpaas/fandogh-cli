from requests_toolbelt.multipart import encoder

from fandogh_cli.fandogh_client import base_url, get_exception, get_session

base_sources_url = '{}sources'.format(base_url)


def upload_source(workspace_path, monitor_callback):
    with open(workspace_path, 'rb') as file:
        e = encoder.MultipartEncoder(
            fields={
                'source': ('workspace', file, 'text/plain')}
        )
        m = encoder.MultipartEncoderMonitor(e, monitor_callback)

        response = get_session().post(base_sources_url, data=m, headers={'Content-Type': m.content_type})

        if response.status_code != 200:
            raise get_exception(response)
        else:
            return response.json()
