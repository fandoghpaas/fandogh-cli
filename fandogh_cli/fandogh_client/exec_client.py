import requests

from fandogh_cli.fandogh_client import base_url, get_exception
from fandogh_cli.fandogh_client import get_stored_token

base_exec_url = '%sservices/exec_commands' % base_url


def post_exec(pod_name, command):
    token = get_stored_token()
    response = requests.post(base_exec_url,
                             headers={'Authorization': 'JWT ' + token},
                             json={'pod_name': pod_name, 'command': command})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
