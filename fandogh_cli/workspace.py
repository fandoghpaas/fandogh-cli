import os
import zipfile
from fnmatch import fnmatch
from fandogh_cli.utils import debug


class Workspace:
    def __init__(self, workspace_config=None):
        workspace_config = workspace_config or {}
        self.path = workspace_config.get('path', os.getcwd())
        self.zip_file_name = os.path.join(self.path, 'workspace.zip')
        files = os.listdir(self.path)
        self.has_docker_ignore = '.dockerignore' in files
        self.has_docker_file = 'Dockerfile' in files
        self._create_zip_file()
        self.zip_file_size_kb = os.path.getsize(self.zip_file_name)
        self.zip_file_size = self.zip_file_size_kb / 1048576

    def _create_zip_file(self):
        zipf = zipfile.ZipFile(self.zip_file_name, 'w', zipfile.ZIP_DEFLATED)
        self.zipdir(self.path, zipf)
        zipf.close()

    def clean(self):
        if os.path.exists(self.zip_file_name):
            os.remove(self.zip_file_name)

    def __str__(self):
        return self.zip_file_name

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        return str(self)

    def get_ignored_entries(self):
        if not self.has_docker_ignore:
            return []
        with open(os.path.join(self.path, '.dockerignore'), 'r') as file:
            entries = file.readlines()
        return entries

    def zipdir(self, path, ziph):
        ignored_entries = self.get_ignored_entries()
        ignored_entries.append('*dockerignore')
        debug(ignored_entries)
        for root, dirs, files in os.walk(path):
            for file in files:
                if file != 'workspace.zip':
                    file_path = os.path.join(os.path.relpath(root, path), file)
                    if file.lower() != "dockerfile" and any(
                            fnmatch(file_path, ignore.strip()) for ignore in ignored_entries):
                        debug('{} filtered out.'.format(file_path))
                        continue
                    ziph.write(file_path)
