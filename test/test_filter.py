import unittest
import os

from ht3.filter import Filter, Group, Value

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
            assert Filter.os.linux_4_2

class TestGroup(unittest.TestCase):
    def test_ListGroup(self):
        l = ['x', 'y']
        g = Group(l)

        assert g.x
        assert 'y' in g

        assert not 'z' in g

    def dict_filter(self):
        d = {'x':1, 'y': 'Test'}
        g = group(d)

        assert g.x
        assert g.x == 1
        assert g.x < 3
        assert g.x > 0
