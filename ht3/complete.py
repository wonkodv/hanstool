"""Completion od commands and python expressions."""
from collections import ChainMap
import ht3.command
import re
import pathlib
import os
import os.path
import collections.abc
from .env import Env


SCOPE = ChainMap(Env, __builtins__)

def filter_completions_i(s, *prop):
    """Filter out proposals that don't start with ``s`` ignoring case.

    returned proposals have the same case as ``s``.
    """
    already_yielded = set()
    l = len(s)
    if l > 0:
        us = s.upper()
        upper = s[-1].isupper()
        lower = s[-1].islower()
    else:
        us=s
        upper=False
        lower=False

    for it in prop:
        for p in it:
            up = p.upper()
            if up[:l] == us:
                if up not in already_yielded:
                    if upper:
                        yield s + up[l:]
                    elif lower:
                        yield s + p[l:].lower()
                    else:
                        yield s+p[l:]
                    already_yielded.add(up)

def filter_completions(s, *prop):
    """Filter out proposals that don't start with ``s``."""
    assert len(prop) > 0
    already_yielded = set()
    l = len(s)
    for it in prop:
        for p in it:
            if p[:l] == s:
                if p not in already_yielded:
                    yield p
                    already_yielded.add(p)

def complete_command_args(string):
    cmd, sep, args = ht3.command.parse_command(string)
    if not sep:
        raise ValueError()
    c = ht3.command.COMMANDS[cmd]
    return (cmd + sep + a for a in filter_completions(args, c.arg_parser.complete(args)))

def complete_commands(string):
    return sorted(filter_completions(string, ht3.command.COMMANDS.keys()))

def complete_command_with_args(string):
    p_space = string.find(' ')

    if p_space == -1:
        return complete_commands(string)
    else:
        return complete_command_args(string)

def _get_attributes_rec(obj, privates):
    values = set()
    for v in sorted(dir(obj)):
        if privates or v[0] != '_':
            values.add(v)
            yield v

    if hasattr(obj, '__class__'):
        c = obj.__class__
        while c != object:
            c = c.__base__
            for v in sorted(dir(c)):
                if v not in values:
                    if privates or v[0] != '_':
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

        values = _get_attributes_rec(val, pl.find('_') == 0)


    prefix = string[:len(string)-len(pl)]
    values = filter_completions(pl, values)
    values = sorted(values)
    values = (prefix + x for x in values)

    return values

def complete_path(s):
    if not s:
        p = pathlib.Path('.')
    else:
        p = pathlib.Path(os.path.expanduser(s))
    if s[-1] in ['/', os.sep]:
        stem = s
        mask = '*'
        p = p
    else:
        stem = s[:-len(p.name)]
        mask = p.name+'*'
        p = p.parent
    for e in p.glob(mask):
        yield stem + e.name


