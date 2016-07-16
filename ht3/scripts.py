"""Load Scripts, executing them in the global Namespace ``Env``."""

import pathlib
from .env import Env
from . import lib

SCRIPTS = []

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
        def key(p):
            """get a key that sorts c.py before b.5.py before a.20.py"""
            if len(p.suffixes)>1:
                s = p.suffixes[-2][1:]
                try:
                    return int(s), p
                except ValueError:
                    pass
            return 0, p

        l = sorted(l, key=key)
        for p in l:
            load_scripts(p)
    elif path.is_file():
        with path.open("rt") as f:
            c = f.read()
        c = compile(c, str(path), "exec")
        exec (c, Env.dict)
        SCRIPTS.append(path)
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
