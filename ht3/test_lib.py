import unittest
import unittest.mock
import time
from unittest.mock import patch, Mock

from ht3 import lib

class Test_frontends(unittest.TestCase):
    def get_fe(self, n):
        m = Mock()
        m.i = 0
        m.running = True
        def start():
            pass
        def loop():
            while m.running:
                m.i += 1

        def stop():
            m.running = False

        m.__name__ = n
        m.start = start
        m.loop = loop
        m.stop = stop
        return m

    @patch('importlib.import_module')
    def test_full_run(self, importMock):

        fe1 = self.get_fe('fe1')
        fe2 = self.get_fe('fe2')

        fe3 = Mock()
        fe3.loop = lambda:time.sleep(0.1)
        fe3.__name__ = 'fe3'

        importMock.side_effect = [fe1, fe2, fe3]

        lib.load_frontend('frontend1')
        lib.load_frontend('frontend2')
        lib.load_frontend('frontend3')

        lib.run_frontends()

        self.assertGreater(fe1.i, 100)
        self.assertGreater(fe2.i, 100)

