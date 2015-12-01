import textwrap
from . import Env

@Env
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

@Env
def list_env():
    """ List all commands """
    Env.show("\n".join(sorted(Env.dict.keys(), key=lambda k:k.lower())))

@Env
def help_command(exp):
    """ Show help on a command or evaluated python expression """
    if exp in Env.COMMANDS:
        obj = Env.COMMANDS[exp]
    else:
        obj = Env.evaluate_py_expression(exp)
    Env.help(obj)
