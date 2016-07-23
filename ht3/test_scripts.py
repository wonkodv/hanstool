from pathlib import Path
from .scripts import _script_module, _script_order_key

def test_name():
    assert _script_module(Path('/a/b/foo_bar.20.py')) == "foo_bar"
    assert _script_module(Path('/a/b/foo_bar.py')) == "foo_bar"

    try:
        _script_module(Path('/a/b/123.py'))
    except NameError:
        assert True
    else:
        assert False

def test_order_key():
    a = Path('/a.py')
    b = Path('/b.10.py')
    c = Path('/c.py')
    d = Path('/d.4.py')
    e = Path('/e.py')

    k = _script_order_key

    assert k(a) == (2, 0, 'a')
    assert k(b) == (1, 10, 'b')
    assert k(d) == (1, 4, 'd')

    assert k(a) < k(c)
    assert k(b) < k(a)
    assert k(d) < k(b)

    l = [a,b,c,d,e]

    s = sorted(l, key=_script_order_key)

    assert s == [d,b,a,c,e]


