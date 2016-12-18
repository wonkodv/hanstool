import socket
import os
import os.path
import threading
import io

import ht3.lib

from ht3.command import run_command
from ht3.env import Env


def handle_socket(sock, addr):
    ht3.lib.THREAD_LOCAL.frontentd = "{}({})".format(__name__,addr)
    buff = io.BytesIO()
    b=True
    with sock:
        while b:
            try:
                b = sock.recv(1024)
            except socket.timeout:
                return
            buff.write(b)

        s = bytes(buff).decode("UTF-8")

        try:
            r = run_command(s)
        except Exception as e:
            sock.send(b"EXCEPTION\0")
            sock.send(traceback.format_exc().encode("UTF-8"))
            sock.send(b"\0")
            lib.EXCEPTION_HOOK(exception=e)
        else:
            sock.send(b"OK\0")
            sock.send(repr(r).encode("UTF-8"))
            sock.send(b"\0")

_evt = None

def start():
    global _evt
    _evt = threading.Event()

def loop():
    fn = Env.get('SOCKET', os.path.expanduser('~/.config/ht3/socket'))
    if os.path.exists(fn):
        os.remove(fn)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.bind(fn)
        sock.settimeout(0.5)
        sock.listen(0)

        while True:
            try:
                conn, addr = sock.accept()
            except socket.timeout:
                if _evt.is_set():
                    return
            else:
                handle_socket(conn, addr)

def stop():
    _evt.set()
