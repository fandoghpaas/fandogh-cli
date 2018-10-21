from string import Template
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


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def convert_datetime(datetime_value):
    if datetime_value:
        return str(USER_TIMEZONE.fromutc(datetime.strptime(datetime_value, DATETIME_FORMAT)))
    return None


def get_window_width():
    try:
        with os.popen('stty size', 'r') as  size:
            columns = size.read().split()[1]
            return int(columns)
    except Exception as exp:
        return None


def parse_key_values(key_values):
    env_variables = {}
    for env in key_values:
        (k, v) = env.split('=', 1)
        env_variables[k] = v
    return env_variables


def process_template(template, mapping):
    return Template(template).substitute(**mapping)


def trim_comments(manifest):
    lines = []
    for line in manifest.split("\n"):
        if not line.strip().startswith("#"):
            lines.append(line)
    return "\n".join(lines)


def read_manifest(manifest_file, parameters):
    try:
        with open(manifest_file, mode='r') as manifest:
            rendered_manifest = process_template(
                manifest.read(),
                parse_key_values(
                    parameters
                )
            )
        return trim_comments(rendered_manifest)
    except IOError as e:
        click.echo(format_text(e.strerror, TextStyle.FAIL), err=True)
    except KeyError as missing_parameter:
        click.echo(format_text("you need to provide value for {} in order to deploy this manifest",
                               TextStyle.FAIL).format(missing_parameter))
