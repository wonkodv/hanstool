import os.path
import socket
import tempfile
import threading
import time
import unittest

import ht3.htd

from ht3.env import Env
from ht3.client import send
from unittest.mock import patch

@unittest.skipUnless(os.name == 'posix',"Not on POSIX")
class TestDaemon(unittest.TestCase):

    @patch('ht3.htd.run_command')
    def test_daemon(self, run_command):
        with tempfile.TemporaryDirectory() as tmpd:
            sname = tmpd +'/socket'
            Env['SOCKET'] = sname

            ht3.htd.start()
            t = threading.Thread(target=ht3.htd.loop)
            t.start()

            while not os.path.exists(sname):
                time.sleep(0.05)

            send("Test Bar", socket_path=sname)

            ht3.htd.stop()

            t.join()

        run_command.assert_any_call('Test Bar')
