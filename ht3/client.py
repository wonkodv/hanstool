import os
import socket
import os.path
import sys

SOCKET = os.environ.get('HT3_SOCKET', os.path.expanduser('~/.config/ht3/socket') )

def send(string):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    s.connect(SOCKET)
    s.send(string.encode('utf-8'))
    s.close()

if __name__ == '__main__':
    for s in sys.argv[1:]:
        send(s)
