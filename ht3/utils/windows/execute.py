import pathlib
import subprocess
import os
import shlex
import shutil
from ht3.utils import process
from ht3.env import Env

def execute(exe, *args, **kwargs):
    """Find an executable in PATH, optionally appending PATHEXT extensions, then execute."""
    exe, ext = next(_get_exe_path(exe))
    return process.execute(exe, *args, **kwargs)

_extensions = os.environ.get('PATHEXT','').split(os.pathsep)
_paths = [pathlib.Path(p) for p in os.get_exec_path()]

def _get_exe_path_ext(p):
    if p.suffix:
        for c in p.parent.glob(p.name+'*'):
            yield str(c), ''
    else:
        for ext in _extensions:
            for c in p.parent.glob(p.name+'*'+ext):
                yield c.name, ext

def _get_exe_path(s):
    p = pathlib.Path(s)
    parts = p.parts
    if len(parts) > 1:
        for c in _get_exe_path_ext(p):
            yield c
    else:
        for c in Env.get('PATH',_paths):
            f = c / s
            for x in _get_exe_path_ext(f):
                yield x

def complete_executable(s):
    """Find all possible executables in PATH, optionally appending PATHEXT."""
    s = shlex.split(s)
    if len(s) != 1:
        return
    s = s[0]

    values = {}
    for exe, ext in _get_exe_path(s):
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
