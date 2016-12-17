"""Completion od commands and python expressions."""

from .env import Env
from collections import ChainMap
import collections.abc
import ht3.command
import inspect
import os
import os.path
import pathlib
import re

__all__ = (
    'filter_completions_i',
    'filter_completions',
    'complete_command_args',
    'complete_commands',
    'complete_command_with_args',
    '_get_attributes_rec',
    'complete_py',
    'complete_path',
)

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

def _get_attributes_rec(obj):
    values = set()

    try:
        for a in sorted(obj.__all__):
            if a not in values:
                yield a
                values.add(a)
    except AttributeError:
        pass

    try:
        for a in sorted(obj.__slots__):
            if a not in values:
                yield a
                values.add(a)
    except AttributeError:
        pass

    try:
        for a in sorted(obj.__dict__):
            if a not in values:
                yield a
                values.add(a)
    except AttributeError:
        pass

    try:
        if not isinstance(obj, type):
            for c in type(obj).__mro__:
                for a in _get_attributes_rec(c):
                    if a not in values:
                        yield a
                        values.add(a)
    except AttributeError:
        pass

    for v in sorted(dir(obj), key=lambda s: (1 if s and s[0]!='_' else 2, s)):
        if a not in values:
            yield a
            values.add(a)


_COMPLETE_PY_SEPERATOR = re.compile("[^a-zA-Z0-9_.]+")

def complete_py(string):
    s = _COMPLETE_PY_SEPERATOR.split(string)
    parts = s[-1].strip().split(".")

    if len(parts) == 1:
        pl = parts[0]
        values = sorted(SCOPE)
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
    values = sorted(values, key=lambda s:s and s[0] == '_')
    values = (prefix + x for x in values)

    return values

def complete_path(s):
    if not s:
        p = pathlib.Path('.')
    else:
        p = pathlib.Path(os.path.expanduser(s))

    if not s or s[-1] in ['/', os.sep]:
        stem = s
        mask = '*'
        p = p
    else:
        stem = s[:-len(p.name)]
        mask = p.name+'*'
        p = p.parent
    for e in p.glob(mask):
        yield stem + e.name


