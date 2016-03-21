"""Completion od commands and python expressions."""
from collections import ChainMap
import ht3.command
import re
import pathlib
import os
from .env import Env


SCOPE = ChainMap(Env, __builtins__)

def filter_completions(s, *prop):
    """Filter out proposals that don't start with ``s``.""";
    l = len(s)
    for it in prop:
        for p in it:
            if p[:l] == s:
                yield p

def complete_all(string):
    for s in complete_command(string):
        yield s
    for s in complete_py(string):
        yield s

def complete_command(string):
    try:
        cmd, sep, args = ht3.command.get_command(string)
        if sep or args:
            return (cmd.name + sep + a for a in filter_completions(args, cmd.complete(args)))
    except KeyError:
        pass
    return sorted(filter_completions(string, ht3.command.COMMANDS.keys()))

def _get_attributes_rec(obj):
    values = set()
    for v in sorted(dir(obj)):
        values.add(v)
        yield v

    if hasattr(obj, '__class__'):
        c = obj.__class__
        while c != object:
            c = c.__base__
            for v in sorted(dir(c)):
                if v not in values:
                    values.add(v)
                    yield v

_COMPLETE_PY_SEPERATOR = re.compile("[^a-zA-Z0-9_.]+")

def complete_py(string):
    s = _COMPLETE_PY_SEPERATOR.split(string)
    parts = s[-1].strip().split(".")

    if len(parts) == 1:
        pl = parts[0]
        values = list(SCOPE)
    else:
        p0 = parts[0]
        pl = parts[-1]

        try:
            val = SCOPE[p0]
            for p in parts[1:-1]:
                val = getattr(val, p)
        except (KeyError, AttributeError):
            return [] # when the string contains illegal keys/attributes

        values = _get_attributes_rec(val)


    prefix = string[:len(string)-len(pl)]
    values = filter_completions(pl, values)
    values = sorted(values)
    values = (prefix + x for x in values)

    return values

def complete_path(s):
    p = pathlib.Path(s)
    for e in p.parent.glob(p.name+'*'):
        if e.is_dir():
            e = str(e) + os.pathsep
        else:
            e = str(e)
        if not e.startswith(s):
            c = e[:len(s)]
            if c.replace('\\','/') == s.replace('\\','/'):
                e = s + e[len(s):]
        assert e.startswith(s), [s,e]
        yield e
