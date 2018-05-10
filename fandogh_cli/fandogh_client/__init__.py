import requests
import os

fandogh_host = os.getenv('FANDOGH_HOST', 'http://fandogh.cloud:8080')
base_url = '%s/api/' % fandogh_host
base_webapp_url = '%swebapp/' % base_url


def create_app(app_name, token):
    response = requests.post(base_webapp_url + 'apps',
                             json={'name': app_name},
                             headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.text


def get_apps(token):
    response = requests.get(base_webapp_url + 'apps',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()


def get_build(app, version, token):
    response = requests.get(base_webapp_url + 'apps/' + app + '/versions/' + version + '/builds',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()


def create_version(app_name, version, workspace_path):
    with open(workspace_path, 'rb') as file:
        files = {'source': file}
        response = requests.post(base_webapp_url + 'apps/' + app_name + '/versions',
                                 files=files,
                                 json={'version': version})
        if response.status_code != 200:
            raise Exception(response.text)
        else:
            return response.text


def list_versions(app_name):
    response = requests.get(base_webapp_url + 'apps/' + app_name + '/versions')
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()


def _parse_env_variables(envs):
    env_variables = {}
    print(envs)
    for env in envs:
        (k, v) = env.split('=')
        env_variables[k] = v
    return env_variables


def deploy_service(app_name, version, service_name, envs, token):
    env_variables = _parse_env_variables(envs)
    print(env_variables)
    response = requests.post(base_webapp_url + 'services',
                             json={'app_name': app_name,
                                   'img_version': version,
                                   'service_name': service_name,
                                   'environment_variables': env_variables},
                             headers={'Authorization': 'JWT ' + token}
                             )
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()


def list_services(token):
    response = requests.get(base_webapp_url + 'services',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()


def destroy_service(service_name, token):
    response = requests.delete(base_webapp_url + 'services/' + service_name,
                               headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()


def get_token(username, password):
    response = requests.post(base_url + 'tokens', json={'username': username, 'password': password})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()
