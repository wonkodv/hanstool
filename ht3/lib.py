import os
import os.path
import pathlib
import subprocess
import sys
import textwrap
import threading
import collections
import traceback
import shlex
import warnings
import re


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
            sep = string[i]
            arg = string[i+1:]
            break
        i += 1
    else:
        cmd = string
        sep = ""
        arg = ""

    return cmd, sep, arg

def run_command(string):
    cmd, sep, arg = parse_command(string)
    try:
        cmd = COMMANDS[cmd]
    except KeyError:
        r = Env.command_not_found_hook(string)
    else:
        r = cmd(arg)
    if r is not None:
        Env._ = r
        Env.__.append(r)
    return r

#}}}

#{{{ Scripts

SCRIPTS = []

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
        c = compile(c, str(path), "exec")
        try:
            exec (c, Env.dict)
        except NotImplementedError:
            # Script wanted to be ignored
            pass
        SCRIPTS.append(path)
    else:
        raise Exception("neither file nor dir in load_Scripts", path)

#}}}

#{{{ Completion

def complete_all(string):
    return complete_command(string) + complete_py(string)

def complete_command(string):
    c, sep, args = parse_command(string)
    if sep and c in COMMANDS: # only complete args if the space after command came already
        cmd = COMMANDS[c]
        values = cmd.complete(args)
        l = len(args)
        values = filter(lambda x:x[:l]==args, values)
        values = sorted(values)
        values = [c + sep + x for x in values]
    else:
        l = len(string)
        values = COMMANDS.keys()
        values = filter(lambda x:x[:l]==string, values)
        values = sorted(values)
    return values

def complete_py(string):
    #s = re.split("[^a-zA-A0-9_.]", string)
    #string = s[-1]
    parts = [s.strip() for s in string.split(".")]

    values = dict()
    values.update(__builtins__)
    values.update(Env.dict)

    if len(parts) == 1:
        pl = parts[0]
    else:
        p0 = parts[0]
        pl = parts[-1]

        try:
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
        except:
            pass

    l = len(pl)
    prefix = string[:len(string)-l]

    values = filter(lambda x:x[:l]==pl, values)
    values = sorted(values)
    values = [prefix + x for x in values]

    return values

#}}}

#{{{ Env

Env = env.Env_class()
Env.COMMANDS = COMMANDS
Env.Check = Check

Env(cmd)
Env(complete_py)
Env(complete_command)
Env(complete_all)

Env.__ = []
Env._  = None

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
def shellescape(string):
    if Check.os.posix:
        return shlex.quote(string)

    #TODO: make this safe!
    warnings.warn("UNSAFE !!! ht3.lib.shellescape")
    string = '"' + string + '"'

    return string

@Env
def shell(string, cwd=None, env=None):
    """ pass a string to a shell. The shell will parse it. """
    Env.log("Running Shell with: "+string)
    return subprocess.Popen(string, shell=True, cwd=cwd, env=env)

@Env
def execute(*args, cwd=None, env=None):
    """ Execute a programm with arguments """
    Env.log("executing: "+str(args))
    return subprocess.Popen(args, shell=False, cwd=cwd, env=env)

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


from .platform import fake_input

_fake_types = (
    ("WHITESPACE",  r"\s+"),
    ("MOVE",        r"(?P<x>\d+)x(?P<y>\d+)"),
    ("MBTN",        r"(?P<mud>\+|-|)M(?P<btn>[1-3])"),
    ("KEY",         r"(?P<kud>\+|-|)(?P<key>[A-Za-z_0-9]+)"),
    ("STRING1",     r"'(?P<s1>[^']*)'"),
    ("STRING2",     r'"(?P<s2>[^"]*)"'),
    ("INVALID",     r"\S+")
    )

_fake_re = re.compile("|".join("(?P<%s>%s)" % pair for pair in _fake_types))


@Env
def fake(string):
    """ Fake a sequence of Events, specified by a string in the
        following mini language:
        *   Whitespaces are ignored
        *   123X456 moves the mouse to x=123 and y=456, see mouse_move
        *   M1      Does a Mouse Click at the current mouse position
                    With the left button. 2=Middle, 3=right
        *   +M2     Press but do not release the middle mouse button
        *   -M3     Release the right mouse button
        *   'hans@fred.com'  Type hans' email address. No escaping. Tou can use
                     single or double quotes
        *   +Key    Press Key. valid Keys are A-Z 0-9 SHIFT, CoNTroL,... see KEY_CODES
        *   -A  Releaase A
        *   A   Press, then release A
    """

    sequence = []
    def a(f, *a):
        sequence.append((f, a))
    for m in _fake_re.finditer(string):
        if   m.group("WHITESPACE"):
            pass

        elif m.group("MOVE"):
            x = int(m.group('x'))
            y = int(m.group('y'))
            a(fake_input.mouse_move, x, y)

        elif m.group("MBTN"):
            ud = m.group('mud')
            btn= int(m.group('btn'))
            if ud != '-':
                a(fake_input.mouse_down, btn)
            if ud != '+':
                a(fake_input.mouse_up, btn)

        elif m.group("KEY"):
            ud = m.group('kud')
            key= m.group('key')
            key= fake_input.KEY_CODES[key.upper()]
            if ud != '-':
                a(fake_input.key_down, key)
            if ud != '+':
                a(fake_input.key_up, key)

        elif m.group("STRING1"):
            s = m.group('s1')
            a(fake_input.type_string, s)

        elif m.group("STRING2"):
            s = m.group('s2')
            a(fake_input.type_string, s)

        elif m.group("INVALID"):
            raise ValueError("Invalid Token", m.group(0))
        else:
            assert False, m

    for c, a in sequence:
        c(*a)


Env.dict.update(vars(fake_input))


# }}}
