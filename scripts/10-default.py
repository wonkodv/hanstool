from ht3.cmd import cmd, COMMANDS
from ht3.lib import run_command

import subprocess
import sys

def _eval(s):
    try:
        c = compile(s, "<input>", "eval")
    except SyntaxError:
        c = compile(s, "<input>", "exec")
    return eval(c, globals())

def _command_not_found_hook(s):
    return _eval(s)

@cmd(args=1, name="$")
def shell(string):
    return subprocess.Popen(string, shell=True)

@cmd(args="shell", name="!")
def exe(*args):
    return subprocess.call(args, shell=False)

@cmd()
def exit():
    sys.exit()

@cmd(name='l')
def lsit_commands():
    for c in sorted(COMMANDS):
        show(COMMANDS[c])

@cmd(name='=',args=1)
def __eval(s):
    r = _eval(s)
    show (r)

@cmd(name='?', args=1)
def help(exp):
    if exp in COMMANDS:
        obj = COMMANDS[exp]
    else:
        obj = _eval(exp)
    __builtins__['help'](obj)

@cmd(args=COMMANDS)
def edit(command):
    f, l = command.origin
    exe(EDITOR, f)
