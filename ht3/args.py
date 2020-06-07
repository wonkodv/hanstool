"""Argument Parsing for commands."""

import collections
import collections.abc
import functools
import getopt
import ht3.complete
import inspect
import pathlib
import shlex
import sys

_DEFAULT = object()


class ArgError(Exception):
    pass


class ParamClassMeta(type):
    """(virtual) MetaClass of ParamClasses.

    Any class that has convert or complete methods is considered a subclss of ParamClass.
    """

    def __subclasscheck__(self, other):
        if super().__subclasscheck__(other):
            return True
        if issubclass(other, BaseParam):
            return False
        for m in ['convert', 'complete']:
            for c in inspect.getmro(other):
                f = getattr(c, m, None)
                if inspect.ismethod(
                        f):  # classmethods are bound, methods of calsses not
                    break
            else:
                break
        else:
            return True
        return False


class ParamClass(metaclass=ParamClassMeta):
    """Parameter where the Class is the param type.

    Used when the Parameter Type has no Arguments:

        class MyParam(ParamClass): pass
        @cmd
        def foo(a:MyParam):
    """

    @classmethod
    def convert(cls, s):
        return s

    @classmethod
    def complete(cls, s):
        return []


class BaseParam:
    """Parameter where an instance of the class is the param type.

    Used when the param type has Arguments:

        class MyParam(BaseParam): pass
        @cmd
        def foo(a:My(some_args)):
    """

    def _no_completion(self, s):
        return []

    def _no_conversion(self, s):
        return s

    complete = _no_completion
    convert = _no_conversion

    def __call__(self, s):
        return self.convert(s)

    def __repr__(self):
        if self.__doc__:
            return self.__doc__
        return type(self).__name__


def Param(convert=_DEFAULT, complete=_DEFAULT, doc=_DEFAULT):
    """Create quick Parameter Object"""

    p = BaseParam()

    if convert is not _DEFAULT:
        if not callable(convert):
            raise TypeError("Convert should be callable", convert)
        p.convert = convert

    if complete is not _DEFAULT:
        if callable(complete):
            p.complete = complete
        else:
            if isinstance(complete, collections.abc.Sequence):
                def complete_from_sequence(s):
                    return complete
                p.complete = complete_from_sequence
            else:
                raise TypeError("Complete should be callable", convert)

    if doc is not _DEFAULT:
        p.__doc__ = doc
    elif complete is not _DEFAULT or convert is not _DEFAULT:
        p.__doc__ = f"Param(convert={p.convert}, complete={p.complete})"
    return p


class MultiParam:
    """Multiple Params of the Same Type."""

    def __init__(self, param):
        self.param = _get_param(param, False)

    def complete(self, strings):
        if strings:
            return self.param.complete(strings[-1])
        return self.param.complete("")

    def convert(self, strings):
        return [self.param.convert(s) for s in strings]

    def __repr__(self):
        return repr(self.param)


class Sequence(MultiParam):
    """Multiple Parameters with different Types."""

    def __init__(self, *params):
        self.params = [_get_param(p, False) for p in params]

    def complete(self, strings):
        s = strings[-1]
        p = self.params[len(strings) - 1]
        return p.complete(s)

    def convert(self, strings):
        if len(self.params) < len(strings):
            raise ArgError("More arguments than specified types")
        return [p.convert(s) for p, s in zip(self.params, strings)]

    def __repr__(self):
        return "Sequence of parameters with the Values: " + repr(self.params)


class Union(BaseParam):
    """One Parameter that can have one of several Types."""

    def __init__(self, *params):
        self.params = [_get_param(p, False) for p in params]

    def complete(self, s):
        for p in self.params:
            yield from p.complete(s)

    def convert(self, s):
        for p in self.params:
            try:
                return p.convert(s)
            except ValueError:
                pass
        raise ValueError("No Conversion succeeded", s)

    def __repr__(self):
        return "Parameter that has one of the types: " + repr(self.params)


Str = Param(convert=str, doc="str")
Int = Param(convert=lambda s: int(s, 0), complete=['42'], doc="int")
Float = Param(convert=float, complete=[], doc="float")


def _convert_bool(s):
    s = s.lower()
    if not s:
        raise ValueError()
    if s in ['n', 'no', 'false']:
        return False
    if s in ['yes', 'true', 'y']:
        return True
    raise ValueError("Not a boolean word", s)


