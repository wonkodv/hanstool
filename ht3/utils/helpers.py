"""Various helper functions"""
import textwrap
import functools
import shlex
from ht3.env import Env
from ht3.command import register_command

def list_commands():
    """ List all commands """
    text = ""
    for n in sorted(Env.COMMANDS):
        c = Env.COMMANDS[n]
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
    if exp in Env.COMMANDS:
        obj = Env.COMMANDS[exp]
    else:
        obj = Env.evaluate_py_expression(exp)
    Env.help(obj)

def cmd_func(name, func, *args, **kwargs):
    """Define a command that calls a function with arguments"""
    cmdf = functools.partial(func, *args, **kwargs)
    register_command(cmdf,
        name=name,
        func_name=name,
        doc='executes\n'+" ".join(shlex.quote(x) for x in args),
        origin_stacked=3)
    Env[name] = cmdf
