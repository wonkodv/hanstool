"""Client to ht3.daemon.

execute with "--help" for usage info.
"""
import pickle
import os
import socket
import os.path
import sys
import io
import argparse
import traceback

class RemoteException(Exception):
    pass

def socket_info():
    """Parse Address from DAEMON_ADDRESS as ipv4, ipv6 or socket

    *   IPv4 Format must be like 127.0.0.1:4267
    *   IPv6 Format must be like [::1]:4267
    *   On Windows it must be one of the above
    *   For a unix socket, it must be a path
    """

    adr = os.environ.get('DAEMON_ADDRESS', None)
    if adr is None:
        if hasattr(socket,'AF_UNIX'):
            adr = os.path.expanduser('~/.config/ht3/socket')
            typ = socket.AF_UNIX
        else:
            adr = ('::1', 4267)
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
                if hasattr(socket,'AF_UNIX'):
                    typ = socket.AF_UNIX
                    adr = os.path.expanduser(adr)
                else:
                    raise ValueError("Misformed Address, should look like "
                            "'127.0.0.1:4267' or '[::1]:4267'", adr)
    return typ, adr


def send(command, string):
    typ, adr = socket_info()
    with socket.socket(typ, socket.SOCK_STREAM) as sock:
        sock.connect(adr)
        with sock.makefile("rwb") as sock_file:
            pickle.dump([command, string], sock_file)
            sock_file.flush()
            while True:
                try:
                    yield pickle.load(sock_file)
                except EOFError:
                    return

def complete(s):
    for s, t, r in send("COMPLETE", s):
        if s != "OK" or t != "COMPLETION":
            raise TypeError(s, t,r)
        elif s == 'EXCEPTION':
            raise RemoteException(t)
        else:
            yield r

def command(s):
    s, t, r = next(send("COMMAND", s))
    if s == "OK" and t in ("RESULT", "REPR", "EXIT"):
        return r
    elif s == 'EXCEPTION':
        raise RemoteException(t)
    else:
        raise TypeError(s,t,r)


def main(options):
    try:
        if options.complete:
            r = complete(options.command)
            for l in r:
                print (l)
        else:
            r = command(options.command)
            if r is not None:
                print(r)
    except RemoteException as e:
        print(e.args[0], file=sys.stderr)
    except Exception as e:
        if options.quiet:
            print(e, file=sys.stderr)
        else:
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="Client for ht3.daemon")
    p.add_argument("-c", "--complete", action='store_true')
    p.add_argument("-q", "--quiet", action='store_true')
    p.add_argument("command")
    o = p.parse_args()
    sys.exit(main(o))
