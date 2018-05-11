from fandogh_cli.config import load_token
import click


def login_required(fn):
    def please_login_first(*args, **kwargs):
        click.echo('In order to use this command, you need to login first')
    token_obj = load_token()
    if token_obj is None:
        return please_login_first
    return fn