def _complete_bool(s):
    if s:
        return ht3.complete.filter_completions_i(
            s, ["yes", "no", "true", "false", "0", "1"])
    return ["Yes", "No"]


Bool = Param(convert=_convert_bool, complete=_complete_bool, doc="bool")


class Range(BaseParam):
    """Parameter has to be in Range."""

    def __init__(self, *r):
        self.range = range(*r)

    def complete(self, s):
        return (str(i) for i in self.range)

    def convert(self, s):
        i = int(s, 0)
        if i in self.range:
            return i
        raise ValueError("Out of range", i, self.range)

    def __repr__(self):
        return "Parameter in the range: " + repr(self.range)


def _convert_time(string):
    try:
        return float(string)
    except ValueError:
        pass
    x = 0
    h = 0
    m = 0
    s = 0
    for c in string.upper():
        if c == "H":
            if s != 0 or m != 0 or h != 0:
                raise ValueError(string)
            h = x
            x = 0
        elif c == "M":
            if s != 0 or m != 0:
                raise ValueError(string)
            m = x
            x = 0
        elif c == "S":
            if s != 0:
                raise ValueError(string)
            s = x
            x = 0
        elif c in "0123456789":
            if s != 0:
                raise ValueError(string)
            x = x * 10 + int(c)
        else:
            raise ValueError(string)
    return (h * 60 + m) * 60 + s


def _complete_time(s):
    if not s:
        yield from ["1", "0.1", "3M", "1H5M"]
    else:
        if any(c not in "0123456789HMS" for c in s):
            return
        if s[-1] in "HMS":
            s = s + "1"
        p = {"H", "M", "S", ".0"}
        if "H" in s.upper():
            p = {"M", "S"}
        if "M" in s.upper():
            p = {"S"}
        if "S" in s.upper():
            p = {}
        for x in p:
            yield s + x


Time = Param(
    convert=_convert_time,
    complete=_complete_time,
    doc="Time, as 1H5M3S or 5.0")


class Option(BaseParam):
    """Param can/must be on of a set of options."""

    def __init__(
            self,
            options,
            ignore_case=False,
            sort=False,
            allow_others=False):
        """Init.

        options: Possible Options,
        ignore_case: Convert to lower, ignore case when completing
        sort: sort completion options
        allow_others: accept values not in `options`
        """
        self.options = options
        self.ignore_case = ignore_case
        self.sort = sort
        self.allow_others = allow_others

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
        if self.allow_others:
            return s
        raise ValueError(s)

    def __repr__(self):
        return "Option of " + repr(list(self.options))


def _get_param(p, var_arg):
    if var_arg:
        if isinstance(p, MultiParam):
            return p
        if p is inspect.Parameter.empty:
            return MultiParam(Str)
        if isinstance(p, BaseParam):
            return MultiParam(p)
        if issubclass(p, ParamClass):
            return MultiParam(p)
        if inspect.isclass(p):
            if issubclass(p, MultiParam):
                raise TypeError("Instantiate your Param Type")
        raise TypeError("Need Specific Parameter Annotation for *args", p)

    if isinstance(p, BaseParam):
        return p

    try:
        if issubclass(p, ParamClass):
            return p
    except TypeError:
        pass

    try:
        b = issubclass(p, BaseParam)
    except TypeError:
        pass
    else:
        if b:
            return p()  # raise errors if there is no 0 argument Constructor

    if isinstance(p, str):
        raise TypeError("Can not convert a String to a Param", p)

    if isinstance(p, collections.abc.Sequence):
        if (any(isinstance(e, (BaseParam, MultiParam)) for e in p) or not any(
                isinstance(e, str) for e in p)):  # allow ['a','1',2] use only a and 1
            raise TypeError("Give a list of allowed strings", p)

        return Option(p)

    if p is inspect.Parameter.empty:
        return BaseParam()
    if p is bool:
        return Bool
    if p is str:
        return Str
    if p is int:
        return Int
    if p is float:
        return Float
    if p is range:
        return Range(p)
    if p is pathlib.Path:
        return ht3.args.Path  # someone will patch this in

    if inspect.isclass(p):
        raise TypeError(
            "Classes can not be Argument types.", p, "Exceptions: \n"
            "* they specify convert and complete as classmethods\n"
            "* they are subclasses of ParamClass\n"
            "* they are Subclass of BaseParam and accept an empty constructor")

    if inspect.isfunction(p):
        n = p.__name__.lower()
        if 'convert' in n:
            return Param(convert=p)
        if 'complete' in n:
            return Param(complete=p)
        raise TypeError(
            "Can not convert function to param if name does not"
            " contain 'convert' or 'complete'", p)

    raise TypeError("Can not Guess Parameter type", p)


