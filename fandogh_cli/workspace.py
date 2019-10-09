import os
import zipfile
from fnmatch import fnmatch

from .exceptions import ValidationException
from .utils import debug


class Workspace:
    def __init__(self, workspace_config=None, context=None):
        workspace_config = workspace_config or {}
        self.path = workspace_config.get('path', os.getcwd())
        if context and context != '.':
            self.path = os.path.abspath(os.path.join(self.path, context))
        self.context = context or '.'

        if not os.path.exists(self.path):
            raise ValidationException('No directory or path with path {} exists!'.format(self.path))
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
        files = ['.fandoghignore', '.dockerignore']
        entries = []
        for file in files:
            if os.path.exists(os.path.join(self.path, file)):
                with open(os.path.join(self.path, file), 'r') as f:
                    line = f.readline()
                    cnt = 1
                    while line:
                        entries.append(line)
                        line = f.readline()
                        cnt += 1
        expand_entries = []
        for entry in entries:
            expand_entries.append(entry.strip() + os.sep + '*')
        if entries:
            return entries + expand_entries
        return []

    def zipdir(self, path, ziph):
        ignored_entries = self.get_ignored_entries()
        ignored_entries.append('*dockerignore')
        ignored_entries.append('*fandoghignore')
        debug(ignored_entries)
        for root, dirs, files in os.walk(path):
            for file in files:
                if file != 'workspace.zip':
                    file_path = os.path.join(os.path.relpath(root, path), file)
                    if file.lower() != "dockerfile" and any(
                            fnmatch(file_path, ignore.strip()) for ignore in ignored_entries):
                        debug('{} filtered out.'.format(file_path))
                        continue
                    ziph.write(os.path.join(self.context, file_path), arcname=file_path)
