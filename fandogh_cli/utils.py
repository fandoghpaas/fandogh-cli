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
        with os.popen('stty size', 'r') as size:
            columns = size.read().split()[1]
            return int(columns)
    except Exception as exp:
        return None


def parse_key_values(key_values):
    env_variables = {}
    for env in key_values:

        if len(env.split('=', 1)) == 1:
            k = env
            if os.environ.get(k, default=None):
                env_variables[k] = os.environ.get(k)
            else:
                raise Exception('${} is not a valid environment variable'.format(k))
        else:
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


# !/usr/bin/env python
'''
A Python class implementing KBHIT, the standard keyboard-interrupt poller.
Works transparently on Windows and Posix (Linux, Mac OS X).  Doesn't work
with IDLE.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

'''

import os

# Windows
if os.name == 'nt':
    import msvcrt

# Posix (Linux, OS X)
else:
    import sys
    import termios
    import atexit
    from select import select


class KBHit:

    def __init__(self):
        '''Creates a KBHit object that you can call to do various keyboard things.
        '''

        if os.name == 'nt':
            pass

        else:

            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)

    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''

        if os.name == 'nt':
            pass

        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''

        s = ''

        if os.name == 'nt':
            return msvcrt.getch()
                # .decode('utf-8')

        else:
            return sys.stdin.read(1)

    def getarrow(self):
        ''' Returns an arrow-key code after kbhit() has been called. Codes are
        0 : up
        1 : right
        2 : down
        3 : left
        Should not be called in the same program as getch().
        '''

        if os.name == 'nt':
            msvcrt.getch()  # skip 0xE0
            c = msvcrt.getch()
            vals = [72, 77, 80, 75]

        else:
            c = sys.stdin.read(3)[2]
            vals = [65, 67, 66, 68]

        return vals.index(ord(c.decode('utf-8')))

    def kbhit(self):
        ''' Returns True if keyboard character was hit, False otherwise.
        '''
        if os.name == 'nt':
            return msvcrt.kbhit()

        else:
            dr, dw, de = select([sys.stdin], [], [], 0)
            return dr != []


# Test
if __name__ == "__main__":

    kb = KBHit()

    print('Hit any key, or ESC to exit')

    while True:

        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 27:  # ESC
                break
            print(c)

    kb.set_normal_term()