class BaseArgParser:
    """ABC for Argument Parsers."""

    def __init__(self):
        raise NotImplementedError("ABC")

    def describe_params(self):
        raise NotImplementedError("ABC")


class NoArgParser(BaseArgParser):
    """Argument Parser for no Arguments."""

    def __init__(self):
        pass

    def convert(self, s):
        if s.strip():
            raise ArgError("No Arguments Expected")
        return [], {}

    def complete(self, s):
        return []

    def describe_params(self):
        return "No Arguments"


class SingleArgParser(BaseArgParser):
    """Parser for single Arguments."""

    def __init__(self, helper):
        self.helper = helper
        self.param_info = list(helper.param_info.values())[0]

    def convert(self, s):
        if not s:
            if self.param_info.optional:
                args = []
            else:
                raise ArgError("Expected 1 argument")
        else:
            args = [s]

        return self.helper.apply_args(args, {})

    def complete(self, s):
        return self.param_info.typ.complete(s)

    def describe_params(self):
        return ("Takes one param:\n"
                "%s%s: %s" % (self.param_info.name,
                              '?' if self.param_info.optional else '',
                              self.param_info.typ))


class ShellArgParser(BaseArgParser):
    """Shell-like Argument Parser."""

    def __init__(self, helper):
        self.helper = helper
        self.param_info = [
            pi for pi in helper.param_info.values() if pi.positional]

    def convert(self, string):
        args = shlex.split(string)
        try:
            return self.helper.apply_args(args, {})
        except TypeError as e:
            raise ValueError("Arguments do not match", *e.args, args)

    def complete(self, string):
        param_info = self.param_info
        if len(param_info) == 0:
            return

        for quote in ['', '"', "'"]:
            try:
                values = shlex.split(
                    string + quote + '|')  # pipe for cursor pos
            except ValueError:
                continue
            else:
                break
        else:
            # raise the error:
            shlex.split(string)

        assert values[-1][-1] == '|'

        current = values[-1][:-1]
        values = values[:-1]

        prefix = string[:len(string) - len(current)]

        if len(values) < len(param_info):
            pi = param_info[len(values)]
        else:
            pi = param_info[-1]
            if not pi.multiple:
                raise ArgError(
                    "Too many arguments",
                    len(values),
                    len(param_info))
            values = values[len(param_info):] + [current]

        if pi.multiple:
            compl = pi.typ.complete(values)
        else:
            compl = pi.typ.complete(current)

        for v in compl:
            if not shlex._find_unsafe(v):
                s = prefix + v + quote
                if s.startswith(string):
                    yield s
            else:
                if quote:
                    s = prefix + v.replace(quote, "\\" + quote) + quote
                    if s.startswith(string):
                        yield s
                else:
                    if v.startswith(current):
                        rem = v[len(current):]
                        if shlex._find_unsafe(rem):
                            rem = '"' + rem.replace('"', r'\"') + '"'
                        yield string + rem

    def describe_params(self):
        param_info = self.param_info

        if not param_info:
            return "No Parameters"

        s = ["Takes the following params:"]
        for pi in param_info:
            s.append("%s%s%s: %s" % ("*" if pi.multiple else '',
                                     pi.name,
                                     '?' if pi.optional else '',
                                     pi.typ))
        return "\n".join(s)


