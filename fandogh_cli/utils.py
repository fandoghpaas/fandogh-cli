import click
import os

from datetime import datetime

import pytz
import tzlocal

FANDOGH_DEBUG = os.environ.get('FANDOGH_DEBUG', False)
USER_TIMEZONE = pytz.timezone(tzlocal.get_localzone().zone)


def is_python2():
    import sys
    return sys.version_info[0] == 2


def debug(msg):
    if FANDOGH_DEBUG:
        click.echo(msg)


def makedirs(name, mode=0o770, exist_ok=True):
    if not is_python2():
        os.makedirs(name, mode, exist_ok)
    else:
        try:
            os.makedirs(name, mode)
        except OSError as e:
            if not exist_ok:
                raise e


class TextStyle:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def format_text(text, style):
    return "{}{}{}".format(style, text, TextStyle.ENDC)


def convert_datetime(datetime_value):
    return str(USER_TIMEZONE.fromutc(datetime.strptime(datetime_value, "%Y-%m-%dT%H:%M:%SZ")))
