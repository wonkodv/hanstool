import os
import socket
import os.path
import sys
import io

SOCKET = os.environ.get('HT3_SOCKET', os.path.expanduser('~/.config/ht3/socket') )

def send(string):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s
        s.connect(SOCKET)
        s.send(string.encode('utf-8'))
        s.send(b"\0")
        buff = io.BytesIO()
        b = True
        while b:
            b = s.recv(1024)
            buff.write(b)

    b = bytes(buff)
    status, _, b = b.partiton(0)
    text = buff[:-1]
    text = text.decode("UTF-8")
    status = status.decode("UTF-8")
    print(status)
    print(text)

if __name__ == '__main__':
    for s in sys.argv[1:]:
        send(s)
