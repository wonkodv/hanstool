import os.path
import threading
import unittest
from unittest.mock import patch
import tempfile

from ht3.env import Env
import ht3.htd
import socket
import time


class TestDaemon(unittest.TestCase):
    @patch('ht3.htd.run_command')
    def test_daemon(self, run_command):
        with tempfile.TemporaryDirectory() as tmpd:
            sname = tmpd +'/socket'
            Env.SOCKET = sname

            ht3.htd.start()
            t = threading.Thread(target=ht3.htd.loop)
            t.start()

            while not os.path.exists(sname):
                time.sleep(0.05)

            s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            s.connect(sname)

            s.send(b'Test Foo')
            time.sleep(0.05)
            s.send(b'Test Bar')

            time.sleep(0.05)

            s.close()

            ht3.htd.stop()

            t.join()

        run_command.assert_any_call('Test Foo')
        run_command.assert_any_call('Test Bar')
