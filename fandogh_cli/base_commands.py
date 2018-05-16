import click
from click import Command

from fandogh_cli.fandogh_client import FandoghAPIError, AuthenticationError
from fandogh_cli.utils import debug


class FandoghCommand(Command):
    def invoke(self, ctx):
        try:
            return super(FandoghCommand, self).invoke(ctx)
        except (FandoghAPIError, AuthenticationError) as exp:
            debug('APIError. status code: {}, content: {}'.format(
                exp.response.status_code,
                exp.response.content))
            click.echo(exp.message, err=True)
        except Exception as exp:
            raise exp
