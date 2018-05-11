import os
import zipfile
from fnmatch import fnmatch

FANDOGH_DEBUG = os.environ.get('FANDOGH_DEBUG', False)


def get_ignored_entries():
    if not os.path.exists('.dockerignore'):
        return []
    with open('.dockerignore', 'r') as file:
        entries = file.readlines()
    return entries


def build_workspace(workspace_config):
    workspace_path = workspace_config.get('path', os.getcwd())
    zip_file_name = os.path.join(workspace_path, 'workspace.zip')
    zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    zipdir(workspace_path, zipf)
    zipf.close()

    return zip_file_name


def cleanup_workspace(workspace_config):
    workspace_path = workspace_config.get('path', os.getcwd())
    zip_file_name = os.path.join(workspace_path, 'workspace.zip')
    # if os.path.exists(zip_file_name):
    #     os.remove(zip_file_name)


def zipdir(path, ziph):
    ignored_entries = get_ignored_entries()
    ignored_entries.append('*dockerignore')
    if FANDOGH_DEBUG:
        print(ignored_entries)
    for root, dirs, files in os.walk(path):
        for file in files:
            if file != 'workspace.zip':
                file_path = os.path.join(os.path.relpath(root, path), file)
                if any(fnmatch(file_path, ignore.strip()) for ignore in ignored_entries):
                    if FANDOGH_DEBUG:
                        print('{} filtered out.'.format(file_path))
                    continue
                ziph.write(file_path)
