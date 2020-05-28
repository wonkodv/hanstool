"""Various helper functions"""

import textwrap
import functools
import shlex
import inspect
import time

from ht3.lib import evaluate_py_expression
from ht3.env import Env
from ht3.command import register_command


def cmd_func(name, func, *args, **kwargs):
    """Define a command that calls a function with arguments.

    The function is added to Env and can be called with additional
    arguments.
    see `functools.partial`."""
    cmdf = functools.partial(func, *args, **kwargs)
    register_command(cmdf,
                     name=name,
                     doc='executes\n' + " ".join(shlex.quote(x) for x in args),
                     origin_stacked=3)

    # be careful, black magic ahead!
    stack = inspect.stack()
    g = stack[1][0].f_globals
    g[name] = cmdf

    return cmdf


def cache_for(t):
    """Decorator that caches a function result for `t` seconds.

    the function can not have arguments.

        @cache_for(1.25)
        def f()
            return complicated_semi_time_dependant_stuff(with_args)
    """
    float(t)

    def deco(f):
        updated = 0
        cache = None

        @functools.wraps(f)
        def wrapper():
            nonlocal cache
            nonlocal updated
            now = time.monotonic()
            if now - updated > t:
                updated = now
                cache = f()
            return cache
        return wrapper
    return deco


__all__ = 'cmd_func', 'cache_for'
