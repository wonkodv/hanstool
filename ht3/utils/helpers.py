"""Various helper functions"""
import textwrap
import functools
import shlex
from ht3.lib import evaluate_py_expression
from ht3.env import Env
from ht3.command import register_command, COMMANDS

def list_commands():
    """ List all commands """
    text = ""
    for n in sorted(COMMANDS):
        c = COMMANDS[n]
        d = c.doc
        a = c.arg_parser
        doc = textwrap.shorten(d,60)
        doc = "%- 20s %s %s\n" % (n, doc, a)
        text += doc
    Env.show(text)

def list_env():
    """ List all commands """
    Env.show("\n".join(sorted(Env.dict.keys(), key=lambda k:k.lower())))

def help_command(exp):
    """ Show help on a command or evaluated python expression """
    if exp in COMMANDS:
        obj = COMMANDS[exp]
    else:
        obj = evaluate_py_expression(exp)
    Env.help(obj)

def cmd_func(name, func, *args, **kwargs):
    """Define a command that calls a function with arguments.

    The function is added to Env and can be called with additional
    arguments.
    see `functools.partial`."""
    cmdf = functools.partial(func, *args, **kwargs)
    register_command(cmdf,
        name=name,
        func_name=name,
        doc='executes\n'+" ".join(shlex.quote(x) for x in args),
        origin_stacked=3)
    Env[name] = cmdf

def _complete_bool(s):
    if s:
        return filter_completions_i(s, ["yes", "no", "true", "false", "0", "1"])
    return ["Yes", "No"]

def _convert_bool(s):
    s = s.lower()
    if not s:
        raise ValueError()

    if s[0] in 'n0' or s == 'false':
        return False
    if s[0] in 'jy1' or s == 'true':
        return True

    raise ValueError("Not a boolean word", s)
