import time

from . import helpers


def test_cache_for():
    x = 0

    @helpers.cache_for(0.05)
    def f():
        nonlocal x
        x = x + 1
        return x

    assert f.__name__ == "f"
    assert f() == 1
    assert f() == 1
    assert f() == 1
    time.sleep(0.1)
    assert f() == 2
    assert f() == 2
