"""Load Scripts, executing them in the global Namespace ``Env``."""

import pathlib
import re
import sys
from importlib.util import spec_from_file_location

from .env import Env
from . import lib



SCRIPTS = []

_SCRIPT_FILE_NAME = re.compile('^([a-zA-Z_][a-zA-Z0-9_]*)(\.(\d+))?$')

def _script_module(path):
    name = path.stem

    m = _SCRIPT_FILE_NAME.fullmatch(name)
    if m:
        name = m.group(1)
    else:
        raise NameError("Can not build Module Name", name)

    return name

def _script_order_key(p):
    """get a key that sorts b.5.py before a.20.py before  c.py """
    m = _SCRIPT_FILE_NAME.fullmatch(p.stem)
    name = m.group(1)
    idx = m.group(3)
    if idx:
        return 1, int(idx), name
    else:
        return 2, 0, name



def load_scripts(path):
    """
    Load a script or directory full of scripts.

    Path can be a string path or pathlib.Path.
    Scripts will be sorted by ``int(path.name.split(.)[-2])``.
    If a script raises NotImplementedError, this is ignored.
    """
    path = pathlib.Path(path)
    if path.is_dir():
        l = path.glob('*.py')
        l = sorted(l, key=_script_order_key)
        for p in l:
            load_scripts(p)
    elif path.is_file():
        name = _script_module(path)
        ename = 'Env.' + name
        spec = spec_from_file_location(ename, str(path))
        mod = spec.loader.load_module()
        assert mod.__name__ == ename
        assert sys.modules[ename] is mod
        assert mod.__file__ == str(path)
        SCRIPTS.append(path)
        Env.put(name, mod)
    elif not path.exists():
        raise FileNotFoundError(path)
    else:
        raise Exception("not file or dir", path)


def reload_all():
    for path in SCRIPTS:
        with path.open("rt") as f:
            c = f.read()
        c = compile(c, str(path), "exec")
        exec (c, Env.dict)

def check_all_compilable():
    r = True
    for path in SCRIPTS:
        with path.open("rt") as f:
            c = f.read()
        try:
            compile(c, str(path), "exec")
        except Exception as e:
            lib.EXCEPTION_HOOK(e)
            r = False
    return r
