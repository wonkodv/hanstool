import pickle
import os
import socket
import os.path
import sys
import io

SOCKET = os.environ.get('HT3_SOCKET', os.path.expanduser('~/.config/ht3/socket') )

def send(command, string, socket_path=SOCKET):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(socket_path)
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

def complete(*args, **kwargs):
    yield from send("COMPLETE", *args, **kwargs)

def command(*args, **kwargs):
    return next(send("COMMAND", *args, **kwargs))


def main(argv):
    if len(argv) == 1:
        c = argv[0]
        r = command(c)
        print (r)
    elif len(argv) == 2 and argv[0] == "-c":
        c = argv[1]
        r = complete(c)
        for l in r:
            print (l)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

