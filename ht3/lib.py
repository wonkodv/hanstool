import os
import os.path
import pathlib
import subprocess
import sys
import textwrap

from .cmd import COMMANDS, cmd
from . import env


def parse_command(string):
    i=0
    for c in string:
        if c in [' ','\t']:
            cmd = string[:i]
            arg = string[i:]
            break
        i += 1
    else:
        cmd = string
        arg = ""
    return cmd, arg

def run_command(string):
    try:
        try:
            cmd, arg = parse_command(string)
            cmd = COMMANDS[cmd]
            res = cmd(arg)
            Env['_'] = res
            return res
        except KeyError:
            res = Env._command_not_found_hook(string)
            Env['_'] = res
            return res
    except Exception as e:
        Env['_'] = e
        raise e

def load_scripts(path):
    if not isinstance(path, pathlib.Path):
        path = str(path)
        path = os.path.expanduser(path)
        path = pathlib.Path(path)
    if path.is_dir():
        l = path.glob('*.py')
        # sort b.50.py before a.80.py
        l = sorted(l, key=lambda p: [p.suffixes[-2][1:] if len(p.suffixes)>1 else "",p])
        for p in l:
            load_scripts(p)
    elif path.is_file():
        with path.open("rt") as f:
            c = f.read()
        c = compile(c, path.as_posix(), "exec")
        exec (c, Env.dict)
    else:
        raise Exception("neither file nor dir in load_Scripts", path)

def get_completion(string):
    c, args = parse_command(string)
    if c in COMMANDS:
        cmd = COMMANDS[c]
        values = cmd.arg_parser.complete(args)
        return [c+" "+ x for x in values]


    return command_completion(string) + py_completion(string)

def command_completion(string):
    l = len(string)
    return [ c for c in COMMANDS if c[:l]==string]

def py_completion(string):
    parts = [s.strip() for s in string.split(".")]

    values = dict()
    values.update(__builtins__)
    values.update(Env.dict)

    if len(parts) == 1:
        prefix = ""
        pl = string
    else:
        p0 = parts[0]
        pl = parts[-1]

        val = values[p0]

        for p in parts[1:-1]:
            val = getattr(val, p)

        values = dir(val)

        if hasattr(val, '__class__'):
            values.append('__class__')
            c = val.__class__
            while c != object:
                values += dir(c)
                c = c.__base__

    l = len(pl)
    prefix = string[:-l]

    return [ prefix + c for c in values if c[:l]==pl ]


Env = env.Env_class()
Env['COMMANDS'] = COMMANDS
Env(cmd)

from . import platform
platform.load_platform_modules()

@Env
def get_main_module():
    return pathlib.Path(sys.argv[0]).stem

@Env
def _command_not_found_hook(s):
    """ Try to evaluate as expression and return the result,
        if that fails, try to execute as statements """
    try:
        c = compile(s, "<input>", "eval")
    except SyntaxError:
        c = compile(s, "<input>", "exec")
    r = eval(c, Env.dict)
    return r

@Env
def shell(string):
    """ pass a string to a shell. The shell will parse it. """
    return subprocess.Popen(string, shell=True)

@Env
def execute(*args):
    """ Execute a programm with arguments """
    return subprocess.call(args, shell=False)

@Env
def exit():
    """ Stop the program """
    sys.exit()

@Env
def list_commands():
    """ List all commands """
    text = ""
    for n in sorted(Env.COMMANDS):
        c = Env.COMMANDS[n]
        f = c.__wrapped__
        d = f.__doc__ or ''
        a = c.arg_parser
        doc = textwrap.shorten(d,60)
        doc = "%- 20s %s %s\n" % (n, doc, a)
        text += doc
    Env.show(text)

@Env
def execute_py_expression(s):
    """ Execute a python expression """
    c = compile(s, "<input>", "exec")
    return eval(c, Env.dict)

@Env
def evaluate_py_expression(s):
    """ Evaluate a python expression, show result """
    c = compile(s, "<input>", "eval")
    r = eval(c, Env.dict)
    return r

@Env
def help_command(exp):
    """ Show help on a command or evaluated python expression """
    if exp in Env.COMMANDS:
        obj = Env.COMMANDS[exp]
    else:
        obj = evaluate_py_expression(exp)
    Env.help(obj)
