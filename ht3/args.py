"""Argument Parsing for commands."""

import shlex
import pathlib
import inspect
import collections.abc
import getopt
import ht3.complete
import ht3.env

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
        ht3.complete.complete_Path(s)

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

        params = iter(sig.parameters.items())
        self.params = []
        for name, param in params:
            if param.kind in [param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD]:
                # X
                # X=1
                var_arg = False
            elif param.kind == param.VAR_POSITIONAL:
                # *args
                var_arg = True
            elif param.kind == param.KEYWORD_ONLY:
                if param.default == param.empty:
                    # *, X=1
                    raise TypeError("Non positional parameter without default", name, param)
                else:
                    # *, X=1
                    continue
            elif param.kind == param.VAR_KEYWORD:
                # **kwargs
                continue
            else:
                assert False

            self.params.append((var_arg, self.ParamAnno(param.annotation)))

        if len(self.params) == 1 and not self.params[0][0]:
            self.split = lambda s: [s]
        else:
            self.split = shlex.split



    def __call__(self, string):
        string = string.strip()
        if not string:
            return [],{}
        it = iter(self.split(string))
        args = []
        params = iter(self.params)
        for var_arg, param in params:
            if var_arg:
                args.extend(param.convert(v) for v in it)
            else:
                try:
                    v = next(it)
                except StopIteration:
                    break
                args.append(param.convert(v))
        assert not list(params)
        return args, {}

    def complete(self, string):
        if len(self.params) == 0:
            return []

        for quote in ['', '"', "'"]:
            try:
                values = self.split(string+quote+'|') # pipe for cursor pos
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
            prefix = string + quote
            if len(values) > 1:
                prefix += " "
        else:
            s = values[-1][:-1]
            i = len(values) - 1
            prefix = string[:len(string)-len(s)]


        if i <= len(self.params):
            var_arg, param = self.params[i]
        else:
            var_arg, param = self.params[-1]
            if not var_arg:
                raise ArgError("Too many arguments",i,len(self.params))

        for v in param.complete(s):
            if shlex._find_unsafe(v) is None:
                s = prefix + v + quote
                if s.startswith(string):
                    yield s
            else:
                if quote:
                    s = prefix + v.replace(quote, "\\"+quote) + "'"
                    if s.startswith(string):
                        yield s
                else:
                    pass # can not help if it did not start with a quote

    class ParamAnno:
        def __init__(self, typ):
            if typ is inspect.Parameter.empty:
                complete = None
                convert  = str
            elif callable(typ):
                def complete(s):
                    c = getattr(ht3.env.Env, '_complete_'+typ.__name__, False)
                    if c:
                        return c(s)
                    c = getattr(ht3.env.Env, 'complete_'+typ.__name__, False)
                    if c:
                        return c(s)
                    return []
                convert = typ
            elif isinstance(typ, str):
                def complete(s):
                    c = getattr(ht3.env.Env, '_complete_'+typ, False)
                    if c:
                        return c(s)
                    c = getattr(ht3.env.Env, 'complete_'+typ, False)
                    if c:
                        return c(s)
                    return []
                def convert(s):
                    c = getattr(ht3.env.Env, '_convert_'+typ, False)
                    if c:
                        return c(s)
                    c = getattr(ht3.env.Env, 'convert_'+typ, False)
                    if c:
                        return c(s)
                    return s
            elif (isinstance(typ, collections.abc.Mapping)
                    or isinstance(typ, collections.abc.Sequence)):
                complete = lambda s: ht3.complete.filter_completions(s, typ)
                def convert(s):
                    if not s in typ:
                        raise KeyError("not in list", s, typ)
                    return s
            # UPGRADE: Add typing.Union once support for python3.4 is dropped
            else:
                raise TypeError(typ)

            self.complete = complete
            self.convert = convert

def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"

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
