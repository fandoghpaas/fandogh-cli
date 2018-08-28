import json

import requests
import os
from fandogh_cli.config import get_user_config

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

        if hasattr(self.response, 'json'):
            self.message = self.response.json().get('message', self.message)


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


class CommandParameterException(Exception):
    def __init__(self, error_dict):
        try:
            self.message = "Errors: \n{}".format(
                "\n".join([" -> {}: {}".format(k, v) for k, v in error_dict.items()]))
        except AttributeError:
            self.message = json.dumps(error_dict, indent=' ')


def get_stored_token():
    token_obj = get_user_config().get('token')
    if token_obj is None:
        raise AuthenticationError()
    return token_obj


def get_exception(response):
    exception_class = {
        404: ResourceNotFoundError,
        401: AuthenticationError,
        400: FandoghBadRequest,
        500: FandoghInternalError,
    }.get(response.status_code, FandoghAPIError)
    return exception_class(response)


def create_image(image_name):
    token = get_stored_token()
    response = requests.post(base_images_url,
                             json={'name': image_name},
                             headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def delete_image(image_name):
    token = get_stored_token()
    response = requests.delete(base_images_url + '/' + image_name,
                               headers={'Authorization': 'JWT ' + token})

    if response.status_code != 200:
        raise get_exception(response)

    return response.json()


def get_images():
    token = get_stored_token()
    response = requests.get(base_images_url,
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        result = response.json()
        for item in result:
            item['last_version_version'] = (item.get('last_version', {}) or {}).get('version', '--')
            item['last_version_date'] = (item.get('last_version', {}) or {}).get('date', '--')
        return result


def get_image_build(image_name, version, image_offset):
    token = get_stored_token()

    response = requests.get(
        base_images_url + '/' + image_name + '/versions/' + version + '/builds', params={'image_offset': image_offset},
        headers={'Authorization': 'JWT ' + token})

    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


from requests_toolbelt.multipart import encoder


def create_version(image_name, version, workspace_path, monitor_callback):
    token = get_stored_token()
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


def list_versions(image_name):
    token = get_stored_token()
    response = requests.get(base_images_url + '/' + image_name + '/versions',
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        result = response.json()
        for item in result:
            item['size'] = str(item.get('size') / 1000 / 1000) + 'MB'
        return result


def _parse_key_values(envs):
    env_variables = {}
    for env in envs:
        (k, v) = env.split('=', 1)
        env_variables[k] = v
    return env_variables


def parse_port_mapping(port_mapping):
    # validate and convert outside:inside:protocol to a nice dict
    port_mapping = port_mapping.upper()
    parts = port_mapping.split(":")
    if len(parts) == 3:
        outside, inside, protocol = parts
        if protocol not in ('TCP', 'UDP'):
            raise CommandParameterException(
                {"internal_ports": [
                    "%s is not a valid protocol in %s, protocol can ba tcp or udp" % (protocol, port_mapping)]})
    elif len(parts) == 2:
        protocol = "TCP"
        outside, inside = parts
    else:
        raise CommandParameterException(
            {"internal_ports": ["{} is not a valid port mapping, use this form outsidePort:insidePort:protocol, "
                                "which protocol is optional and default protocol is tcp".format(port_mapping)]})
    try:
        return dict(outside=int(outside), inside=int(inside), protocol=protocol)
    except ValueError:
        raise CommandParameterException(
            {"internal_ports": ["{} is not a valid port mapping, port numbers should be numbers".format(port_mapping)]})


def deploy_service(image_name, version, service_name, envs, hosts, port, internal, registry_secret, image_pull_policy,
                   internal_ports):
    token = get_stored_token()
    env_variables = _parse_key_values(envs)
    internal_ports = list(internal_ports)
    internal_ports.append("{}:{}".format(port, port))
    body = {'image_name': image_name,
            'image_version': version,
            'service_name': service_name,
            'environment_variables': env_variables,
            'port': port,
            'registry_secret': registry_secret,
            'hosts': hosts,
            'internal_port_mapping': [parse_port_mapping(port_mapping) for port_mapping in internal_ports],
            'image_pull_policy': image_pull_policy}
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


def list_services():
    token = get_stored_token()
    response = requests.get(base_services_url,
                            headers={'Authorization': 'JWT ' + token})
    if response.status_code != 200:
        raise get_exception(response)
    else:
        json_result = response.json()
        return json_result


def destroy_service(service_name):
    token = get_stored_token()
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


def get_logs(service_name, last_logged_time):
    token = get_stored_token()

    response = requests.get(base_services_url + '/' + service_name + '/logs',
                            headers={'Authorization': 'JWT ' + token}, params={'last_logged_time': last_logged_time})

    if response.status_code == 200:
        return response.json()
    else:
        raise get_exception(response)


def get_details(service_name):
    services = list_services()
    for service in services:
        if service['name'] == service_name:
            return service


def deploy_managed_service(service_name, version, configs):
    token = get_stored_token()
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


def help_managed_service():
    token = get_stored_token()
    response = requests.get(
        base_managed_services_url,
        headers=dict(Authorization='JWT ' + token)
    )
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()


def deploy_manifest(manifest):
    token = get_stored_token()
    response = requests.post(base_services_url + '/manifests',
                             json=manifest,
                             headers={'Authorization': 'JWT ' + token}
                             )
    if response.status_code != 200:
        raise get_exception(response)
    else:
        return response.json()
