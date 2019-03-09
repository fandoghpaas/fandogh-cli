from fandogh_cli.fandogh_client import base_url, get_exception, get_session

base_exec_url = '%sservices/exec_commands' % base_url
base_session_url = '%sservices/exec_sessions' % base_url


def post_exec(pod_name, command):
    response = get_session().post(base_exec_url,
                                  json={'pod_name': pod_name, 'command': command})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def post_session(pod_name, command):
    response = get_session().post(base_session_url,
                                  json={'pod_name': pod_name, 'command': command})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
