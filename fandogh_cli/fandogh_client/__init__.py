import requests

base_url = 'http://localhost:8000/api/webapp/'


# base_url = 'http://fandogh.cloud:8080/api/webapp/'


def create_app(app_name):
    response = requests.post(base_url + 'apps', data={'name': app_name})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.text


def create_version(app_name, version, workspace_path):
    with open(workspace_path, 'rb') as file:
        files = {'source': file}
        response = requests.post(base_url + 'apps/' + app_name + '/versions/' + version, files=files, data={'version': version})
        if response.status_code != 200:
            raise Exception(response.text)
        else:
            return response.text


def list_versions(app_name):
    response = requests.get(base_url + 'apps/' + app_name + '/versions')
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()


def deploy_service(app_name, version, service_name=None):
    response = requests.post(base_url + 'services', data={'app_name': app_name, 'img_version': version, 'service_name': service_name})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.text


def list_services():
    response = requests.get(base_url + 'services')
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()
