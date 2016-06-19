import unittest
import pathlib
from unittest.mock import Mock, patch
from ht3 import args

class TestStrParam(unittest.TestCase):
    def test_convert(self):
        p = args.Str
        s = "Test"
        assert p.convert(s) is s

    def test_complete(self):
        p = args.Str
        s = "Test"
        assert list(p.complete(s)) == []

class TestIntParam(unittest.TestCase):
    def test_convert(self):
        p = args.Int
        s = "0xf"
        assert p.convert(s) == 15

    def test_complete(self):
        p = args.Int
        s = "0"
        assert p.complete(s) is not None

class TestBoolParam(unittest.TestCase):
    def test_convert(self):
        p = args.Bool
        assert p.convert("No") is False
        assert p.convert("Yes") is True

    def test_complete(self):
        p = args.Bool
        assert "YES" in list(p.complete("YE"))
        assert "yes" in list(p.complete("y"))



class TestUnionParam(unittest.TestCase):
    def test_convert(self):
        p = args.Union(args.Bool, args.Int)
        assert p.convert("32") == 32
        assert p.convert("False") is False

    def test_complete(self):
        p = args.Union(args.Bool, args.Int)
        assert 'Yes' in list(p.complete(''))
        assert '0b'  in list(p.complete('0'))


class TestMultiParam(unittest.TestCase):
    def test_convert(self):
        p = args.MultiParam(args.Int)
        assert p.convert(["32", "42"]) == [32, 42]


    def test_complete(self):
        p = args.MultiParam(args.Bool)
        assert 'False' in list(p.complete(['FooBar', 'Fa']))


class TestSequence(unittest.TestCase):
    def test_convert(self):
        p = args.Sequence(args.Int, args.Float, args.Bool)
        assert p.convert(["32", "42", "no"]) == [32, 42.0, False]


    def test_complete(self):
        p = args.Sequence(args.Int, args.Float, args.Bool)
        assert 'no' in list(p.complete(["32", "42", "n"]))


class TestSingleArgParser(unittest.TestCase):
    def test_convert(self):
        def f(i:int):
            pass
        p = args.ArgParser(f)
        assert p.convert("123") == ([123],{})

    def test_complete(self):
        def f(i:args.Param(complete=lambda s:["asd fgh"])):
            pass
        p = args.ArgParser(f)
        assert list(p.complete("a")) == ["asd fgh"]

class TestShellArgParser(unittest.TestCase):
    def test_convert(self):
        def f(i:int, b:bool, s):
            pass
        p = args.ArgParser(f)
        assert p.convert("'123' 'No' 'Tes't' 'T'ext'") == ([123, False, "Test Text"],{})
        assert p.convert("123 No 42.42") == ([123, False, "42.42"],{})

    def test_complete(self):
        def f(i:int, s:args.Param(complete=[
                        "ws text",
                        "text",
                        "singlequote's",
                        'doublequote"s'])):
            pass
        p = args.ArgParser(f)
        assert list(p.complete("1 text")) == ["1 text"]
        assert list(p.complete('1 ')) == ['1 "ws text"', "1 text", "singlequote's", 'doublequote"s']
        assert list(p.complete('1 "w')) == ['1 "ws text"']
        assert list(p.complete('1 w')) == ['1 ws\\ text']
