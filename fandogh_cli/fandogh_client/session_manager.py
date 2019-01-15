#!/usr/bin/env python

import sys
import threading
import six
import websocket
from fandogh_cli.fandogh_client import fandogh_ssh_host
import click

from fandogh_cli.utils import KBHit


def get_encoding():
    encoding = getattr(sys.stdin, "encoding", "")
    if not encoding:
        return "utf-8"
    else:
        return encoding.lower()


OPCODE_DATA = (websocket.ABNF.OPCODE_TEXT, websocket.ABNF.OPCODE_BINARY)
ENCODING = get_encoding()


class RawInput:
    def raw_input(self, prompt):
        if six.PY3:
            line = input(prompt)
        else:
            line = raw_input(prompt)

        if ENCODING and ENCODING != "utf-8" and not isinstance(line, six.text_type):
            line = line.decode(ENCODING).encode("utf-8")
        elif isinstance(line, six.text_type):
            line = line.encode("utf-8")

        return line


class NonInteractive(RawInput):

    def write(self, data):
        sys.stdout.write(data)
        # sys.stdout.write("\n")
        sys.stdout.flush()

    def read(self):
        return self.raw_input("")


def start_session(session_key):
    try:
        kbhit = KBHit()
        # if not sys.stdin.isatty():
        #     raise Exception('tty stdin is needed!')
        # fd = sys.stdin.fileno()
        # mode = tty.tcgetattr(fd)
        # tty.setraw:q

        options = {
            'header': {
                'SESSION-KEY': session_key
            }
        }

        opts = {}
        ws = websocket.create_connection(fandogh_ssh_host + '/session', sslopt=opts, **options)

        console = NonInteractive()

        def recv():
            try:
                frame = ws.recv_frame()
            except websocket.WebSocketException:
                return websocket.ABNF.OPCODE_CLOSE, None
            if not frame:
                raise websocket.WebSocketException("Not a valid frame %s" % frame)
            elif frame.opcode in OPCODE_DATA:
                return frame.opcode, frame.data
            elif frame.opcode == websocket.ABNF.OPCODE_CLOSE:
                ws.send_close()
                return frame.opcode, None
            elif frame.opcode == websocket.ABNF.OPCODE_PING:
                ws.pong(frame.data)
                return frame.opcode, frame.data

            return frame.opcode, frame.data

        def recv_ws():
            while True:
                opcode, data = recv()
                msg = None
                if six.PY3 and opcode == websocket.ABNF.OPCODE_TEXT and isinstance(data, bytes):
                    data = str(data, "utf-8")
                if opcode in OPCODE_DATA:
                    msg = data

                if msg is not None:
                    console.write(msg)

                if opcode == websocket.ABNF.OPCODE_CLOSE:
                    break

        thread = threading.Thread(target=recv_ws)
        thread.daemon = True
        thread.start()

        while True:
            try:
                kbhit.kbhit()
                message = kbhit.getch()
                ws.send(message)
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    except websocket.WebSocketConnectionClosedException as e:
        click.echo('Connection has been closed...')
    finally:
        kbhit.set_normal_term()
        # tty.tcsetattr(fd, tty.TCSAFLUSH, mode)


if __name__ == "__main__":
    try:
        start_session()
    except Exception as e:
        print(e)
