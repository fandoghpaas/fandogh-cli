import fnmatch
import os
import click


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def wsgi_name_hint():
    cwd = os.getcwd()
    candidates = find_files(os.getcwd(), '*wsgi*.py')
    candidates = map(lambda candidate: candidate[len(cwd) + 1:-3], candidates)
    candidates = map(lambda candidate: candidate.replace('/', '.'), candidates)
    click.echo('Possible wsgi modules are:')
    for candidate in candidates:
        click.echo(' - {}'.format(candidate))
