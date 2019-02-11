import os
import zipfile
from fnmatch import fnmatch
from fandogh_cli.utils import debug
import sys


if sys.version[0] == '2':
    from itertools import imap as map


class Workspace:
    def __init__(self, workspace_config=None):
        workspace_config = workspace_config or {}
        self.path = workspace_config.get('path', os.getcwd())
        self.zip_file_name = os.path.join(self.path, 'workspace.zip')
        files = os.listdir(self.path)
        files_lowercase = list(map(str.lower, files))

        self.docker_file_name = ''
        if 'dockerfile' in files_lowercase:
            self.docker_file_name = files[files_lowercase.index('dockerfile')]

        self.docker_ignore_name = ''
        if '.dockerignore' in files_lowercase:
            self.docker_ignore_name = files[files_lowercase.index('.dockerignore')]

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
        if not self.docker_ignore_name:
            return []
        with open(os.path.join(self.path, self.docker_ignore_name), 'r') as file:
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
                    if (file != self.docker_file_name and
                        any(fnmatch(file_path, ignore.strip()) for ignore in ignored_entries)):
                        debug('{} filtered out.'.format(file_path))
                        continue
                    ziph.write(file_path)
