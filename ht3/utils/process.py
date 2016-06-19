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

def execute(*args, shell=False, **kwargs):
    """Execute a program."""
    p = subprocess.Popen(args, shell=shell, **kwargs)
    p.shell = shell
    Env.log_subprocess(p)
    watch(p, lambda p: Env.log_subprocess_finished(p))
    return p

def execute_disconnected(*args, **kwargs):
    """Execute a program without any file handles attached."""
    return Env.execute(*args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        **kwargs)

def execute_auto(*args, **kwargs):
    """Execute a program, in foreground if on CLI, else in background."""
    if CHECK.current_frontend('ht3.cli'):
        p = Env.execute(*args, **kwargs)
        p.wait()
    else:
        p = Env.execute_disconnected(*args, **kwargs)
    return p

def procio(*args, input=None, timeout=None, **kwargs):
    """Get ouput from a program."""
    p = Env.execute(
        *args,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        **kwargs)

    out, err = p.communicate(input=input, timeout=timeout)
    if p.returncode != 0:
        return IOError("Non-zero return code", p.returncode, out, err)
    return out

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
