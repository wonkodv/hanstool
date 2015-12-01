import collections
import functools
import os
import os.path
import pathlib
import re
import shlex
import subprocess
import sys
import textwrap
import threading
import time
import traceback
import warnings


from . import env
from . import check

FRONTENDS = []
FRONTEND_MODULES = []
FRONTEND_LOCAL = threading.local()

SCRIPTS = []

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

def import_recursive(name):
    m = __import__(name)
    s = name.split('.')
    env.Env[s[0]] = m
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
            env.Env.handle_exception(e)
        try:
            fe.stop()
        except Exception as e:
            env.Env.handle_exception(e)
        del FRONTEND_LOCAL.frontend
    else:
        threads = []
        evt = threading.Event()

        def run_fe(fe):
            FRONTEND_LOCAL.frontend = fe.__name__
            try:
                fe.loop()
            except Exception as e:
                env.Env.handle_exception(e)
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
                    env.Env.handle_exception(e)

            # wait for all frontends to finish.
            for t, f in threads:
                t.join()

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
            exec (c, env.Env.dict)
        except NotImplementedError:
            # Script wanted to be ignored
            pass
        SCRIPTS.append(path)
    else:
        raise Exception("neither file nor dir in load_Scripts", path)

def format_log_message(msg, *args, **kwargs):
    if isinstance(msg, str):
        if kwargs:
            if args:
                raise ValueError("args or kwargs")
            msg = msg % kwargs
        else:
            msg = msg % args
    else:
        msg = repr(msg)
    if env.Env.get('DEBUG',False):
        msg = "".join(traceback.format_stack()) + "\n" + msg
    return msg


def execute_py_expression(s):
    """ Execute a python expression """
    c = compile(s, "<input>", "exec")
    return eval(c, env.Env.dict)

def evaluate_py_expression(s):
    """ Evaluate a python expression, show result """
    c = compile(s, "<input>", "eval")
    r = eval(c, env.Env.dict)
    return r
