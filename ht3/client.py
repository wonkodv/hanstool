import pickle
import os
import socket
import os.path
import sys
import io

SOCKET = os.environ.get('HT3_SOCKET', os.path.expanduser('~/.config/ht3/socket') )

def send(string, socket_path=SOCKET):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(socket_path)
        with sock.makefile("rwb") as sock_file:
            pickle.dump(string, sock_file)
            sock_file.flush()
            status, result = pickle.load(sock_file)
    return status, result

if __name__ == '__main__':
    for c in sys.argv[1:]:
        print(c)
        s, r = send(c)
        print (s)
        print (r)

