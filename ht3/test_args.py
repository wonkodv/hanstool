import unittest
from unittest.mock import Mock
from ht3.args import Args

class TestArgs(unittest.TestCase):
    def test_shell_args(self):
        a = Args('shell')

        assert a('a "b" \'C\'" "') == (['a', 'b', 'C '], {})
        with self.assertRaises(ValueError):
            a('a "')

    def test_one_arg(self):
        a = Args(1)

        assert a(" a ") == (["a"],{})
        with self.assertRaises(ValueError):
            a('')

    def test_no_arg(self):
        a = Args(None)
        assert a('') == ([],{})
        assert a('       ') == ([],{})
        with self.assertRaises(ValueError):
            a('asdfg')

    def test_callable_arg(self):
        a = Args(int)

        assert a("42") == ([42],{})

    def test_dict_args(self):
        d = {'a': 1, 'b':2}
        a = Args('dict', dict=[d])

        assert a('a') == ([1],{})


    def test_auto_full(self):
        typ = Mock()
        cmd = Mock()

        def f(s : str, n, t : typ, *args:int, kwa=42):
            assert s == 'Hans'
            assert kwa == 42
            assert len(args) == 4
            return 'OK'

        cmd.__wrapped__ = f

        a = Args('auto', _command=cmd)

        args, kwargs = a('Hans fred typ 0 1 2 3')
        assert f(*args, **kwargs) == 'OK'

        assert kwargs == {}
        s, n, t, a0, a1, a2, a3= args


        assert s == 'Hans'
        assert n == 'fred'
        typ.assert_was_called_once_with('typ')
        assert t is typ('Some String')
        assert a0 == 0
        assert a1 == 1
        assert a2 == 2
        assert a3 == 3

    def test_auto_partial(self):
        cmd = Mock()
        def f(a,b=0):
            pass
        cmd.__wrapped__ = f

        a = Args('auto', _command=cmd)

        args, kwargs = a('a')
        assert kwargs == {}
        assert args == ['a']
