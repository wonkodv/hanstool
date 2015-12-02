import unittest
import os

from ht3.check import Group, Value

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

class TestValue(unittest.TestCase):
    def test_all(self):
        x = True
        v = Value(lambda:x)

        assert x
        x = False
        assert not x

        x = 7
        assert x != 5
        assert x == 7
