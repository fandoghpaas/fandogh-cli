from time import sleep
import click
import os

FANDOGH_DEBUG = os.environ.get('FANDOGH_DEBUG', False)


def is_python2():
    import sys
    return sys.version_info[0] == 2


def debug(msg):
    if FANDOGH_DEBUG:
        print(msg)


def login_required(fn):
    # TODO: Move out of utils
    from fandogh_cli.config import load_token
    def please_login_first(*args, **kwargs):
        click.echo('In order to use this command, you need to login first')

    token_obj = load_token()
    if token_obj is None:
        return please_login_first
    return fn


def do_every(seconds, task, while_condition=lambda: True):
    while while_condition():
        task()
        sleep(seconds)


def makedirs(name, mode=0660, exist_ok=True):
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
                except OSError, e:
                    if e.errno != os.errno.EEXIST and not exist_ok:
                        raise
                if tail == os.curdir:
                    return
            os.mkdir(name, mode)
        _makedirs(name, mode)
