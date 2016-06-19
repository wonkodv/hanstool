"""Argument Parsing for commands."""

import collections
import collections.abc
import getopt
import ht3.complete
import ht3.env
import inspect
import pathlib
import shlex

def _no_completion(s):
    return []

class Param:
    def __init__(self, convert=str, complete=_no_completion, doc=None):
        if not callable(convert):
            raise TypeError("Convert should be callable", convert)
        self.convert = convert
        if not callable(complete):
            if isinstance(complete, collections.abc.Sequence):
                self.complete = lambda s: complete
            else:
                raise TypeError("Complete should be callable", convert)
        else:
            self.complete = complete

        if doc is None:
            doc = "Param(convert={0}, complete={1})".format(self.convert, self.complete)
        self.doc = doc

    def __repr__(self):
        return self.doc

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
        if len(self.params) < len(strings):
            raise ArgError("More arguments than specified types")
        return [p.convert(s) for p,s in zip(self.params, strings)]

    __str__ = lambda self: "Sequence of parameters with the Values: "+str(self.params)

class Union(Param):
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

Str = Param(convert=str, doc="str")
Int = Param(convert=lambda s:int(s,0), complete=['0x', '0b', '0o', '1', '2', '42'], doc="int")
Float = Param(convert=float,complete=[], doc="float")
Python = Param(complete=lambda s:ht3.env.Env.complete_py(s),
                doc="PythonCode")
Path = Param(convert=pathlib.Path,
             complete=lambda s:ht3.env.Env.complete_path(s),
             doc="Path")
Executable = Param(complete=lambda s:ht3.env.Env.complete_executable(s), doc="Executable")
ExecutableWithArgs = Param(complete=lambda s:ht3.env.Env.complete_executable_with_args(s), doc="ExecutableWithArgs")
Command = Param(complete=lambda s:ht3.env.Env.complete_commands(s), doc="Command")
CommandWithArgs = Param(complete=lambda s:ht3.env.Env.complete_command_with_args(s),
                        doc="CommandWithArgs")

def _convert_bool(s):
    s = s.lower()
    if not s:
        raise ValueError()
    if s in ['n','no','false']:
        return False
    if s in ['yes','true','y']:
        return True
    raise ValueError("Not a boolean word", s)

def _complete_bool(s):
    if s:
        return ht3.complete.filter_completions_i(s,
            ["yes", "no", "true", "false", "0", "1"])
    return ["Yes", "No"]

Bool = Param(convert=_convert_bool, complete=_complete_bool, doc="bool")

class Range(Param):
    def __init__(self, range):
        self.range = range

    def complete(self, s):
        return (str(i) for i in self.range)

    def convert(self, s):
        i = int(s, 0)
        if i in self.range:
            return i
        raise ValueError("Out of range", i, self.range)

class Option(Param):
    def __init__(self, options, ignore_case=False, sort=False):
        self.options = options
        self.ignore_case = ignore_case
        self.sort = sort
        self.doc="Option"

    def complete(self, s):
        if self.ignore_case:
            c = ht3.complete.filter_completions_i(s, self.options)
        else:
            c = ht3.complete.filter_completions(s, self.options)
        if self.sort:
            c = sorted(c)
        return c

    def convert(self, s):
        if self.ignore_case:
            sl = s.lower()
            ic = True
        else:
            ic = False
        for o in self.options:
            if ic:
                if sl == o.lower():
                    return o
            else:
                if s == o:
                    return o
        raise ValueError(s)

    __str__ = lambda self: "Option of "+str([o for opts in self.options for o in opts])

def _get_param(p, var_arg):
    if var_arg:
        if isinstance(p, MultiParam):
            return p
        if p is inspect.Parameter.empty:
            return MultiParam(Str)
        if isinstance(p, Param):
            return MultiParam(p)
        if inspect.isclass(p):
            if issubclass(p, MultiParam):
                raise TypeError("Instantiate your Param Type")
        raise TypeError("Need Specific Parameter Annotation for *args", p)

    if isinstance(p, Param):
        return p
    if isinstance(p, str):
        raise TypeError("Can not convert a String to a Param", p)

    if isinstance(p, collections.abc.Sequence):
        if (any(isinstance(e, (Param, MultiParam)) for e in p) or
                not any(isinstance(e, str) for e in p)):
            raise TypeError("Give a list of allowed strings")

        return Option(p)

    if p is inspect.Parameter.empty:
        return Param()
    if p is bool:
        return Bool
    if p is str:
        return Str
    if p is int:
        return Int
    if p is float:
        return Float
    if p is pathlib.Path:
        return Path
    if p is range:
        return Range(p)

    if callable(p):
        try:
            n = p.__name__.lower()
        except AttributeError:
            pass
        else:
            if 'convert' in n:
                return Param(convert=p)
            elif 'complete' in n:
                return Param(complete=p)
            else:
                raise TypeError("Can not convert function to param if name does not"
                    " contain 'convert' or 'complete'", p)

    raise TypeError("Can not Guess Parameter type", p)

_param_info = collections.namedtuple('param_info',['name', 'multiple', 'positional', 'keyword', 'optional', 'typ'])


class BaseArgParser:
    def __init__(self):
        raise NotImplementedError("ABC")

    def describe_params(self):
        raise NotImplementedError("ABC")


