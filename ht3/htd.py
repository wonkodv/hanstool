import socket
import os
import os.path
import threading

from ht3.command import run_command
from ht3.env import Env

_evt = threading.Event()

def loop():
    _evt.clear() # should be put somewhere else, can be race condition with stop
    fn = Env.get('SOCKET', os.path.expanduser('~/.config/ht3/socket'))
    if os.path.exists(fn):
        os.remove(fn)
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:

        sock.bind(fn)
        sock.settimeout(0.5)

        while not _evt.is_set():
            try:
                b = sock.recv(1024)
            except socket.timeout:
                continue

            s = b.decode('utf-8')
            try:
                run_command(s)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                Env.log_error(e)
                pass

def stop():
    _evt.set()
