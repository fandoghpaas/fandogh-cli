import requests

from fandogh_cli.fandogh_client import base_url, get_exception

base_reports_url = '%serrors' % base_url


def report(info):
    response = requests.post(base_reports_url,
                             json=info)
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
