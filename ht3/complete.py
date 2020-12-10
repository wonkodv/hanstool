"""Completion od commands and python expressions."""

import inspect
import os
import os.path
import pathlib
import re
from collections import ChainMap

import ht3.command

from .env import Env

__all__ = (
    "filter_completions_i",
    "filter_completions",
    "complete_command_args",
    "complete_commands",
    "complete_command_with_args",
    "complete_py",
    "complete_path",
)

SCOPE = ChainMap(Env, __builtins__)


def filter_completions_i(s, *prop):
    """Filter out proposals that don't start with ``s`` ignoring case.

    returned proposals have the same case as ``s``.
    """
    already_yielded = set()
    length = len(s)
    if length > 0:
        us = s.upper()
        upper = s[-1].isupper()
        lower = s[-1].islower()
    else:
        us = s
        upper = False
        lower = False

    for it in prop:
        for p in it:
            up = p.upper()
            if up[:length] == us:
                if up not in already_yielded:
                    if upper:
                        yield s + up[length:]
                    elif lower:
                        yield s + p[length:].lower()
                    else:
                        yield s + p[length:]
                    already_yielded.add(up)


def filter_completions(s, *prop):
    """Filter out proposals that don't start with ``s``."""
    assert len(prop) > 0
    already_yielded = set()
    length = len(s)
    for it in prop:
        for p in it:
            if p[:length] == s:
                if p not in already_yielded:
                    yield p
                    already_yielded.add(p)


def complete_command_args(string):
    cmd, sep, args = ht3.command.parse_command(string)
    if not sep:
        raise ValueError()
    c = ht3.command.COMMANDS[cmd]
    return (
        cmd + sep + a for a in filter_completions(args, c.arg_parser.complete(args))
    )


def complete_commands(string):
    return sorted(filter_completions(string, ht3.command.COMMANDS.keys()))


def complete_command_with_args(string):
    p_space = string.find(" ")

    if p_space == -1:
        return complete_commands(string)

    return complete_command_args(string)


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
            return []  # when the string contains illegal keys/attributes

        values = set(dir(val))
        for p in inspect.getmro(type(val)):
            values.update(dir(p))

    prefix = string[: len(string) - len(pl)]

    values = filter_completions(pl, values)
    values = sorted(values, key=lambda s: s and s[0] == "_")
    values = (prefix + x for x in values)

    return values


def complete_path(s):
    if not s:
        p = pathlib.Path(".")
    else:
        p = pathlib.Path(s).expanduser()

    if not s or s[-1] in ["/", os.sep]:
        stem = s
        mask = "*"
        # p = p
    else:
        stem = s[: -len(p.name)]
        mask = p.name + "*"
        p = p.parent
    for e in p.glob(mask):
        if e.is_dir():
            yield stem + e.name + "/"
        else:
            yield stem + e.name
