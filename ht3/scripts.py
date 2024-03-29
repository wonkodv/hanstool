"""Load Scripts, executing them in the global Namespace ``Env``."""

import pathlib
import re
import sys
from importlib.util import spec_from_file_location

from . import lib
from .env import Env

SCRIPTS = []
ADDED_SCRIPTS = []

_SCRIPT_FILE_NAME_RE = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)(\.(\d+))?$")


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
    return 100, name


def add_scripts(path):
    """Add a script or directory full of scripts."""
    path = pathlib.Path(path)
    if path.is_dir():
        for p in path.glob("*.py"):
            add_scripts(p)
    elif path.is_file():
        if path not in ADDED_SCRIPTS:
            if not any(path.samefile(pathlib.Path(m.__file__)) for m in SCRIPTS):
                ADDED_SCRIPTS.append(path)
    elif not path.exists():
        raise FileNotFoundError(path)
    else:
        raise Exception("not file or dir", path)


def load_scripts():
    """Load added Scripts, sorted d.5.py before c.20.py before b.py before a.101.py."""

    scripts_to_load = sorted(ADDED_SCRIPTS, key=_script_order_key)
    if not scripts_to_load:
        raise ValueError("No scripts added (or already loaded)")
    for path in scripts_to_load:
        name = _script_module(path)
        ename = "Env." + name
        spec = spec_from_file_location(ename, str(path))
        mod = spec.loader.load_module()
        assert mod.__name__ == ename
        assert sys.modules[ename] is mod
        assert path.samefile(mod.__file__), (path, mod.__file__)
        ADDED_SCRIPTS.remove(path)
        SCRIPTS.append(mod)
        if getattr(mod, "_SCRIPT_ADD_TO_ENV", True):
            if Env.get(name):
                raise ImportError(
                    f"Env['{name}'] already occupied. Free it or specify _SCRIPT_ADD_TO_ENV=False",
                    name,
                    Env[name],
                )
            Env.put(name, mod)


def reload_all():
    try:
        for mod in SCRIPTS:
            if getattr(mod, "_SCRIPT_RELOAD", True):
                ADDED_SCRIPTS.append(pathlib.Path(mod.__file__))
            if getattr(mod, "_SCRIPT_ADD_TO_ENV", True):
                try:
                    delattr(Env, mod.__name__[4:])
                except KeyError:
                    pass  # was already removed from Env
            if Env.get(mod.__name__[4:], None) == mod:
                del Env[mod.__name__[4:]]
        SCRIPTS.clear()
        load_scripts()
    except Exception:
        import traceback

        traceback.print_exc()
        raise


def check_all_compilable():
    r = True
    for mod in SCRIPTS:
        path = pathlib.Path(mod.__file__)
        with path.open("rt",  encoding="utf-8") as f:
            c = f.read()
        try:
            compile(c, str(path), "exec")
        except Exception as e:
            lib.EXCEPTION_HOOK(exception=e)
            r = False
    return r
