import socket
import threading
import time
import unittest

import ht3client
import ht3.daemon

from ht3.env import Env
from unittest.mock import patch, Mock

class TestDaemon(unittest.TestCase):

    @patch('ht3.daemon.socket_info')
    @patch('ht3.daemon.run_command')
    def test_daemon(self, run_command, socket_info_server):
        socket_info = [socket.AF_INET, ('localhost', 42267)]
        socket_info_server.return_value = socket_info

        run_command.return_value = 4267

        Env['log'] = Mock()

        ht3.daemon.start()
        t = threading.Thread(target=ht3.daemon.loop)
        t.start()

        time.sleep(0.05)

        with ht3client.HT3Client(*socket_info) as htc:
            r = htc.command("Test Bar")

        ht3.daemon.stop()

        t.join()

        assert r == 4267
        run_command.assert_any_call('Test Bar')
