from fandogh_cli.fandogh_client import base_url, get_exception, get_session

base_namespace_url = '%sapi/users/namespaces' % base_url


def list_namespaces():
    response = get_session().get(base_namespace_url)

    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def details_namespace():
    # TODO: use user's namespace)
    response = get_session().get("%s/%s" % (base_namespace_url, "NAMESPACE"))
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
