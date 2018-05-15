from time import sleep
import click
import os

FANDOGH_DEBUG = os.environ.get('FANDOGH_DEBUG', False)


def is_python2():
    import sys
    return sys.version_info[0] == 2


def debug(msg):
    if FANDOGH_DEBUG:
        click.echo(msg)


def login_required(fn):
    # TODO: Move out of utils
    from fandogh_cli.config import load_token

    def please_login_first(*args, **kwargs):
        click.echo("Please login first. You can do it by running 'fandogh login' command")

    token_obj = load_token()
    if token_obj is None:
        return please_login_first
    return fn


def makedirs(name, mode=0o770, exist_ok=True):
    if not is_python2():
        os.makedirs(name, mode, exist_ok)
    else:
        def _makedirs(name, mode):
            head, tail = os.path.split(name)
            if not tail:
                head, tail = os.path.split(head)
            if head and tail and not os.path.exists(head):
                try:
                    _makedirs(head, mode)
                except OSError as e:
                    if e.errno != os.errno.EEXIST and not exist_ok:
                        raise
                if tail == os.curdir:
                    return
            os.mkdir(name, mode)

        _makedirs(name, mode)