class NoArgParser(BaseArgParser):
    def __init__(self, param_info):
        self.param_info = param_info

    def convert(self, s):
        assert not s.strip()
        return [],{}

    def complete(self, s):
        return []

    def describe_params(self):
        return "No Arguments"

class SingleArgParser(BaseArgParser):
    def __init__(self, param_info):
        self.param_info = param_info

    def convert(self, s):
        if self.param_info.optional:
            if not s.strip():
                return [], {}
        return [self.param_info.typ.convert(s)], {}

    def complete(self, s):
        return self.param_info.typ.complete(s)

    def describe_params(self):
        return ("Takes one param:\n"
                "%s%s: %s" % ( self.param_info.name,
                            '?' if self.param_info.optional else '',
                            self.param_info.typ))

class ShellArgParser(BaseArgParser):
    def __init__(self, param_info):
        self.param_info = [pi for pi in param_info if pi.positional]

    def convert(self, string):
        string = string.strip()
        it = iter(shlex.split(string))
        args = []
        param_info = iter(self.param_info)
        for param in param_info:
            if param.multiple:
                args.extend(param.typ.convert(list(it)))
            else:
                try:
                    v = next(it)
                except StopIteration:
                    break
                args.append(param.typ.convert(v))
        return args, {}

    def complete(self, string):
        if len(self.param_info) == 0:
            return []

        for quote in ['', '"', "'"]:
            try:
                values = shlex.split(string+quote+'|') # pipe for cursor pos
            except ValueError:
                continue
            else:
                break
        else:
            # raise the error:
            shelx.split(string)

        assert values[-1][-1] == '|'

        current = values[-1][:-1]
        values = values[:-1]

        prefix = string[:len(string)-len(current)]


        if len(values)+1 <= len(self.param_info):
            pi = self.param_info[len(values)]
        else:
            pi = self.param_info[-1]
            if not pi.multiple:
                raise ArgError("Too many arguments",i,len(self.params))
            values = values[len(self.param_info):] + [current]


        if pi.multiple:
            assert isinstance(pi.typ, MultiParam)
            compl = pi.typ.complete(values)
        else:
            assert isinstance(pi.typ, Param)
            compl = pi.typ.complete(current)

        for v in compl:
            if shlex._find_unsafe(v) is None:
                s = prefix + v + quote
                if s.startswith(string):
                    yield s
            else:
                if quote:
                    s = prefix + v.replace(quote, "\\"+quote) + quote
                    if s.startswith(string):
                        yield s
                else:
                    if v.startswith(current):
                        s = (
                            prefix + 
                            current +
                            '"'+ 
                            v[len(current):].replace('"', r'\"') +
                            '"'
                        )
                        assert s.startswith(string)
                        yield s

    def describe_params(self):
        param_info = self.param_info
        if not param_info:
            return "No Parameters"
        else:
            s =["Takes the following params:"]
            for pi in param_info:
                s.append("%s%s%s: %s" % ("*" if pi.multiple else '',
                                        pi.name,
                                       '?' if pi.optional else '',
                                        pi.typ))
            return "\n".join(s)


def ArgParser(function, typ='auto'):
    sig = inspect.signature(function)
    param_info = []
    sig_params = iter(sig.parameters.items())
    for name, sig_param in sig_params:
        if sig_param.kind == sig_param.POSITIONAL_ONLY:
            # some builtin functions. shouldnt happen often!
            multiple=False
            positional=True
            keyword=False
            optional=(sig_param.default != sig_param.empty)
        elif sig_param.kind == sig_param.POSITIONAL_OR_KEYWORD:
            # X=1
            multiple=False
            positional=True
            keyword=True
            optional=(sig_param.default != sig_param.empty)
        elif sig_param.kind == sig_param.KEYWORD_ONLY:
            # *, X=1
            multiple = False
            positional = False
            keyword = True
            optional=(sig_param.default != sig_param.empty)
        elif sig_param.kind == sig_param.VAR_POSITIONAL:
            # *args
            multiple = True
            positional = True
            keyword = True
            optional = True
        elif sig_param.kind == sig_param.VAR_KEYWORD:
            # **kwargs
            multiple = True
            positional = False
            keyword = True
            optional = True
        else:
            assert False

        pi = _param_info(
            multiple=multiple,
            positional=positional,
            keyword=keyword,
            optional=optional,
            name=name,
            typ=_get_param(sig_param.annotation, multiple))
        param_info.append(pi)

    if typ == 'auto':
        if len(param_info) == 1 and not param_info[0].multiple:
            return SingleArgParser(param_info[0])

        if all(i.positional or i.optional for i in param_info):
            return ShellArgParser(param_info)

        #if all(i.keyword or i.optional for i in param_info):
        #    return GetOptArgParser()
        # TODO

        raise TypeError("No matching argument parser", param_info)

    if typ in [None, 0]:
        if all(i.optional for i in param_info):
            return NoArgParser()
        raise TypeError("There are required paramertes", param_info)

    if typ in ['shell']:
        if all(i.positional or i.optional for i in param_info):
            return ShellArgParser(param_info)
        raise TypeError("There are required non-positional paramertes", param_info)

    #if all(i.keyword or i.optional for i in param_info):
    #    return GetOptArgParser()
    # TODO

    raise TypeError("No matching argument parser", param_info)
