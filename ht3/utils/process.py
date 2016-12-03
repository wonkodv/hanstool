"""Functions to spawn subprocesses.

All functions here use posix semantics, some are redefined in ht3.util.windows.process"""

import subprocess
import shlex
import warnings
import pathlib
import os

from ht3.env import Env
from . import processwatch
from ht3.check import CHECK

import ht3.hook

SUBPROCESS_SPAWN_HOOK = ht3.hook.Hook()
SUBPROCESS_FINISH_HOOK = ht3.hook.Hook()

def shellescape(*strings):
    return " ".join(shlex.quote(s) for s in strings)

def execute(*args, shell=False, is_split=..., **kwargs):
    """Execute a program."""
    if not all(isinstance(a, str) for a in args):
        raise TypeError("Expecting strings")


    if shell:
        if is_split is ...:
            pass
        elif is_split:
            raise TypeError("Don't pass `is_split` and `shell`")
        if len(args) != 1:
            raise TypeError("Pass only 1 argument with `shell`", args)
        args = args[0]
        name = pathlib.Path(shlex.split(args)[0]).name
    else:
        if is_split is ...:
            is_split = True

        if not is_split:
            if len(args) != 1:
                raise TypeError("Pass only 1 argument if not `is_split`", args)
            args = shlex.split(args[0])
        name = pathlib.Path(args[0]).name

    try:
        p = subprocess.Popen(args, shell=shell, **kwargs)
    except OSError as e:
        e.args = e.args + (args,shell)
        raise e
    p.name = name
    p.shell = shell
    SUBPROCESS_SPAWN_HOOK(p)
    def onreturn(cb):
        processwatch.watch(p, cb)
        return cb
    p.onreturn = onreturn
    p.onreturn(SUBPROCESS_FINISH_HOOK)
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

class ProcIOException(Exception):
    def __init__(self, msg, returncode, out, err, args):
        self.returncode = returncode
        self.out = out
        self.err = err
        self.args = args
        self.msg  = msg
        super().__init__(msg, returncode, out, err, args)

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
        raise ProcIOException("Non-zero return code", args, p.returncode, out, err)
    return out

def complete_executables(s):
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
