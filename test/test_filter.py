import unittest
import os

from ht3.filter import Filter, Group

class TestFilter(unittest.TestCase):
    def test_basic_os(self):
        assert os.name in Filter.os

    def test_basic_os(self):
        if os.name == 'nt':
            assert Filter.os.win
            assert Filter.os.windows
            assert Filter.os.nt
        elif os.name == 'posix':
            assert Filter.os.posix
            #TODO: assert Filter.os.linux

class TestGroup(unittest.TestCase):
    def test_all(self):
        l = ['x', 'y']
        g = Group(l)

        assert g.x
        assert not g.z

        assert 'x' in g
        assert not 'z' in g

        assert g('x','y')
        assert not g('x', 'y', 'z')
        assert not g('z')
