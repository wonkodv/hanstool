"""Argument Parsing for commands."""

import shlex
import pathlib
import inspect
import collections.abc
import getopt
import ht3.complete

__all__ = ('Args', )

_DEFAULT=object()

class ArgError(ValueError):
    pass

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
            raise ArgError("Expecting no args, got: " + string)
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
            raise ArgError("Expecting an argument, got none")
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
    """Takes "getopt" arguments: %s."""
    def __init__(self, opts):
        super().__init__()
        self.opts = opts
        self.__doc__ = self.__doc__ % (opts,)

    def __call__(self, string):
        args = string.split()
        optlist, args = getopt.gnu_getopt(args, self.opts)
        kwargs = {}
        for k, v in optlist:
            k = k[1:]
            if v == '':
                # opts a:b, args -a '' -a '' will give a:2 but who would do such a thing
                if k in kwargs:
                    v = kwargs[k] + 1
                else:
                    v = 1
            else:
                if k in kwargs:
                    raise ArgError("option -%s occured multiple times" % k)
            kwargs[k] = v

        return args, kwargs

class SetArgs(ArgParser):
    """Takes one of a set of arguments."""
    def __init__(self, *sets, default=_DEFAULT):
        self.sets=sets
        self.default=default

    def __call__(self, string):
        string = string.strip()
        if not string:
            if self.default is _DEFAULT:
                raise ArgError ("Expected an argument, got none")
            return [self.default],{}
        for s in self.sets:
            if string in s:
                return [string],{}
        raise ArgError("illegal argument", string, self.sets)

    def complete(self, string):
        string = string.strip()
        return ht3.complete.filter_completions(string, *self.sets)


class DictArgs(ArgParser):
    """Takes one of a set of arguments."""
    def __init__(self, *dicts, default=_DEFAULT):
        self.default = default
        self.dicts = dicts

    def __call__(self, string):
        string = string.strip()
        for s in self.dicts:
            if string in s:
                return [s[string]], {}
        if self.default is not _DEFAULT:
            return [self.default],{}
        raise ArgError ("Key not in dicts, no default", string, self.dicts)

    def complete(self, string):
        string = string.strip()
        return sorted(ht3.complete.filter_completions(string, *self.dicts))

class CallableArgParser(ArgParser):
    """Takes a String that is accepted by %s()."""
    def __init__(self, call, default=_DEFAULT):
        self.call = call
        self.default = default
        self.__doc__ = self.__doc__ % (call,)

    def __call__(self, string):
        string = string.strip()
        if not string:
            if self.default is _DEFAULT:
                raise ArgError ("Expected an argument, got none")
            return [self.default],{}
        return [self.call(string)],{}


class AutoArgs(ArgParser):
    """Parses args matching the signature %s."""
    def __init__(self, command):
        self.command = command
        self.sig = inspect.signature(command)
        self.__doc__ = self.__doc__ % (self.sig)


    def __call__(self, string):
        if not string.strip():
            return [],{}

        values = []
        if len(self.sig.parameters) == 1:
            p = list(self.sig.parameters.items())[0][1]
            if p.kind in [p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD]:
                values = [string]
        if not values:
            values = shlex.split(string)

        values = iter(values)

        args=[]
        for name, p in self.sig.parameters.items():
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
            s = []
            if 'set' in kwargs:
                s.append(kwargs['set'])
            if 'sets' in kwargs:
                s.extend(kwargs['sets'])
            if not s:
                raise KeyError('Pass a set in `set` or `sets`')
            return SetArgs(*s)

        if spec == 'dict':
            d = []
            if 'dict' in kwargs:
                d.append(kwargs['dict'])
            if 'dicts' in kwargs:
                d.extend(kwargs['dicts'])
            if not d:
                raise KeyError('Pass a dict in `dict` or `dicts`')
            return DictArgs(*d)

        if spec == 'callable':
            return CallableArgParser(kwargs['call'])

        if spec == 'getopt':
            return GetOptsArgs(kwargs['opt'])

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
