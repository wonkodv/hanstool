import os
import os.path
import pickle
import re
import socket
import threading

import ht3.lib
from ht3.command import run_command
from ht3.complete import complete_command_with_args
from ht3.env import Env

RE_INET6 = re.compile(r"\[([\d:]+)\]:(\d+)")
RE_INET = re.compile(r"(\d+\.\d+\.\d+\.\d+):(\d+)")


def socket_info():
    """Parse Address from DAEMON_ADDRESS as ipv4, ipv6 or socket

    *   IPv4 Format must be like 127.0.0.1:4267
    *   IPv6 Format must be like [::1]:4267
    *   On Windows it must be one of the above
    *   For a unix socket, it must be a path
    """

    adr = Env.get("DAEMON_ADDRESS", None)
    if adr is None:
        if hasattr(socket, "AF_UNIX"):
            adr = os.path.expanduser("~/.config/ht3/socket")
            typ = socket.AF_UNIX
        else:
            adr = ("::1", 4267)
            typ = socket.AF_INET6
    else:
        m = RE_INET6.match(adr)
        if m:
            typ = socket.AF_INET6
            adr = tuple(m.groups())
        else:
            m = RE_INET.match(adr)
            if m:
                typ = socket.AF_INET
                adr = tuple(m.groups())
            else:
                if hasattr(socket, "AF_UNIX"):
                    typ = socket.AF_UNIX
                    adr = os.path.expanduser(adr)
                else:
                    raise ValueError(
                        "Misformed Address, should look like "
                        "'127.0.0.1:4267' or '[::1]:4267'",
                        adr,
                    )
    if typ is getattr(socket, "AF_UNIX", object()):
        if os.path.exists(adr):
            os.remove(adr)
    return typ, adr


def handle_socket(sock, addr):
    ht3.lib.THREAD_LOCAL.frontentd = "{}({})".format(__name__, addr)
    with sock:
        sock.settimeout(0.1)
        with sock.makefile("wrb") as sock_file:
            try:
                cmd, string = pickle.load(sock_file)
                if cmd == "COMMAND":
                    r = run_command(string)
                    try:
                        obj = ("OK", "RESULT", r)
                        pickle.dump(obj, sock_file)
                    except Exception:
                        obj = ("OK", "REPR", repr(r))
                        pickle.dump(obj, sock_file)
                elif cmd == "COMPLETE":
                    for c in complete_command_with_args(string):
                        obj = ("OK", "COMPLETION", c)
                        pickle.dump(obj, sock_file)
                    obj = ("OK", "COMPLETION-DONE", None)
                    pickle.dump(obj, sock_file)
                elif cmd == "PING":
                    obj = ("OK", "PONG", None)
                    pickle.dump(obj, sock_file)
                else:
                    obj = ("BAD-COMMAND", cmd)
                    pickle.dump(obj, sock_file)
            except (BrokenPipeError, EOFError, socket.timeout):
                pass
            except SystemExit:
                obj = ("OK", "EXIT", None)
                pickle.dump(obj, sock_file)
                raise
            except Exception as e:
                obj = ("EXCEPTION", e, None)
                try:
                    pickle.dump(obj, sock_file)
                except Exception:
                    pass
                ht3.lib.EXCEPTION_HOOK(exception=e)


_evt = None


def start():
    global _evt
    _evt = threading.Event()


def loop():
    typ, adr = socket_info()
    with socket.socket(typ, socket.SOCK_STREAM) as sock:
        sock.bind(adr)
        Env.log(f"ht3.daemon: Listening on {adr}")
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
                except Exception:
                    pass


def stop():
    _evt.set()
