"""Functions to spawn subprocesses.

All functions here use posix semantics, some are redefined in ht3.util.windows.process"""

import subprocess
import shlex
import warnings
import pathlib
import os

from ht3.env import Env
from .processwatch import watch
from ht3.check import CHECK

def shellescape(*strings):
    return " ".join(shlex.quote(s) for s in strings)

def shell(string, cwd=None, env=None, **kwargs):
    """ pass a string to a shell. The shell will parse it. """
    p = subprocess.Popen(
        string,
        shell=True,
        cwd=cwd,
        env=env,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs)
    p.shell=True
    Env.log_subprocess(p)
    watch(p, lambda p: Env.log_subprocess_finished(p))
    return p

def execute(*args, cwd=None, env=None, **kwargs):
    """ Execute a programm with arguments """
    p = subprocess.Popen(args, shell=False, cwd=cwd, env=env, **kwargs)
    Env.log_subprocess(p)
    watch(p, lambda p: Env.log_subprocess_finished(p))
    p.shell=False
    return p

def complete_executable(s):
    s = shlex.split(s)
    if len(s) != 1:
        return
    s = s[0]
    p = pathlib.Path(s)

    if p.is_absolute() or '/' in s:
        for c in p.parent.glob(p.name+'*'):
            if c.is_file():
                if os.access(str(c), os.F_OK | os.X_OK):
                    yield str(c)
    else:
        for p in os.get_exec_path():
            p = pathlib.Path(p)
            for c in p.glob(s+'*'):
                if c.is_file():
                    if os.access(str(c), os.F_OK | os.X_OK):
                        yield c.name
