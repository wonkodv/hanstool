import unittest
import unittest.mock
import time
import os
from unittest.mock import patch, Mock, MagicMock

from ht3 import lib

class Test_frontends(unittest.TestCase):
    def test_import_recursive(self):
        m = lib.import_recursive('unittest.mock')
        self.assertIs(m, unittest.mock)

    def get_fe(self, n):
        m = Mock()
        m.i = 0
        m.running = True
        def start():
            while m.running:
                m.i += 1

        def stop():
            m.running = False

        m.__name__ = n
        m.loop = start
        m.stop = stop
        return m

    @patch('ht3.lib.import_recursive')
    def test_full_run(self, importMock):

        fe1 = self.get_fe('fe1')
        fe2 = self.get_fe('fe2')

        fe3 = Mock()
        fe3.stop = lambda:None
        fe3.loop = lambda:time.sleep(0.1)
        fe3.__name__ = 'fe3'

        importMock.side_effect = [fe1, fe2, fe3]

        lib.load_frontend('frontend1')
        lib.load_frontend('frontend2')
        lib.load_frontend('frontend3')

        lib.run_frontends()

        self.assertGreater(fe1.i, 100)
        self.assertGreater(fe2.i, 100)

class Test_check(unittest.TestCase):
    def test_basic_os(self):
        assert os.name in lib.Check.os
        assert lib.Check.os(os.name)

    def test_basic_os(self):
        if os.name == 'nt':
            assert lib.Check.os.win
            assert lib.Check.os.windows
            assert lib.Check.os.nt
        elif os.name == 'posix':
            assert lib.Check.os.posix
            #TODO: assert Check.os.linux

    def test_currnet_frontend(self):
        with self.assertRaises(AttributeError):
            lib.Check.current_frontend('ht3.cli')
        with patch('ht3.lib.FRONTEND_LOCAL') as fl:
            fl.frontend='testfe'
            assert lib.Check.current_frontend('testfe')

