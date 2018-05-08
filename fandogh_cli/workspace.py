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
    for i in os.listdir(path):
        if 'workspace.zip' not in i:
            ziph.write(i, compress_type=zipfile.ZIP_DEFLATED)
