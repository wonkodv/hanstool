import shlex
import re
import pathlib


class ArgParser:
    def __call__(self, string):
        raise NotImplementedError()

    def complete(self, string):
        return []

    def __str__(self):
        return self.__doc__

class NoArgs(ArgParser):
    """ Takes no arguments """

    def __call__ (self, string):
        string = string.strip()
        if string:
            raise ValueError("Not expecting an argument!, got: " + string)
        return [],{}

class NoOrOneArgs(ArgParser):
    """ Takes no or one argument of arbitrary format """

    def __call__ (self, string):
        string = string.strip()
        if string:
            return [string], {}
        return [],{}

class AllArgs(ArgParser):
    """ Takes one argument of arbitrary format """

    def __call__ (self, string):
        string = string.strip()
        if not string:
            raise ValueError("Expecting an argument")
        return [string],{}

class ShellArgs(ArgParser):
    """ Takes shellencoded arguments """

    def __call__(self,string):
        a = shlex.split(string)
        return a,{}

class PathArgs(ArgParser):
    """ Takes shellencoded arguments """

    def __call__(self, string):
        return [pathlib.Path(string)],{}

class GetOptsArgs(ArgParser):
    """ Takes the following "getopt" arguments:\n%s """
    def __init__(self, opts, **kwargs):
        super().__init__(**kwargs)
        self.opts = opts
        self.__doc__ = self.__doc__ % (opts,)

    def __call__(string):
        raise NotImplemented()

class SetArgs(ArgParser):
    """ Takes one of a set of arguments """
    def __init__(self, sets, **kwargs):
        super().__init__(**kwargs)
        self.sets=sets

    def __call__(self, string):
        string = string.strip()
        for s in self.sets:
            if string in s:
                return [string],{}

        raise ValueError (string, self.sets)

    def complete(self, string):
        string = string.strip()
        for s in self.sets:
            for e in s:
                if e.startswith(string):
                    yield e

class DictArgs(SetArgs):
    """ Takes one of a set of arguments """
    def __init__(self, dicts, default=..., **kwargs):
        super().__init__(dicts, **kwargs)
        self.default = default

    def __call__(self, string):
        string = string.strip()
        for s in self.sets:
            if string in s:
                return [s[string]], {}
        if not self.default is ...:
            return [self.default],{}
        raise ValueError (string, self.sets)

class CallableConverter(ArgParser):
    """ Takes a String that is accepted by %s() """
    def __init__(self, func, **kwargs):
        self.call = call
        self.__doc__ = self.__doc__ % (call,)

    def __call__(self, string):
        return [self.call(string)],{}

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
            return GetOptsArgs(id[1:], **kwargs)

        return ParseArgSpecString(spec, **kwargs)

    if isinstance(spec, list):
        return SetArgs([spec], **kwargs)

    if isinstance(spec, tuple):
        return SetArgs([spec], **kwargs)

    if isinstance(spec, set):
        return SetArgs([spec], **kwargs)

    if isinstance(spec, dict):
        return DictArgs([spec], **kwargs)

    if callable(spec):
        return CallableConverter(spec, **kwargs)
    raise ValueError(spec)

def ParseArgSpecString(spec, **kwargs):
    raise NotImplementedError(spec)

    tokens = re.split("([{}()?+*,]) ", spec)
    tokens = iter(tokens)
    token = None

    "Int (INT|CHAR|dict1)+ set0{10} dict0"
