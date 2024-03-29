import sys

if sys.platform == "win32":
    import unittest
    from ctypes import c_size_t, c_void_p

    from . import functions

    if hasattr(functions, "__all__"):
        del functions.__all__  # import EVERYTHING
        from .functions import *

    class TestLoad(unittest.TestCase):
        def test_load(self):
            @load(windll.kernel32)
            def GlobalAlloc(uFlafs: UINT, dwBytes: c_size_t) -> c_void_p:
                pass

            b = GlobalAlloc(0x40, 100)
            assert int(b) != 0

            with self.assertRaises(OSError):
                GlobalAlloc(7, 0)

            assert not GetLastError()