class GetOptArgParser(BaseArgParser):
    """Takes "getopt" arguments."""

    def __init__(self, opts, helper):
        self.opts = opts
        self.helper = helper

    def complete(self, string):
        if not string or string[-1] == ' ':
            for o in self.opts:
                if o != ':':
                    yield string + '-' + o
        if string[-1] == '-' and (len(string) == 1 or string[-2] == ' '):
            for o in self.opts:
                if o != ':':
                    yield string + o

    def convert(self, string):
        optlist, args = getopt.gnu_getopt(shlex.split(string), self.opts)
        kwargs = {}
        for k, v in optlist:
            k = k[1:]
            if v == '':
                # opts a:b, args -a '' -a '' will give a:2 but who would do
                # such a thing
                if k in kwargs:
                    v = kwargs[k] + 1
                else:
                    v = 1
            else:
                if k in kwargs:
                    raise ValueError("option -%s occured multiple times" % k)
            kwargs[k] = v

        return self.helper.apply_args(args, kwargs)

    def describe_params(self):
        return "GetOpt Args: " + self.opts


def ArgParser(function, typ, apply_defaults):
    """Create the right Argument Parser for a function.

    function: the function to parse for,
    typ: ArgumentParser or strategy ['auto', 'shell', False for No Args, 1 for 1 argument, :opts for opts]"""

    if isinstance(typ, BaseArgParser):
        return typ
    if isinstance(typ, type):
        raise NotImplementedError(
            "No convention for passing classes as arg parsers")

    helper = ParamHelper(function, apply_defaults)

    param_info = list(helper.param_info.values())

    if isinstance(typ, str) and typ.startswith(':'):
        return GetOptArgParser(typ[1:], helper)

    if typ == 'auto':
        if len(param_info) == 0:
            return NoArgParser()

        if len(param_info) == 1 and not param_info[0].multiple:
            return SingleArgParser(helper)

        if all(i.positional or i.optional for i in param_info):
            return ShellArgParser(helper)

        # if all(i.keyword or i.optional for i in param_info):
        #    return GetOptArgParser()
        # TODO

        raise TypeError("No matching argument parser", param_info)

    if typ in [1, '1']:
        if len(param_info) > 1:
            if not param_info[0].multiple:
                if all(i.optional for i in param_info[1:]):
                    return SingleArgParser(helper)
            raise TypeError(
                "There are more than 1 required paramertes",
                param_info)
        raise TypeError("No paramerter expected", param_info)

    if typ in [None, 0, False]:
        if all(i.optional for i in param_info):
            return NoArgParser()
        raise TypeError("There are required paramertes", param_info)

    if typ in ['shell']:
        if all(i.positional or i.optional for i in param_info):
            return ShellArgParser(helper)
        raise TypeError(
            "There are required non-positional paramertes",
            param_info)

    raise TypeError("No matching argument parser", param_info)


class ParamHelper():
    """Helper that applies Arguments to function Parameters."""

    _param_info = collections.namedtuple(
        'param_info', [
            'name', 'multiple', 'positional', 'keyword', 'optional', 'typ'])

    def __init__(self, f, apply_defaults):
        self.sig = inspect.signature(f)
        self.function = f
        self.apply_defaults = apply_defaults

        self.param_info = collections.OrderedDict()

        for name, sig_param in self.sig.parameters.items():
            if sig_param.kind == sig_param.POSITIONAL_ONLY:
                # some builtin functions. shouldnt happen often!
                multiple = False
                positional = True
                keyword = False
                optional = (sig_param.default != sig_param.empty)
            elif sig_param.kind == sig_param.POSITIONAL_OR_KEYWORD:
                # X=1
                multiple = False
                positional = True
                keyword = True
                optional = (sig_param.default != sig_param.empty)
            elif sig_param.kind == sig_param.KEYWORD_ONLY:
                # *, X=1
                multiple = False
                positional = False
                keyword = True
                optional = (sig_param.default != sig_param.empty)
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

            pi = self._param_info(
                multiple=multiple,
                positional=positional,
                keyword=keyword,
                optional=optional,
                name=name,
                typ=_get_param(sig_param.annotation, multiple))
            self.param_info[name] = pi

    def apply_args(self, args, kwargs):
        ba = self.sig.bind(*args, **kwargs)
        if self.apply_defaults:
            ba.apply_defaults()
        for name in ba.arguments:
            pi = self.param_info[name]
            ba.arguments[name] = pi.typ.convert(ba.arguments[name])
        return ba.args, ba.kwargs


def enforce_args(_f=None, *, apply_defaults=False):
    def deco(f):
        h = ParamHelper(f, apply_defaults)

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            args, kwargs = h.apply_args(args, kwargs)
            return f(*args, **kwargs)
        return wrapper

    if _f is None:
        return deco

    return deco(_f)
