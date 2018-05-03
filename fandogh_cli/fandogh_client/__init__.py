import requests

base_url = 'http://fandogh.cloud:8080/api/webapp/'


def create_app(app_name):
    response = requests.post(base_url + 'apps', data={'name': app_name})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.text


def create_version(app_name, version):
    with open('/Users/SOROOSH/projects/fandogh/fandogh-cli/Archive.zip', 'rb') as file:
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


def deploy_container(app_name, version):
    response = requests.post(base_url + 'deployments', data={'app_name': app_name, 'img_version': version})
    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.text
