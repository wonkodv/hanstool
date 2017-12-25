import pickle
import os
import socket
import os.path
import sys
import io


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
                    status, result = pickle.load(sock_file)
                    if status != "OK":
                        raise result
                    yield result
                except EOFError:
                    return

def complete(s):
    yield from send("COMPLETE", s)

def command(s):
    return next(send("COMMAND", s))


def main(argv):
    if len(argv) == 1:
        c = argv[0]
        try:
            r = command(c)
        except Exception as e:
            print(e, file=sys.stderr)
        else:
            if r is not None:
                print(r)
    elif len(argv) == 2 and argv[0] == "-c":
        c = argv[1]
        r = complete(c)
        for l in r:
            print (l)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

