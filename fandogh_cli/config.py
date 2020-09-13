import os
from yaml import load, dump, FullLoader
from fandogh_cli.utils import makedirs

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class ConfigRepository:
    def __init__(self, configuration_file=None, configurations=None):
        if configuration_file is not None:
            self.configuration_file = configuration_file
            _configurations = self._load_from_file(configuration_file)
            self._load_from_dict(_configurations)
        if configurations is not None:
            self._load_from_dict(configurations)

    def _load_from_file(self, configuration_file):
        if os.path.exists(configuration_file):
            with open(configuration_file) as cfile:
                return load(cfile, Loader=FullLoader)
        makedirs(os.path.dirname(configuration_file))
        with open(configuration_file, mode='w'):
            pass
        return {}

    def _load_from_dict(self, configs):
        self._configs = configs or {}

    def set(self, key, value, save=True):
        self._configs[key] = value
        if save:
            self.save()

    def get(self, key, default=None):
        return self._configs.get(key, default)

    def get_dict(self):
        return self._configs

    def save(self):
        if self.configuration_file:
            with open(self.configuration_file, mode='w') as cfile:
                cfile.write(dump(self._configs, default_flow_style=False))


_config_repository = {}


def get_project_config():
    if 'project' not in _config_repository:
        _config_repository['project'] = ConfigRepository(os.path.join(os.getcwd(), '.fandogh', 'config.yml'))
    return _config_repository['project']


def get_user_config():
    if 'user' not in _config_repository:
        _config_repository['user'] = ConfigRepository(
            os.path.join(os.path.expanduser('~'), '.fandogh', 'credentials.yml')
        )
    return _config_repository['user']


def get_cluster_config():
    return get_user_config().get('clusters')


def set_cluster_config(clusters):
    return get_user_config().set('clusters', clusters)


def get_user_token():
    return get_cluster_token()


clusters = get_user_config().get('clusters', None)


def get_active_cluster():
    if clusters:
        for index, cluster in enumerate(clusters):
            if cluster['active']:
                return cluster
    return None


def get_cluster_token():
    if get_active_cluster():
        return get_active_cluster().get('token', None)
    return None


def set_cluster_token(token):
    for index, cluster in enumerate(clusters):
        if cluster['active']:
            del clusters[index]
            custom_dict = [
                dict(name=cluster['name'], url=cluster['url'], active=True, token=token),
            ]
            custom_dict.extend(clusters)
            set_cluster_config(custom_dict)


def get_cluster_namespace():
    if get_active_cluster():
        return get_active_cluster().get('namespace', None)
    return None


def set_cluster_namespace(namespace):
    if clusters:
        for index, cluster in enumerate(clusters):
            if cluster['active']:
                token = cluster.get('token', None)
                del clusters[index]
                custom_dict = [
                    dict(name=cluster['name'], url=cluster['url'], active=True, token=token,
                         namespace=namespace),
                ]
                custom_dict.extend(clusters)
                set_cluster_config(custom_dict)
