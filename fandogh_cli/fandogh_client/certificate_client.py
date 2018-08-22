import requests

from fandogh_cli.fandogh_client import base_url, get_exception, _parse_key_values
from fandogh_cli.fandogh_client import get_stored_token
from fandogh_cli.utils import convert_datetime

base_domains_url = '%sdomains' % base_url


def detail_certificate(name):
    token = get_stored_token()
    response = requests.get(base_domains_url + '/' + name + '/certificate',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def create_certificate(name):
    token = get_stored_token()
    response = requests.post(base_domains_url + '/' + name + '/certificate',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 201:
        raise get_exception(response)
    else:
        return response.json()
