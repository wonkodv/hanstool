import pathlib
import subprocess
from ht3.utils import process
import os
import shlex
import shutil

def execute(exe, *args, **kwargs):
    """Find an executable in PATH, optionally appending PATHEXT extensions"""

    w = shutil.which(exe)
    if w:
        exe = w

    return process.execute(exe, *args, **kwargs)

_extensions = os.environ.get('PATHEXT','').split(os.pathsep)
_paths = [pathlib.Path(p) for p in os.get_exec_path()]

def _glob_path_complete(p):
    if p.suffix:
        for c in p.parent.glob(p.name+'*'):
            yield c.path
    else:
        for ext in _extensions:
            for c in p.parent.glob(p.name+'*'+ext):
                yield c.name

def complete_executable(s):
    s = shlex.split(s)
    if len(s) != 1:
        return
    s = s[0]
    p = pathlib.Path(s)
    parts = p.parts
    if len(parts) > 1:
        return _glob_path_complete(p)
    else:
        for p in _paths:
            f = p / s
            for x in _glob_path_complete(f):
                yield x
