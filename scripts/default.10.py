from ht3.cmd import cmd, COMMANDS
from ht3.lib import run_command

from pathlib import Path
import subprocess
import sys
import textwrap
import inspect


def _command_not_found_hook(s):
    try:
        c = compile(s, "<input>", "eval")
    except SyntaxError:
        c = compile(s, "<input>", "exec")
    r = eval(c, gloabls())
    return r

@cmd(args=1, name="$")
def shell(string):
    """ pass a string to a shell. The shell will parse it. """
    return subprocess.Popen(string, shell=True)

@cmd(args="shell", name="!")
def execute(*args):
    """ Execute a programm with arguments """
    return subprocess.call(args, shell=False)

@cmd()
def exit():
    """ Stop the program """
    sys.exit()

@cmd(name='l')
def lsit_commands():
    """ List all commands """
    for n in sorted(COMMANDS):
        c = COMMANDS[n]
        f = c.__wrapped__
        d = f.__doc__ or ''
        a = f.arg_parser
        doc = textwrap.shorten(d,60)
        doc = "%- 20s %s %s" % (n, doc, a)
        show(doc)

@cmd(name=';',args=1)
def execute_py_expression(s):
    """ Execute a python expression """
    c = compile(s, "<input>", "exec")
    return eval(c, globals())

@cmd(name='=',args=1)
def evaluate_py_expression(s):
    """ Evaluate a python expression, show result """
    c = compile(s, "<input>", "eval")
    r = eval (c,globals())
    show (r)

@cmd(name='?', args=1)
def _help(exp):
    """ Show help on a command or evaluated python expression """
    if exp in COMMANDS:
        obj = COMMANDS[exp]
    else:
        obj = evaluate_py_expression(exp)
    __builtins__['help'](obj)

@cmd(name="+", args=COMMANDS)
def edit(command):
    """ Edit the location where a command was defined """
    f, l = command.origin
    execute(EDITOR, f)

@cmd
def py():
    """ start a python repl """
    return execute(sys.executable)
