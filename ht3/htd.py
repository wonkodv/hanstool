import socket
import os
import os.path
import threading

from ht3.command import run_command
from ht3.env import Env

_evt = threading.Event()

def start():
    _evt.clear()

def loop():
    fn = Env.get('SOCKET', os.path.expanduser('~/.config/ht3/socket'))
    if os.path.exists(fn):
        os.remove(fn)

    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
        sock.bind(fn)
        sock.settimeout(0.5)

        while True:
            try:
                b = sock.recv(1024)
            except socket.timeout:
                if _evt.is_set():
                    return
                continue

            s = b.decode('utf-8')
            try:
                run_command(s)
            except Exception as e:
                Env.log_error(e)
                pass

def stop():
    _evt.set()
