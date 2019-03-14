import requests

from fandogh_cli.fandogh_client import base_url, get_exception, parse_key_values, get_session
from fandogh_cli.fandogh_client import get_stored_token
from fandogh_cli.utils import convert_datetime

base_secrets_url = '%ssecrets' % base_url


def list_secret():
    response = get_session().get(base_secrets_url)
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
    response = get_session().post(base_secrets_url,
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


def put_secret(name, secret_type, fields):
    response = get_session().put(base_secrets_url + "/" + name,
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


def delete_secret(name):
    response = get_session().delete(base_secrets_url + "/" + name,
                                    json={},
                                    )
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
