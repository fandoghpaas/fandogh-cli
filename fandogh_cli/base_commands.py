from datetime import datetime, timedelta

import click
from click import Command
from fandogh_cli import NAME
from fandogh_cli.fandogh_client import FandoghAPIError, AuthenticationError
from fandogh_cli.utils import debug, TextStyle, format_text
from fandogh_cli.version_check import get_latest_version, get_current_version, Version
from fandogh_cli.config import get_user_config


class VersionException(Exception):
    pass


class FandoghCommand(Command):
    def invoke(self, ctx):
        try:
            self._check_for_new_version()
            return super(FandoghCommand, self).invoke(ctx)
        except (FandoghAPIError, AuthenticationError) as exp:
            debug('APIError. status code: {}, content: {}'.format(
                exp.response.status_code,
                exp.response.content))
            click.echo(format_text(exp.message, TextStyle.FAIL), err=True)
        except VersionException as exp:
            click.echo(format_text("New Version of {} is available, please update to continue "
                                   "using Fandogh services using : `pip install {} --upgrade`".format(NAME, NAME),
                                   TextStyle.FAIL))
        except Exception as exp:
            raise exp

    def _check_for_new_version(self):
        latest_version = self._get_latest_version()
        version_diff = get_current_version().compare(latest_version)
        if version_diff < -2:  # -1:Major -2:Minor -3:Patch
            click.echo(format_text("New version is available, "
                                   "please update to new version"
                                   " using `pip install {} --upgrade` to access latest bugfixes".format(NAME),
                                   TextStyle.WARNING))
            debug("New Version is available: {}".format(latest_version))
        elif version_diff < 0:
            debug("New Version is available: {}".format(latest_version))
            raise VersionException()

    def _get_latest_version(self):
        cached_version_info = get_user_config().get("version_info")
        if cached_version_info is None:
            latest_version = get_latest_version()
            last_check = datetime.now()
        else:
            last_check, latest_version = cached_version_info.get('last_check', None), Version(
                cached_version_info.get('latest_version', None))
            if latest_version is None or (datetime.now() - last_check) > timedelta(hours=6):
                latest_version = get_latest_version()
                last_check = datetime.now()
        get_user_config().set("version_info", dict(last_check=last_check, latest_version=str(latest_version)), )
        return latest_version
