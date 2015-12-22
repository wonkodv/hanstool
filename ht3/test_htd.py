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

            t = threading.Thread(target=ht3.htd.loop)
            t.start()

            time.sleep(0.01)

            s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            s.connect(sname)

            s.send(b'Test Fooo')
            s.send(b'Test Bar')
            s.close()

            ht3.htd.stop()

        run_command.assert_was_called_with('Test Foo')
        run_command.assert_was_called_with('Test Bar')
