import os
import subprocess
import sys
import unittest

from .process import execute, shellescape


def helper(*args, **kwargs):
    p = execute(
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        errors="replace",
        env=dict([("TEST", "hans")] + list(os.environ.items())),
        **kwargs
    )
    return p


class TestProcess(unittest.TestCase):
    if sys.platform == "win32":

        def test_excecute(self):
            p = helper(sys.executable, "-c", "print('%TEST%')")
            t, e = p.communicate()
            assert t.strip() == "%TEST%"

        def test_excecute_split(self):
            p = helper(sys.executable, "-c", "print('%TEST%')", is_split=True)
            t, e = p.communicate()
            assert t.strip() == "%TEST%"

        def test_excecute_shell(self):
            p = helper('"' + sys.executable + '" -c "print(\'%TEST%\')"', shell=True)
            t, e = p.communicate()
            assert t.strip() == "hans", [t, e, p]

    else:

        def test_excecute(self):
            p = helper(sys.executable, "-c", "print('$TEST')")
            t, e = p.communicate()
            assert t.strip() == "$TEST"

        def test_excecute_split(self):
            p = helper(sys.executable, "-c", "print('$TEST')", is_split=True)
            t, e = p.communicate()
            assert t.strip() == "$TEST"

        def test_excecute_shell(self):
            p = helper(
                shellescape(sys.executable) + " -c \"print('$TEST')\"", shell=True
            )
            t, e = p.communicate()
            assert t.strip() == "hans"

    def test_excecute_nosplit_err(self):
        with self.assertRaises(TypeError):
            helper("a", "b", is_split=False)

    def test_excecute_shell_split(self):
        with self.assertRaises(TypeError):
            helper("a", "b", is_split=True, shell=True)

    def test_excecute_shell_split2(self):
        with self.assertRaises(TypeError):
            helper("a", "b", shell=True)
