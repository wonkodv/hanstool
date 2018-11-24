"""Load Scripts, executing them in the global Namespace ``Env``."""

import importlib
import inspect
import pathlib
import re
import sys

from importlib.util import spec_from_file_location


from .env import Env
from . import lib

SCRIPTS = []
ADDED_SCRIPTS = []

_SCRIPT_FILE_NAME_RE = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)(\.(\d+))?$')

def _script_module(path):
    name = path.stem

    m = _SCRIPT_FILE_NAME_RE.fullmatch(name)
    if m:
        name = m.group(1)
    else:
        raise NameError("Can not build Module Name", name)

    return name

def _script_order_key(p):
    """get a key that sorts scripts"""
    m = _SCRIPT_FILE_NAME_RE.fullmatch(p.stem)
    name = m.group(1)
    idx = m.group(3)
    if idx:
        return int(idx), name
    else:
        return 100, name

def add_scripts(path):
    """ Add a script or directory full of scripts.  """
    path = pathlib.Path(path)
    if path.is_dir():
        l = path.glob('*.py')
        for p in l:
            add_scripts(p)
    elif path.is_file():
        if path not in ADDED_SCRIPTS:
            if not any(path.samefile(Path(m.__file__)) for m in SCRIPTS):
                ADDED_SCRIPTS.append(path)
    elif not path.exists():
        raise FileNotFoundError(path)
    else:
        raise Exception("not file or dir", path)

def load_scripts():
    """Load added Scripts, sorted d.5.py before c.20.py before b.py before a.101.py."""

    l = sorted(ADDED_SCRIPTS, key=_script_order_key)
    if not l:
        raise ValueError("No scripts added (or already loaded)")
    for path in l:
        name = _script_module(path)
        ename = 'Env.' + name
        spec = spec_from_file_location(ename, str(path))
        mod = spec.loader.load_module()
        assert mod.__name__ == ename
        assert sys.modules[ename] is mod
        assert mod.__file__ == str(path)
        ADDED_SCRIPTS.remove(path)
        SCRIPTS.append(mod)
        if getattr(mod, '_SCRIPT_ADD_TO_ENV', True):
            if name in Env:
                raise ImportError("Env['{name}'] already occupied. Free it or specify _SCRIPT_ADD_TO_ENV=False")
            Env.put(name, mod)

def reload_all():
    for mod in SCRIPTS:
        if getattr(mod, '_SCRIPT_RELOAD', True):
            ADDED_SCRIPTS.append(pathlib.Path(mod.__file__))
        if getattr(mod, '_SCRIPT_ADD_TO_ENV', True):
            delattr(Env, mod.__name__.lstrip("Env."))
    SCRIPTS.clear()
    load_scripts()

def check_all_compilable():
    r = True
    for mod in SCRIPTS:
        path = pathlib.Path(mod.__file__)
        with path.open("rt") as f:
            c = f.read()
        try:
            compile(c, str(path), "exec")
        except Exception as e:
            lib.EXCEPTION_HOOK(exception=e)
            r = False
    return r
