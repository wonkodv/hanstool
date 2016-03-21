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

def filterDict(d, *keys):
    return dict((k,d[k]) for k in d if k in keys)

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


    def complete(self, s):
        ht3.complete.complete_path(s)

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
        sig = inspect.signature(command.function)
        self.__doc__ = self.__doc__ % (sig)

        params = list(sig.parameters.items())
        if len(params) == 1 and params[0][1].kind in [
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD]:
            self.split = lambda s: [s]
        else:
            self.split = shlex.split

        convert = []
        self.convert = convert
        for name, p in params:
            t = p.annotation
            if p.kind in [p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD]:
                convert.append([False,t])
            elif p.kind == p.VAR_POSITIONAL:
                convert.append([True,t])
                break
            else:
                raise TypeError("Can not handle parameter", name, p, sig)

    def __call__(self, string):
        string = string.strip()
        if not string:
            return [],{}
        it = iter(self.split(string))
        args = []
        for consume_all, typ in self.convert:
            if typ is inspect.Parameter.empty:
                typ = str
            elif callable(typ):
                pass
            elif typ == 'py':
                typ = str
            else:
                raise TypeError(typ)

            if consume_all:
                args.extend( typ(v) for v in it)
            else:
                try:
                    v = next(it)
                except StopIteration:
                    break
                args.append(typ(v))
        return args, {}

    def complete(self, string):
        if len(self.convert) == 0:
            return []

        for append in ['', '"', "'"]:
            try:
                values = self.split(string+append+'|') # pipe for cursor pos
            except ValueError:
                continue
            else:
                break
        else:
            # raise the error:
            self.split(string)

        assert values[-1][-1] == '|'

        if values[-1] == '|':
            values = values[:-1]
            new = True
            i = len(values)
            s = ""
            prefix = string + append + " "
        else:
            s = values[-1][:-1]
            i = len(values) - 1
            prefix = string[:len(string)-len(s)]


        if i <= len(self.convert):
            consume_all, typ = self.convert[i]
        else:
            consume_all, typ = self.convert[-1]
            assert consume_all

        if typ == pathlib.Path:
            values = ht3.complete.complete_path(s)
        else:
            values = [s+typ.__name__]

        for v in values:
            yield prefix + v

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
            return SetArgs(*s, **filterDict(kwargs, 'default'))

        if spec == 'dict':
            d = []
            if 'dict' in kwargs:
                d.append(kwargs['dict'])
            if 'dicts' in kwargs:
                d.extend(kwargs['dicts'])
            if not d:
                raise KeyError('Pass a dict in `dict` or `dicts`')
            return DictArgs(*d, **filterDict(kwargs, 'default'))

        if spec == 'callable':
            return CallableArgParser(kwargs['call'], **filterDict(kwargs, 'default'))

        if spec == 'getopt':
            return GetOptsArgs(kwargs['opt'])

        if spec.startswith(':'):
            return GetOptsArgs(spec[1:])

        if spec == 'auto':
            return AutoArgs(kwargs['_command'])

    if isinstance(spec, ArgParser):
        return spec

    if isinstance(spec, collections.abc.Mapping):
        return DictArgs(spec, **filterDict(kwargs, 'default'))

    if isinstance(spec, collections.abc.Container):
        return SetArgs(spec, **filterDict(kwargs, 'default'))

    if callable(spec):
        return CallableArgParser(spec, **filterDict(kwargs, 'default'))

    raise ValueError(spec)
