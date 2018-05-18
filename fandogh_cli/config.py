import os
from yaml import load, dump
from fandogh_cli.utils import makedirs

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

#
# class ConfigObject:
#     def __init__(self, **kwargs):
#         self.app_name = kwargs.get('app.name')
#
#
# def _get_config_path():
#     cwd = os.getcwd()
#     config_path = os.path.join(cwd, '.fandogh', 'config.yml')
#     return config_path
#
#
# def _get_credentials_path():
#     home = os.path.expanduser('~')
#     credentials_path = os.path.join(home, '.fandogh', 'credentials.yml')
#     return credentials_path
#
#
# def persist_config(app):
#     config_path = _get_config_path()
#     makedirs(os.path.dirname(config_path), exist_ok=True)
#     with open(config_path, 'w') as file:
#         file.write(dump({'app.name': app}, default_flow_style=False))
#
#
# def persist_token(token_obj):
#     credentials_path = _get_credentials_path()
#     makedirs(os.path.dirname(credentials_path), exist_ok=True)
#     with open(credentials_path, 'w') as file:
#         file.write(dump(token_obj, default_flow_style=False))
#
#
# def load_token():
#     credentials_path = _get_credentials_path()
#     token_obj = load_yml_file(credentials_path)
#     return token_obj.get('token', None) if token_obj else None
#
#
# def load_config():
#     config_path = _get_config_path()
#     return ConfigObject(**load_yml_file(config_path))
#
#
# def load_yml_file(path):
#     if os.path.exists(path):
#         with open(path, 'r') as file:
#             yml_dic = load(file)
#             return yml_dic
#     return None


class ConfigRepository:
    def __init__(self, configuration_file=None, configurations=None):
        if configuration_file is not None:
            self.configuration_file = configuration_file
            configurations = self._load_from_file(configuration_file)
            self._load_from_dict(configurations)
        elif configurations is not None:
            self._load_from_dict(configurations)

    def _load_from_file(self, configuration_file):
        if os.path.exists(configuration_file):
            with open(configuration_file) as cfile:
                return load(cfile)
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

    def get(self, key):
        return self._configs.get(key, None)

    def save(self):
        if self.configuration_file:
            with open(self.configuration_file, mode='w') as cfile:
                cfile.write(dump(self._configs, default_flow_style=False))


def _initialize_configuration():
    return {
        'project': ConfigRepository(os.path.join(os.getcwd(), '.fandogh', 'config.yml')),
        'user': ConfigRepository(os.path.join(os.path.expanduser('~'), '.fandogh', 'credentials.yml'))
    }


_config_repository = _initialize_configuration()


def get_project_config():
    return _config_repository['project']


def get_user_config():
    return _config_repository['user']
