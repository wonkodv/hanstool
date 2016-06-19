"""Various helper functions"""
import textwrap
import functools
import shlex
from ht3.lib import evaluate_py_expression
from ht3.env import Env
from ht3.command import register_command, COMMANDS


def cmd_func(name, func, *args, **kwargs):
    """Define a command that calls a function with arguments.

    The function is added to Env and can be called with additional
    arguments.
    see `functools.partial`."""
    cmdf = functools.partial(func, *args, **kwargs)
    register_command(cmdf,
        name=name,
        doc='executes\n'+" ".join(shlex.quote(x) for x in args),
        origin_stacked=3)
    Env[name] = cmdf

