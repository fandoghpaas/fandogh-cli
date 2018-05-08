import os
import zipfile


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
    if os.path.exists(zip_file_name):
        os.remove(zip_file_name)


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file != 'workspace.zip':
                ziph.write(os.path.join(os.path.relpath(root, path), file))