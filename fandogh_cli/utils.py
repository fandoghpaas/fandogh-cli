from time import sleep

from fandogh_cli.config import load_token
import click
import os

FANDOGH_DEBUG = os.environ.get('FANDOGH_DEBUG', False)


def debug(msg):
    if FANDOGH_DEBUG:
        print(msg)


def login_required(fn):
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
