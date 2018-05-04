import os
from shutil import make_archive


def build_workspace(workspace_config):
    workspace_path = workspace_config.get('path', os.getcwd())
    zip_file_name = os.path.join(workspace_path, 'workspace')
    make_archive(zip_file_name, 'zip')
    return zip_file_name + '.zip'


