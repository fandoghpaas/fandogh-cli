import requests
from fandogh_cli.fandogh_client import base_url, get_exception
from fandogh_cli.fandogh_client import get_stored_token

base_namespace_url = '%sapi/users/namespaces' % base_url


def details_namespace():
    token = get_stored_token()
    response = requests.get("%s/%s" % (base_namespace_url, "NAMESPACE"),  # use user's namespace
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
