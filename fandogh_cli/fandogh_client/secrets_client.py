import requests

from fandogh_cli.fandogh_client import base_url, get_exception, parse_key_values
from fandogh_cli.fandogh_client import get_stored_token
from fandogh_cli.utils import convert_datetime

base_secrets_url = '%ssecrets' % base_url


def list_secret():
    token = get_stored_token()
    response = requests.get(base_secrets_url,
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        result = []
        for secret in response.json():
            secret["created_at"] = convert_datetime(secret["created_at"])
            result.append(
                secret
            )
        return result


def create_secret(name, secret_type, fields):
    token = get_stored_token()
    response = requests.post(base_secrets_url,
                             headers={'Authorization': 'JWT ' + token},
                             json={
                                 "name": name,
                                 "type": secret_type,
                                 "fields": parse_key_values(fields)
                             },
                             )
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
