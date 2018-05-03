import os

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def get_config_path():
    cwd = os.getcwd()
    config_path = os.path.join(cwd, '.fandogh', 'config.yml')
    return config_path


def persist_config(app):
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as file:
        file.write(dump({'app.name': app}, default_flow_style=False))
        pass


def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = load(file)
            return config
    return None
