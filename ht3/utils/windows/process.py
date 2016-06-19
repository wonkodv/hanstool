"""Implement process-related functions that behave special on windows."""

import pathlib
import subprocess
import os
import shlex
import ctypes
from ht3.utils import process
from ht3.env import Env

def execute(exe, *args, **kwargs):
    """Find an executable in PATH, optionally appending PATHEXT extensions, then execute."""
    if not kwargs.get('shell',False):
        try:
            exe = next(_get_exe_path(exe, True))
        except StopIteration:
            raise FileNotFoundError(exe) from None
    return process.execute(exe, *args, **kwargs)

_extensions = os.environ.get('PATHEXT','').split(os.pathsep)
_paths = [pathlib.Path(p) for p in os.get_exec_path()]



def _get_exe_path_ext(p, full_path):
    if p.suffix:
        for c in p.parent.glob(p.name+'*'):
            if full_path:
                yield str(c)
            else:
                yield str(c), ''
    else:
        for ext in _extensions:
            for c in p.parent.glob(p.name+'*'+ext):
                if full_path:
                    yield str(c)
                else:
                    yield c.name, ext

def _get_exe_path(s, full_path):
    p = pathlib.Path(s)
    parts = p.parts
    if len(parts) > 1:
        for c in _get_exe_path_ext(p, full_path):
            yield c
    else:
        for c in Env.get('PATH',_paths):
            f = c / s
            for x in _get_exe_path_ext(f, full_path):
                yield x

def complete_executable(s):
    """Find all possible executables in PATH, optionally appending PATHEXT.

    If there is more than file with the same name, only differing in the 
    extension, yield both, else yield only the name"""
    s = shlex.split(s)
    if len(s) != 1:
        return
    s = s[0]

    values = {}
    for exe, ext in _get_exe_path(s, False):
        short = exe[:-len(ext)]
        if short in values:
            values[short].add(exe)
        else:
            values[short] = {exe}

    for short, longs in sorted(values.items()):
        if len(longs) == 1:
            yield short
        else:
            for l in longs:
                yield l


def shellescape(*strings):
    return subprocess.list2cmdline(strings)


def WaitForInputIdle(process, timeout=-1):
    r = ctypes.windll.user32.WaitForInputIdle(process._handle, timeout)
    if r == 0:
        return True
    if r == 0x102:
        return False
    raise ctypes.WinError()
