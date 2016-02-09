import unittest
from ht3.utils.windows.execute import complete_executable
import os

@unittest.skipUnless(os.name == 'nt', "Not On Windows")
class TestWinPathCompl(unittest.TestCase):
    def test_it(self):
        p = list(complete_executable('python'))
        assert p[0][-4:].lower() == '.exe'
