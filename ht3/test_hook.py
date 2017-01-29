from .hook import *
import unittest
import unittest.mock
import sys

class TestHook(unittest.TestCase):
    def test_hook(self):
        h = Hook("x")

        X = []
        @h.register
        def callback(x):
            X.append(x)
            return x

        h(x=1)
        assert X == [1]

        h(x=2)
        assert X == [1,2]

    @unittest.skipIf(sys.version_info < (3,5), "signature(follow_wrapped) not implemented")
    def test_signature_check(self):
        h = Hook("a","b")

        with self.assertRaises(TypeError):
            @h.register
            def callback(a,b,c): pass
        with self.assertRaises(TypeError):
            @h.register
            def callback(x, y): pass
        with self.assertRaises(TypeError):
            @h.register
            def callback(a): pass

        @h.register
        def callback(a,b,*c): pass


class TestResultHook(unittest.TestCase):
    def test_result_hook(self):
        h = ResultHook()

        @h.register
        def no0():
            return 0
        @h.register
        def no1():
            return 1
        @h.register
        def no2():
            return None
        @h.register
        def no3():
            return None

        assert h() == 1


