import shlex
import re


class ArgParser:
    def __call__(self, string):
        raise NotImplementedError("This is a ABC")

    def complete(self, string):
        return []

class NoArgs(ArgParser):
    """ Takes no arguments """

    def __call__ (self, string):
        string = string.strip()
        if string != '':
            raise ValueError("Not expecting an argument!, got: " + string)
        return []

class NoOrOneArgs(ArgParser):
    """ Takes no or one argument of arbitrary format """

    def __call__ (self, string):
        string = string.strip()
        if string != '':
            return [string]
        return []

class AllArgs(ArgParser):
    """ Takes one argument of arbitrary format """

    def __call__ (self, string):
        return [string]

class ShellArgs(ArgParser):
    """ Takes shellencoded arguments """

    def __call__(self,string):
        a = shlex.split(string)
        return a

class GetOptsArgs(ArgParser):
    """ Takes the following "getopt" arguments:\n%s """
    def __init__(self, opts, **kwargs):
        super().__init__(**kwargs)
        self.opts = opts
        self.__doc__ = self.__doc__ % (opts,)

    def __call__(string):
        raise NotImplemented()

class SetArgs(ArgParser):
    """ Takes one of these argumwents: \n%s """
    def __init__(self, sets, **kwargs):
        super().__init__(**kwargs)
        self.sets=sets
        self.__doc__ = self.__doc__ % (", ".join(sorted(k for s in sets for k in s)))

    def __call__(self, string):
        string = string.strip()
        for s in self.sets:
            if string in s:
                return [string]

        raise ValueError (string, self.sets)

    def complete(self, string):
        string = string.strip()
        for s in self.sets:
            for e in s:
                if e.startswith(string):
                    yield e

class DictArgs(SetArgs):
    """ Takes one of these argumwents: \n%s """
    def __init__(self, dicts, **kwargs):
        super().__init__(dicts, **kwargs)

    def __call__(self, string):
        string = string.strip()
        for s in self.sets:
            if string in s:
                return [s[string]]
        raise ValueError (string, self.sets)


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

    raise ValueError(spec)

def ParseArgSpecString(spec, **kwargs):
    raise NotImplementedError(spec)
    tokens = re.split("([{}()?+*,]) ", spec)
    tokens = iter(tokens)
    token = None

    "Int (INT|CHAR|dict1)+ set0{10} dict0"
