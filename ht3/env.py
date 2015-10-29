import subprocess
import textwrap
import sys
import os

class Env_class:
    """ Class to record all variables and functions of
    all scripts and command invocations in one namespace """

    def __init__(self):
        self.dict=dict()

    def __getattr__(self, key):
        return self.dict[key]

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, val):
        self.dict[key] = val

    def get(self, key, default=None):
        return self.dict.get(key, default)

    def __iter__(self):
        return iter(self.dict)

    def __call__(self, func):
        """ decorator to put functions in Env """
        self.dict[func.__name__] = func
        return func

Env = Env_class()
Env['Env']=Env

for k, v in os.environ.items():
    if k in ['EDITOR']:
        Env[k] = v
    elif k.startswith('HT3_'):
        Env[k[4:]] = v

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
    for n in sorted(Env.COMMANDS):
        c = Env.COMMANDS[n]
        f = c.__wrapped__
        d = f.__doc__ or ''
        a = c.arg_parser
        doc = textwrap.shorten(d,60)
        doc = "%- 20s %s %s" % (n, doc, a)
        Env.show(doc)

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
    help(obj)
