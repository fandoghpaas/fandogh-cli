import requests

from fandogh_cli.fandogh_client import base_url, get_exception

base_domains_url = '%sdomains' % base_url


def add_domain(name, token):
    request = {
        'name': name
    }
    response = requests.post(base_domains_url,
                             json=request,
                             headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def list_domains(token):
    response = requests.get(base_domains_url,
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def verify_domain(name, token):
    response = requests.post(base_domains_url + '/' + name + '/verifications',
                             headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
