import unittest
import pathlib
import sys
from unittest.mock import Mock, patch
from ht3 import args


class TestParamClass(unittest.TestCase):
    def test_realpc(self):
        class cls(args.ParamClass):
            pass

        assert issubclass(cls, args.ParamClass)

    def test_virtualPC(self):
        class cls:
            @classmethod
            def convert(cls, s):
                return s

            @classmethod
            def complete(cls, s):
                return s
        assert issubclass(cls, args.ParamClass)

    def test_virtual_no_class_methods(self):
        class cls:
            def convert(self, s):
                return s

            def complete(self, s):
                return s
        assert not issubclass(cls, args.ParamClass)

    def test_virtual_pc_no_complete(self):
        class cls():
            @classmethod
            def convert(cls, s):
                pass
        assert not issubclass(cls, args.ParamClass)

    def test_virtual_pc_no_convert(self):
        class cls():
            @classmethod
            def complete(cls, s):
                pass
        assert not issubclass(cls, args.ParamClass)

    def test_pc_used(self):
        class cls:
            @classmethod
            def convert(cls, s):
                return s

            @classmethod
            def complete(cls, s):
                return s
        assert cls is args._get_param(cls, False)


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


class TestTimeParam(unittest.TestCase):
    def test_convert(self):
        p = args.Time
        assert p.convert("2H1S") == 7201
        assert p.convert("10H50M30S") == 39030
        assert p.convert("4M") == 240
        self.assertAlmostEqual(p.convert("1.2"), 1.2)

    def test_complete(self):
        p = args.Time
        assert "1H" in list(p.complete("1"))
        assert "1M" in list(p.complete("1"))
        assert "1.0" in list(p.complete("1"))
        assert {"2H1M", "2H1S"} == set(p.complete("2H"))


class TestUnionParam(unittest.TestCase):
    def test_convert(self):
        p = args.Union(args.Bool, args.Int)
        assert p.convert("32") == 32
        assert p.convert("False") is False

    def test_complete(self):
        p = args.Union(args.Bool, args.Int)
        assert 'Yes' in list(p.complete(''))
        assert '42' in list(p.complete('4'))


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
        def f(i: int):
            pass
        p = args.ArgParser(f, 'auto', False)
        assert p.convert("123") == ((123,), {})

    def test_complete(self):
        def f(i: args.Param(complete=lambda s: ["asd fgh"])):
            pass
        p = args.ArgParser(f, 'auto', False)
        assert list(p.complete("a")) == ["asd fgh"]


class TestShellArgParser(unittest.TestCase):
    def test_convert(self):
        def f(i: int, b: bool, s):
            pass
        p = args.ArgParser(f, 'auto', False)
        assert p.convert("'123' 'No' 'Tes't' 'T'ext'") == (
            (123, False, "Test Text"), {})
        assert p.convert("123 No 42.42") == ((123, False, "42.42"), {})

    def test_complete(self):
        def f(i: int, s: args.Param(complete=[
            "ws text",
            "text",
            "singlequote's",
                'doublequote"s'])):
            pass
        p = args.ArgParser(f, 'auto', False)
        assert list(p.complete("1 text")) == ["1 text"]
        assert list(p.complete('1 "w')) == ['1 "ws text"']

        return
        # TODO: this is difficult, get it done sometime
        assert list(p.complete('1 w')) == ['1 w"s text"']
        assert list(
            p.complete('1 ')) == [
            '1 "ws text"',
            "1 text",
            '1 "singlequote\'s"',
            '1 "doublequote\\"s"']
        assert list(
            p.complete('1  ')) == [
            '1  "ws text"',
            "1  text",
            '1  "singlequote\'s"',
            '1  "doublequote\\"s"']
        assert list(
            p.complete("1 '")) == [
            "1 'ws text'",
            "1 'text'",
            "1 'singlequote\\'s'",
            "1 'doublequote\"s'"]
        assert list(p.complete('1  w')) == ['1  w"s text"']
        assert list(p.complete('1  ws" "tex')) == ['1  ws" "text']


class TestEnforceArgs(unittest.TestCase):
    def test_basic(self):
        @args.enforce_args
        def f(
            a: args.Int,
            b: args.Float,
            *c,
            d: args.Union(
                args.Int,
                args.Bool)):
            return a, b, c, d

        assert (255, 1.0, (), True) == f("0xFF", "1.0", d="Yes")
        assert (255, 1.0, ("hans",), True) == f("0xFF", "1.0", "hans", d="Yes")
        assert (255, 1.0, ("hans", "fred"), True) == f(
            "0xFF", "1.0", "hans", "fred", d="Yes")

    @unittest.skipUnless(sys.version_info >= (3, 5),
                         "Not supported before Python 3.5")
    def test_apply_on_defaults(self):
        @args.enforce_args(apply_defaults=True)
        def f(i: args.Int = '0x0F'):
            return i
        assert f() == 15

    def test_apply_on_defaults_off(self):
        @args.enforce_args
        def f(i: args.Int = '0x0F'):
            return i
        assert f() == '0x0F'
