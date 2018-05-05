import os

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def _get_config_path():
    cwd = os.getcwd()
    config_path = os.path.join(cwd, '.fandogh', 'config.yml')
    return config_path


def _get_credentials_path():
    home = os.path.expanduser('~')
    credentials_path = os.path.join(home, '.fandogh', 'credentials.yml')
    return credentials_path


def persist_config(app):
    config_path = _get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as file:
        file.write(dump({'app.name': app}, default_flow_style=False))


def persist_token(token_obj):
    credentials_path = _get_credentials_path()
    os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
    with open(credentials_path, 'w') as file:
        file.write(dump(token_obj, default_flow_style=False))


def load_token():
    credentials_path = _get_credentials_path()
    token_obj = load_yml_file(credentials_path)
    return token_obj.get('token', None) if token_obj else None


def load_config():
    config_path = _get_config_path()
    return load_yml_file(config_path)


def load_yml_file(path):
    if os.path.exists(path):
        with open(path, 'r') as file:
            yml_dic = load(file)
            return yml_dic
    return None
