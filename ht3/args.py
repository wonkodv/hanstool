"""Argument Parsing for commands."""

import shlex
import pathlib
import inspect
import collections.abc

__all__ = ('Args', )

_DEFAULT=object()

class ArgParser:
    def __init__(self):
        pass

    def __call__(self, string):
        raise NotImplementedError()

    def complete(self, string):
        return []

    def __str__(self):
        return self.__doc__

class NoArgs(ArgParser):
    """Takes no arguments."""

    def __call__ (self, string):
        string = string.strip()
        if string:
            raise ValueError("Not expecting an argument!, got: " + string)
        return [],{}

class NoOrOneArgs(ArgParser):
    """Takes no or one argument of arbitrary format."""

    def __call__ (self, string):
        string = string.strip()
        if string:
            return [string], {}
        return [],{}

class AllArgs(ArgParser):
    """Takes one argument of arbitrary format."""
    def __init__(self, default=_DEFAULT):
        self.default=default

    def __call__ (self, string):
        string = string.strip()
        if not string:
            if self.default is not _DEFAULT:
                return [self.default],{}
            raise ValueError("Expecting an argument")
        return [string],{}

class ShellArgs(ArgParser):
    """Takes shellencoded arguments."""

    def __call__(self, string):
        a = shlex.split(string)
        return a,{}

class PathArgs(ArgParser):
    """Takes shellencoded arguments."""

    def __call__(self, string):
        return [pathlib.Path(string)],{}

class GetOptsArgs(ArgParser):
    """Takes the following "getopt" arguments:\n%s."""
    def __init__(self, opts):
        super().__init__()
        self.opts = opts
        self.__doc__ = self.__doc__ % (opts,)

    def __call__(self, string):
        raise NotImplementedError()

class SetArgs(ArgParser):
    """Takes one of a set of arguments."""
    def __init__(self, sets, default=_DEFAULT):
        super().__init__()
        self.sets=sets
        self.default=default

    def __call__(self, string):
        string = string.strip()
        for s in self.sets:
            if string in s:
                return [string],{}

        if self.default is _DEFAULT:
            raise ValueError (string, self.sets)
        return [self.default],{}

    def complete(self, string):
        string = string.strip()
        for s in self.sets:
            for e in s:
                if e.startswith(string):
                    yield e

class DictArgs(SetArgs):
    """Takes one of a set of arguments."""
    def __init__(self, dicts, default=_DEFAULT):
        super().__init__(dicts)
        self.default = default

    def __call__(self, string):
        string = string.strip()
        for s in self.sets:
            if string in s:
                return [s[string]], {}
        if self.default is not _DEFAULT:
            return [self.default],{}
        raise ValueError (string, self.sets)

class CallableArgParser(ArgParser):
    """Takes a String that is accepted by %s()."""
    def __init__(self, call, default=_DEFAULT):
        self.call = call
        self.default = default
        self.__doc__ = self.__doc__ % (call,)

    def __call__(self, string):
        if self.default is not _DEFAULT and string.strip() == '':
            return [self.default],{}
        return [self.call(string)],{}


class AutoArgs(ArgParser):
    """Parses shell style args and converts to annotated types"""
    def __init__(self, command):
        self.command = command;

    def __call__(self, string):
        sig = inspect.signature(self.command)
        values = iter(shlex.split(string))

        args=[]
        for name, p in sig.parameters.items():
            t = p.annotation
            if t == p.empty:
                t = str
            if p.kind in [p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD]:
                try:
                    v = next(values)
                except StopIteration:
                    break
                v = t(v)
                args.append(v)
            elif p.kind == p.VAR_POSITIONAL:
                for v in values:
                    v = t(v)
                    args.append(v)
                break
        return args, {}

def Args(spec, **kwargs):
    if not spec:
        return NoArgs()

    if spec in ['1', 1, 'all']:
        return AllArgs()

    if isinstance(spec, str):
        if spec == '?':
            return NoOrOneArgs()

        if spec == 'shell':
            return ShellArgs()

        if spec == 'path':
            return PathArgs()

        if spec == 'set':
            return SetArgs(kwargs['set'])

        if spec == 'dict':
            return DictArgs(kwargs['dict'])

        if spec == 'callable':
            return CallableArgParser(kwargs['call'])

        if spec.startswith(':'):
            return GetOptsArgs(spec[1:])

        if spec == 'auto':
            return AutoArgs(kwargs['_command'])

    if isinstance(spec, ArgParser):
        return spec

    if isinstance(spec, collections.abc.Mapping):
        return DictArgs(spec)

    if isinstance(spec, collections.abc.Container):
        return SetArgs(spec)

    if callable(spec):
        return CallableArgParser(spec)

    raise ValueError(spec)
