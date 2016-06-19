"""Argument Parsing for commands."""

import shlex
import pathlib
import inspect
import collections.abc
import getopt
import ht3.complete
import ht3.env

class BaseParam:
    def __init__(self):
        pass

    def complete(self, string):
        return []

    def convert(self, string):
        return string

    __str__ = lambda self: type(self).__name__

class MultiParam:
    def __init__(self, param):
        self.param = _get_param(param, False)

    def complete(self, strings):
        return self.param.complete(strings[-1])

    def convert(self, strings):
        return [self.param.convert(s) for s in strings]

    __str__ = lambda self: str(self.param)

class Sequence(MultiParam):
    def __init__(self, *params):
        self.params = [_get_param(p, False) for p in params]

    def complete(self, strings):
        s = strings[-1]
        p = self.params[len(strings)-1]
        return p.complete(s)

    def convert(self, strings):
        if len(self.params) < len(self.strings):
            raise ArgError("More arguments than specified types")
        return [p.convert(s) for p,s in zip(self.params, strings)]

    __str__ = lambda self: "Sequence of parameters with the Values: "+str(self.params)

class Union(BaseParam):
    def __init__(self, *params):
        self.params = [_get_param(p, False) for p in params]

    def complete(self, s):
        for p in self.params:
            for c in p.complete(s):
                yield c

    def convert(self, s):
        for p in self.params:
            try:
                return p.convert(s)
            except ValueError:
                continue
        else:
            raise ValueError("No Conversion succeeded", s)

    __str__ = lambda self: "Parameter that has one of the types: "+str(self.params)

class Str(BaseParam):
    def __init__(self, complete=None):
        if complete:
            assert callable(complete)
            self.complete=complete

    def __str__(self):
        if self.complete.__name__ == 'complete':
            return "String"
        n = self.complete.__name__
        return "String (%s) " % n.replace('_',' ').replace('complete','').strip()

class Int(BaseParam):
    complete = lambda _,s: ['0x', '0b', '0o']
    convert  = lambda _,s: int(s,0)

class Float(BaseParam):
    complete = lambda _,s: []
    convert  = lambda _,s: float(s)

class Option(BaseParam):
    def __init__(self, *options, ignore_case=False):
        self.options = options
        self.ignore_case = ignore_case

    def complete(self, s):
        if self.ignore_case:
            return ht3.complete.filter_completions_i(s, *self.options)
        else:
            return ht3.complete.filter_completions(s, *self.options)

    def convert(self, s):
        if self.ignore_case:
            sl = s.lower()
            ic = True
        else:
            ic = False
        for opts in self.options:
            for o in opts:
                if ic:
                    if sl == o.lower():
                        return o
                else:
                    if sl == o:
                        return o
        raise ValueError(s)

    __str__ = lambda self: "Option of "+str([o for opts in self.options for o in opts])

class Python(BaseParam):
    def complete (self, s):
        return  ht3.env.Env.complete_py(s)
    __str__ = lambda self: "Python Code"

class Path(BaseParam):
    def complete (self, s):
        return  ht3.env.Env.complete_py(s)

    def convert(self, s):
        return pathlib.Path(s)

class Executable(BaseParam):
    def complete (self, s):
        return ht3.env.Env.complete_executable(s)

class ExecutableWithArgs(MultiParam):
    def __init__(self):
        pass

    def complete(self, strings):
        exe = strings[0]
        args = strings[1:]
        if not args:
            return ht3.env.Env.complete_executable(exe)
        raise NotImplementedError()

class Command(BaseParam):
    def complete (self, s):
        return ht3.env.Env.complete_commands(s)

class CommandWithArgs(BaseParam):
    def complete (self, s):
        return ht3.env.Env.complete_command_with_args(s)

class Bool(BaseParam):
    def complete(self, s):
        if s:
            return ht3.complete.filter_completions_i(s,
                ["yes", "no", "true", "false", "0", "1"])
        return ["Yes", "No"]
    def convert(self, s):
        s = s.lower()
        if not s:
            raise ValueError()
        if s in ['n','no','false']:
            return False
        if s in ['yes','true','y']:
            return True
        raise ValueError("Not a boolean word", s)


class ArgParser:
    """Parses and completes a functions parameters."""

    def __init__(self, function):
        sig = inspect.signature(function)
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

            self.params.append((var_arg, _get_param(param.annotation, var_arg), name))

        if len(self.params) == 1 and not self.params[0][0]:
            self.split = lambda s: [s]
        else:
            self.split = shlex.split



    def convert(self, string):
        string = string.strip()
        if not string:
            return [],{}
        it = iter(self.split(string))
        args = []
        params = iter(self.params)
        for var_arg, param, name in params:
            if var_arg:
                args.extend(param.convert(list(it)))
            else:
                try:
                    v = next(it)
                except StopIteration:
                    break
                args.append(param.convert(v))
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

        values[-1] = values[-1][:-1]

        if values[-1] == '':
            prefix = string + quote
            if len(values) > 1:
                prefix += " "
        else:
            s = values[-1]
            prefix = string[:len(string)-len(s)]


        if len(values) <= len(self.params):
            var_arg, param, name = self.params[len(values)-1]
        else:
            var_arg, param, name = self.params[-1]
            if not var_arg:
                raise ArgError("Too many arguments",i,len(self.params))

        assert var_arg == isinstance(param, MultiParam)
        assert var_arg != isinstance(param, BaseParam)

        if var_arg:
            compl = param.complete(values)
        else:
            compl = param.complete(values[-1])

        for v in compl:
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
    def describe_params(self):
        params = self.params
        if not params:
            return "No Parameters"
        else:
            s =["Takes the following params:"]
            for var_arg, param, name in params:
                s.append("%s%s: %s" % ("*" if var_arg else '', name, param))
            return "\n".join(s)


def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"



def _get_param(p, var_arg):
    if var_arg:
        if isinstance(p, MultiParam):
            return p
        if p is inspect.Parameter.empty:
            return MultiParam(Str())
        if isinstance(p, BaseParam):
            return MultiParam(p)
        raise TypeError("Need Specific Parameter Annotation for *args", p)

    if isinstance(p, BaseParam):
        return p

    if isinstance(p, collections.abc.Sequence):
        if (any(isinstance(e, (BaseParam, MultiParam)) for e in p) or 
                not any(isinstance(e, str) for e in p)):
            raise TypeError("Give a list of allowed strings")

        return Option(p)

    if p is inspect.Parameter.empty:
        return BaseParam()
    if p is bool:
        return Bool()
    if p is str:
        return Str()
    if p is int:
        return Int()
    if p is float:
        return Float()
    if p is pathlib.Path:
        return Path()

    try:
        if issubclass(p, BaseParam):
            return p()
    except TypeError:
        pass

    if callable(p):
        try:
            if 'complete' in p.__name__.lower():
                return Str(p)
        except AttributeError:
            pass

    raise TypeError("Can not Guess Parameter type", p)
