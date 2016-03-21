import unittest
import pathlib
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
        a = Args(d)

        assert a('a') == ([1],{})
    def test_dict_args_explicit(self):
        d = {'a': 1, 'b':2}
        a = Args('dict', dict=d)

        assert a('a') == ([1],{})

    def test_dict_multiple(self):
        d1 = {'a': 1, 'b':2}
        d2 = {'c': 3, 'd':4}
        a = Args('dict', dicts=[d1,d2])

        assert a('a') == ([1],{})
        assert a('c') == ([3],{})

    def test_dict_args_compl(self):
        d = {'foo': 1, 'bar':2, 'baz':3}
        a = Args('dict', dict=d)
        assert set(a.complete('')) == {'foo','bar','baz'}
        assert set(a.complete('b')) == {'bar','baz'}

    def test_set_args(self):
        s = {'a', 'b'}
        a = Args(s)

        assert a('a') == (['a'],{})

    def test_set_args_explicit(self):
        s = {'a', 'b'}
        a = Args('set', set=s)

        assert a('a') == (['a'],{})

    def test_set_multiple(self):
        s1 = {'a', 'b'}
        s2 = {'c', 'd'}
        a = Args('set', sets=[s1, s2])

        assert a('a') == (['a'], {})
        assert a('c') == (['c'], {})

    def test_set_args_compl(self):
        s = {'foo', 'bar', 'baz'}
        a = Args('set', set=s)
        assert set(a.complete('')) == {'foo','bar','baz'}
        assert set(a.complete('b')) == {'bar','baz'}


    def test_auto_full(self):
        typ = Mock()
        cmd = Mock()

        def f(s : str, n, t: typ, *args:int, kwa=42):
            assert s == 'Hans'
            assert kwa == 42
            assert len(args) == 4
            return 'OK'

        cmd.function = f

        a = Args('auto', _command=cmd)

        args, kwargs = a('Hans fred typ 0 1 2 3')
        assert f(*args, **kwargs) == 'OK'

        assert kwargs == {}
        s, n, t, a0, a1, a2, a3= args


        assert s == 'Hans'
        assert n == 'fred'
        typ.assert_called_once_with('typ')
        assert t is typ('Some String')
        assert a0 == 0
        assert a1 == 1
        assert a2 == 2
        assert a3 == 3

    def test_auto_partial(self):
        cmd = Mock()
        def f(a,b=0):
            pass
        cmd.function = f

        a = Args('auto', _command=cmd)

        args, kwargs = a('a')
        assert kwargs == {}
        assert args == ['a']

    def test_auto_onearg_vararg(self):
        cmd = Mock()
        def f(*a):
            pass
        cmd.function = f

        a = Args('auto', _command=cmd)

        args, kwargs = a('1 2 3')
        assert kwargs == {}
        assert args == ['1', '2', '3']

    def test_auto_onearg(self):
        cmd = Mock()
        def f(a):
            pass
        cmd.function = f

        a = Args('auto', _command=cmd)

        args, kwargs = a('1 2 3')
        assert kwargs == {}
        assert args == ['1 2 3']

    def test_auto_noargs(self):
        cmd = Mock()
        def f(a=0):
            pass
        cmd.function = f

        a = Args('auto', _command=cmd)

        args, kwargs = a('')
        assert kwargs == {}
        assert args == []


    def test_auto_complete_full(self):
        def f(t1:pathlib.Path, t2:pathlib.Path):
            pass
        cmd = Mock()
        cmd.function = f
        a = Args('auto', _command=cmd)

        def t(s):
            return list(a.complete(s))

        assert 'A ht3/' in t('A ht')


    def test_getopt(self):
        a = Args(':ab:c')

        args, kwargs = a('-ac -aa -b foo bar baz')
        assert args == ['bar', 'baz']
        assert kwargs == {'a': 3, 'c': 1, 'b': 'foo'}

    def test_getopt_explicit(self):
        a = Args('getopt', opt='abc')

        args, kwargs = a('-ac -aa -b foo bar baz')
        assert args == ['foo', 'bar', 'baz']
        assert kwargs == {'a': 3, 'c': 1, 'b': 1}
