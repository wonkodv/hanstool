import socket
import threading
import time
import unittest

import ht3.daemon

from ht3.env import Env
from ht3.client import command
from unittest.mock import patch

class TestDaemon(unittest.TestCase):

    @patch('ht3.daemon.socket_info')
    @patch('ht3.client.socket_info')
    @patch('ht3.daemon.run_command')
    def test_daemon(self, run_command, socket_info_client, socket_info_server):
        socket_info_client.return_value = [socket.AF_INET, ('localhost', 42267)]
        socket_info_server.return_value = [socket.AF_INET, ('localhost', 42267)]
        run_command.return_value = 4267


        ht3.daemon.start()
        t = threading.Thread(target=ht3.daemon.loop)
        t.start()

        time.sleep(0.05)

        r = command("Test Bar")

        ht3.daemon.stop()

        t.join()

        assert r == 4267
        run_command.assert_any_call('Test Bar')