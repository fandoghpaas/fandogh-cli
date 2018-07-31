import requests
import os

fandogh_host = os.getenv('FANDOGH_HOST', 'https://api.fandogh.cloud')
base_url = '%s/api/' % fandogh_host
base_images_url = '%simages' % base_url
base_services_url = '%sservices' % base_url
base_managed_services_url = '%smanaged-services' % base_url
max_workspace_size = 20  # MB


class TooLargeWorkspace(Exception):
    pass


class FandoghAPIError(Exception):
    message = "Server Error"

    def __init__(self, response):
        self.response = response


class AuthenticationError(Exception):
    message = "Please login first. You can do it by running 'fandogh login' command"

    def __init__(self, response):
        self.response = response


class ResourceNotFoundError(FandoghAPIError):
    message = "Resource Not found"

    def __init__(self, response, message=None):
        self.response = response
        if message:
            self.message = message


class FandoghInternalError(FandoghAPIError):
    message = "Sorry, there is an internal error, the incident has been logged and we will fix it ASAP"

    def __init__(self, response):
        self.response = response


class FandoghBadRequest(FandoghAPIError):
    def __init__(self, response):
        self.response = response
        try:
            self.message = "Errors: \n{}".format(
                "\n".join([" -> {}: {}".format(k, v) for k, v in response.json().items()]))
        except AttributeError:
            self.message = response.text


def get_exception(response):
    exception_class = {
        404: ResourceNotFoundError,
        401: AuthenticationError,
        400: FandoghBadRequest,
        500: FandoghInternalError,
    }.get(response.status_code, FandoghAPIError)
    return exception_class(response)


def create_image(image_name, token):
    response = requests.post(base_images_url,
                             json={'name': image_name},
                             headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def get_images(token):
    response = requests.get(base_images_url,
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def get_image_build(image_name, version, token):
    response = requests.get(base_images_url + '/' + image_name + '/versions/' + version + '/builds',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


from requests_toolbelt.multipart import encoder


def create_version(image_name, version, workspace_path, monitor_callback, token):
    with open(workspace_path, 'rb') as file:
        e = encoder.MultipartEncoder(
            fields={'version': version,
                    'source': ('workspace', file, 'text/plain')}
        )
        m = encoder.MultipartEncoderMonitor(e, monitor_callback)

        response = requests.post(base_images_url + '/' + image_name + '/versions',
                                 data=m,
                                 headers={'Content-Type': m.content_type,
                                          'Authorization': 'JWT ' + token})

        if response.status_code == 404:
            raise ResourceNotFoundError(
                response=response,
                message="There is no image named {}, please check for typo".format(image_name)
            )
        if response.status_code != 200:
            raise get_exception(response)
        else:
            return response.json()


def list_versions(image_name, token):
    response = requests.get(base_images_url + '/' + image_name + '/versions',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def _parse_key_values(envs):
    env_variables = {}
    for env in envs:
        (k, v) = env.split('=')
        env_variables[k] = v
    return env_variables


def deploy_service(image_name, version, service_name, envs, hosts, port, token, internal):
    env_variables = _parse_key_values(envs)
    body = {'image_name': image_name,
            'image_version': version,
            'service_name': service_name,
            'environment_variables': env_variables,
            'port': port,
            'hosts': hosts}
    if internal:
        body['service_type'] = "INTERNAL"

    response = requests.post(base_services_url,
                             json=body,
                             headers={'Authorization': 'JWT ' + token}
                             )
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def list_services(token, show_all):
    response = requests.get(base_services_url,
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        json_result = response.json()
        if show_all:
            return json_result
        return [item for item in json_result if item.get('state', None) == 'RUNNING']


def destroy_service(service_name, token):
    response = requests.delete(base_services_url + '/' + service_name,
                               headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json().get('message', "`{}` service has been destroyed successfully".format(service_name))


def get_token(username, password):
    response = requests.post(base_url + 'tokens', json={'username': username, 'password': password})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def get_logs(service_name, token):
    response = requests.get(base_services_url + '/' + service_name + '/logs',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code == 200:
        return response.json()
    else:
        raise get_exception(response)


def deploy_managed_service(service_name, version, configs, token):
    configution = _parse_key_values(configs)
    response = requests.post(base_managed_services_url,
                             json={'name': service_name,
                                   'version': version,
                                   'config': configution},
                             headers={'Authorization': 'JWT ' + token}
                             )
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def help_managed_service(token):
    response = requests.get(
        base_managed_services_url,
        headers=dict(Authorization='JWT ' + token)
    )
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
