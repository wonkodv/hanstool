"""Completion od commands and python expressions."""
from collections import ChainMap
import ht3.command
import re
from . import env


SCOPE = ChainMap(env.Env.dict, __builtins__)

def filter_completions(s, *prop):
    """Filter out proposals that don't start with ``s``.""";
    l = len(s)
    return (p for it in prop for p in it  if p[:l] == s)


def complete_all(string):
    for s in complete_command(string):
        yield s
    for s in complete_py(string):
        yield s

def complete_command(string):
    cmd, sep, args = ht3.command.parse_command(string)
    COMMANDS = ht3.command.COMMANDS

    if sep and cmd in COMMANDS: # only complete args if the space after command came already
        c = COMMANDS[cmd]
        values = c.complete(args)
        values = (cmd + sep + x for x in filter_completions(args, values))
    else:
        values = sorted(filter_completions(string, COMMANDS.keys()))
    return values

def complete_py(string):
    #TODO: 1+DEB<tab> -> 1+DEBUG
    #s = re.split("[^a-zA-A0-9_.]*", string)
    #string = s[-1]
    parts = string.split(".")

    if len(parts) == 1:
        pl = parts[0]
        values = list(SCOPE)
    else:
        p0 = parts[0]
        pl = parts[-1]

        try:
            val = SCOPE[p0]

            for p in parts[1:-1]:
                p = p.strip()
                val = getattr(val, p)

            values = dir(val)

            if hasattr(val, '__class__'):
                values.append('__class__')
                c = val.__class__
                while c != object:
                    values += dir(c)
                    c = c.__base__
        except (KeyError, AttributeError):
            pass
    prefix = string[:len(string)-len(pl)]
    values = filter_completions(pl, values)
    values = sorted(values)
    values = [prefix + x for x in values]

    return values

