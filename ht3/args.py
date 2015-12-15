"""Argument Parsing for commands."""

import shlex
import pathlib

__all__ = ('Args', )

_DEFAULT=object()

class ArgParser:
    def __init__(self, **kwargs):
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
    def __init__(self, default=_DEFAULT, **kwargs):
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
    def __init__(self, opts, **kwargs):
        super().__init__(**kwargs)
        self.opts = opts
        self.__doc__ = self.__doc__ % (opts,)

    def __call__(self, string):
        raise NotImplementedError()

class SetArgs(ArgParser):
    """Takes one of a set of arguments."""
    def __init__(self, sets, default=_DEFAULT, **kwargs):
        super().__init__(**kwargs)
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
    def __init__(self, dicts, default=_DEFAULT, **kwargs):
        super().__init__(dicts, **kwargs)
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
    def __init__(self, call, default=_DEFAULT, **kwargs):
        self.call = call
        self.default = default
        self.__doc__ = self.__doc__ % (call,)

    def __call__(self, string):
        if self.default is not _DEFAULT and string.strip() == '':
            return [self.default],{}
        return [self.call(string)],{}

class AutoArgs(ArgParser):
    """Parses shell style args and converts to annotated types"""
    def __init__(self, command, defaults=_DEFAULT, **kwargs):
        self.command = command
        if defaults is _DEFAULT:
            defaults = []
        self.defaults = defaults

    def __call__(self, string):
        t = self.command.__wrapped__.__annotations__
        raise NotImplementedError()


def Args(spec, **kwargs):
    if not spec:
        return NoArgs(**kwargs)

    if spec in ['1', 1, 'all']:
        return AllArgs(**kwargs)

    if isinstance(spec, str):
        if spec == '?':
            return NoOrOneArgs(**kwargs)

        if spec == 'shell':
            return ShellArgs(**kwargs)

        if spec == 'path':
            return PathArgs(**kwargs)

        if spec == 'set':
            d= []
            if 'set' in kwargs:
                d.append(kwargs['set'])
            if 'sets' in kwargs:
                d.extend(kwargs['sets'])
            return SetArgs(d, **kwargs)

        if spec == 'dict':
            d= []
            if 'dict' in kwargs:
                d.append(kwargs['dict'])
            if 'dicts' in kwargs:
                d.extend(kwargs['dicts'])
            return DictArgs(d, **kwargs)

        if spec.startswith(':'):
            return GetOptsArgs(spec[1:], **kwargs)

        if spec == 'auto':
            return AutoArgs(**kwargs)

    if isinstance(spec, list):
        return SetArgs([spec], **kwargs)

    if isinstance(spec, tuple):
        return SetArgs([spec], **kwargs)

    if isinstance(spec, set):
        return SetArgs([spec], **kwargs)

    if isinstance(spec, dict):
        return DictArgs([spec], **kwargs)

    if callable(spec):
        return CallableArgParser(spec, **kwargs)
    raise ValueError(spec)
