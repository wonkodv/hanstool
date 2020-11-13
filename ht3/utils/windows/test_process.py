import unittest
from unittest.mock import patch
from ht3.utils.windows.process import complete_executable, execute
import os
import sys


@unittest.skipUnless(os.name == "nt", "Windows Test")
class TestWinExecute(unittest.TestCase):
    def test_complete(self):
        p = list(complete_executable("expl"))
        assert "explorer" in p

    @patch("ht3.utils.process.Env")
    def test_execute(self, Env):
        p = execute(sys.executable, "-c", "import sys; sys.exit(42)")
        p.wait()
        assert p.returncode == 42
