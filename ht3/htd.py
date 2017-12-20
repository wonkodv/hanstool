import traceback
import pickle
import socket
import os
import os.path
import threading
import io

import ht3.lib

from ht3.command import run_command
from ht3.env import Env
from ht3.complete import complete_command_with_args


def handle_socket(sock, addr):
    ht3.lib.THREAD_LOCAL.frontentd = "{}({})".format(__name__,addr)
    with sock:
        with sock.makefile("wrb") as sock_file:
            try:
                cmd, string = pickle.load(sock_file)
                if cmd == "COMMAND":
                    r = run_command(string)
                    obj = ("OK", r)
                    pickle.dump(obj, sock_file)
                elif cmd == "COMPLETE":
                    for c in complete_command_with_args(string):
                        pickle.dump(("OK",c), sock_file)
                else:
                    raise ValueError(cmd)
            except Exception as e:
                obj = ["EXCEPTION",e]
                try:
                    pickle.dump(obj, sock_file)
                except:
                    pass
                lib.EXCEPTION_HOOK(exception=e)

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
                try:
                    handle_socket(conn, addr)
                except:
                    pass

def stop():
    _evt.set()
