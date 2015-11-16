import os
import os.path
import pathlib
import subprocess
import sys
import textwrap
import threading
import collections
import traceback

from .cmd import COMMANDS, cmd
from . import env

#{{{ Frontends

FRONTENDS = []
FRONTEND_MODULES = []
FRONTEND_LOCAL = threading.local()

def import_recursive(name):
    m = __import__(name)
    s = name.split('.')
    Env[s[0]] = m
    for p in s[1:]:
        m = getattr(m, p)
    return m


def load_frontend(name):
    mod = import_recursive(name)
    assert callable(mod.loop)
    assert callable(mod.stop)
    FRONTEND_MODULES.append(mod)
    FRONTENDS.append(name)

def run_frontends():
    """ Start all loaded frontends in seperate threads. If any frontend returns
    from its loop() method, call stop() of all frontends (from the main thread
    so stop must be threadsafe) and wait for all threads to finish.
    """

    frontends = list(FRONTEND_MODULES) # avoid concurrency

    if not frontends:
        raise ValueError("No Frontend Loaded yet")

    if len(frontends) == 1:     # Shortcut if there is no need for threading stuff
        fe = frontends[0]
        FRONTEND_LOCAL.frontend = fe.__name__
        try:
            fe.loop()
        except Exception as e:
            Env.handle_exception(e)
        try:
            fe.stop()
        except Exception as e:
            Env.handle_exception(e)
        del FRONTEND_LOCAL.frontend
    else:
        threads = []
        evt = threading.Event()

        def run_fe(fe):
            FRONTEND_LOCAL.frontend = fe.__name__
            try:
                fe.loop()
            except Exception as e:
                Env.handle_exception(e)
            finally:
                evt.set()
        for fe in frontends:
            t = threading.Thread(target=run_fe, args=[fe])
            t.start()
            threads.append((t, fe))

        try:
            evt.wait() # wait till some Frontend's loop() method returns
        finally:
            # stop all frontends
            for t, f in threads:
                try:
                    f.stop()
                except Exception as e:
                    Env.handle_exception(e)

            # wait for all frontends to finish.
            for t, f in threads:
                t.join()



#}}}

#{{{ Check

from . import check

Check = check.Check()

OS = set()
OS.add(os.name)
OS.add(sys.platform)

if os.name == 'nt':
    OS.add("win")
    OS.add("windows")

Check.os = check.Group(OS)
Check.frontend = check.Group(FRONTENDS)
Check.current_frontend = check.Value(lambda:FRONTEND_LOCAL.frontend)

#}}}

#{{{ Commands

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
    cmd, arg = parse_command(string)
    try:
        cmd = COMMANDS[cmd]
    except KeyError:
        return Env.command_not_found_hook(string)
    else:
        return cmd(arg)

#}}}

#{{{ Scripts

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

#}}}

#{{{ Completion

def get_all_completions(string):
    return _command_completion(string) + _py_completion(string)

def _command_completion(string):
    c, args = parse_command(string)
    if args and c in COMMANDS: # only complete args if the space after command came already
        cmd = COMMANDS[c]
        values = cmd.arg_parser.complete(args)
        return [c+" "+ x for x in values]
    l = len(string)
    return [ c for c in COMMANDS if c[:l]==string]

def _py_completion(string):
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

#}}}

#{{{ Env

Env = env.Env_class()
Env.COMMANDS = COMMANDS
Env.Check = Check

Env(cmd)

for k, v in os.environ.items():
    if k[:4] == 'HT3_':
        Env[k[4:]] = v


from .platform import env

@Env
def command_not_found_hook(s):
    """ Try to evaluate as expression and return the result,
        if that fails, try to execute as statements """
    try:
        c = compile(s, "<input>", "eval")
    except SyntaxError:
        c = compile(s, "<input>", "exec")
    return eval(c, Env.dict)

@Env
def handle_exception(e):
    """ Handle Exceptions that a frontend can not handle itself """
    if Env.get('DEBUG',False):
        import pdb
        pdb.post_mortem()
    traceback.print_exc()

@Env
def shell(string):
    """ pass a string to a shell. The shell will parse it. """
    return subprocess.Popen(string, shell=True)

@Env
def execute(*args):
    """ Execute a programm with arguments """
    return subprocess.call(args, shell=False)

@Env
def exit(n=0):
    """ Stop the program """
    sys.exit(n)

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
def list_env():
    """ List all commands """
    Env.show("\n".join(sorted(Env.dict.keys(), key=lambda k:k.lower())))

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


# }}}
