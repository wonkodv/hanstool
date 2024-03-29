import os
import unittest
from unittest.mock import patch

from ht3.check import CHECK, Group, Value


class TestGroup(unittest.TestCase):
    def test_all(self):
        lst = ["x", "y"]
        g = Group(lst)

        assert g.x
        assert not g.z

        assert "x" in g
        assert "z" not in g

        assert g("x", "y")
        assert not g("x", "y", "z")
        assert not g("z")


class TestValue(unittest.TestCase):
    def test_all(self):
        x = 1
        v = Value(lambda: x)

        assert v
        x = 0
        assert not v

        x = 7
        assert v != 5
        assert v == 7


class TestCheck(unittest.TestCase):
    def test_basic_os(self):
        assert os.name in CHECK.os
        assert CHECK.os(os.name)

    def test_specific_os(self):
        if os.name == "nt":
            assert CHECK.os.win
            assert CHECK.os.windows
            assert CHECK.os.nt
        elif os.name == "posix":
            assert CHECK.os.posix
            # TODO: assert CHECK.os.linux

    def test_currnet_frontend(self):
        with patch("ht3.lib.THREAD_LOCAL") as fl:
            fl.frontend = "testfe"
            assert CHECK.current_frontend("testfe")
