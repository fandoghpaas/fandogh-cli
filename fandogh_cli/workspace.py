import os
import tarfile
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
        self.tar_file_name = os.path.join(self.path, 'workspace.tar.gz')
        files = os.listdir(self.path)
        self.has_docker_ignore = '.dockerignore' in files or '.fandoghignore' in files
        self.has_docker_file = 'Dockerfile' in files
        self._create_tar_file()
        self.tar_file_size_kb = os.path.getsize(self.tar_file_name)
        self.tar_file_size = self.tar_file_size_kb / 1048576

    def _create_tar_file(self):
        tarf = tarfile.open(name=self.tar_file_name, mode='w:gz')
        self.tardir(self.path, tarf)
        tarf.close()

    def clean(self):
        if os.path.exists(self.tar_file_name):
            os.remove(self.tar_file_name)

    def __str__(self):
        return self.tar_file_name

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        return str(self)

    def get_ignored_entries(self):
        ignore_files = ('.dockerignore', '.fandoghignore')
        entries = []
        for ignore_file in ignore_files:
            ignore_file_path = os.path.join(self.path, ignore_file)
            if os.path.exists(ignore_file_path):
                with open(ignore_file_path, 'r') as file:
                    entries = [line for line in file.readlines() if line.strip() and not line.startswith('#')]
        entries = self.add_custom_ignore_folder_to_entries(entries, [".git/", ".git"])
        expand_entries = []
        for entry in entries:
            expand_entries.append(entry.strip() + os.sep + '*')
        entries = entries + expand_entries
        for index, entry in enumerate(entries):
            if entry.startswith("/"):
                entries[index] = entry[1:]

        return entries

    def tardir(self, path, tarh):
        ignored_entries = self.get_ignored_entries()
        ignored_entries.append('*dockerignore')
        debug(ignored_entries)
        for root, dirs, files in os.walk(path):
            for file in files:
                if file != 'workspace.tar.gz':

                    file_path = os.path.join(os.path.relpath(root, path), file)

                    if file.lower() != "dockerfile" and any(
                            fnmatch(file_path, ignore.strip()) for ignore in ignored_entries):
                        debug('{} filtered out.'.format(file_path))
                        continue
                    tarh.add(os.path.join(self.context, file_path), arcname=file_path)

    @staticmethod
    def add_custom_ignore_folder_to_entries(entries, ignore_folders):
        for folder in ignore_folders:
            if folder not in entries:
                entries.append(folder)
        return entries
