"""Register commands."""
import functools
import inspect
import traceback

import ht3.args
import ht3.hook
from .env import Env
from .lib import THREAD_LOCAL, start_thread

COMMANDS = {}

COMMAND_RUN_HOOK = ht3.hook.Hook()
COMMAND_RESULT_HOOK = ht3.hook.Hook()
COMMAND_EXCEPTION_HOOK = ht3.hook.Hook()
COMMAND_NOT_FOUND_HOOK = ht3.hook.ResultHook()

_DEFAULT = object()
_COMMAND_RUN_ID = 0

class NoCommandError(Exception):
    pass

def register_command(func, *, origin_stacked, name=_DEFAULT,
                     async=False, args='auto',
                     doc=_DEFAULT, attrs=None):
    """ Register a function as Command """

    origin = traceback.extract_stack()
    origin = origin[-origin_stacked]
    origin = origin[0:2]

    if async:
        def Command(arg_string=""):
            """ The function that will be executed """
            args, kwargs = arg_parser.convert(arg_string)
            t = start_thread(func, args=args, kwargs=kwargs)
            return t
    else:
        def Command(arg_string=""):
            args, kwargs = arg_parser.convert(arg_string)
            r = func(*args, **kwargs)
            return r

    Command.function = func

    arg_parser = ht3.args.ArgParser(func, args)

    if attrs is None:
        attrs = dict()

    if isinstance(func,functools.partial):
        func_name = func.func.__name__
    else:
        func_name = func.__name__

    if name is _DEFAULT:
        name = func_name

    if doc is _DEFAULT:
        doc = inspect.getdoc(func) or ''

    long_doc = "".join(["Command '%s'" % name, "\n",
        ("Calls %s\n" % func_name ) if func_name != name else "",
        arg_parser.describe_params(), "\n",
        "Executed in a seperate Thread\n" if async else "",
        "\n",
        doc + "\n" if doc else '',
        "\n",
        "Defined in:\n\t%s:%d" % origin
    ])

    Command.__doc__ = long_doc
    Command.doc = doc
    Command.__name__ = func_name
    Command.name = name
    Command.async = async
    Command.origin = origin
    Command.attrs = attrs
    Command.arg_parser = arg_parser

    COMMANDS[name] = Command

    func.__command__ = Command

def cmd(func=None, **kwargs):
    """Decorate a function to become a command

    use as decorator with or without arguments to register a function
    as a command. The function will be registered in its original form
    in the module and in arg parsing form in COMMANDS.
    """

    if func is None:
        def decorator(func):
            """ the actual decorator """
            register_command(func=func, origin_stacked=3, **kwargs)
            return func
        return decorator
    else:
        register_command(func=func, origin_stacked=3, **kwargs)
    return func

def parse_command(string):
    return string.partition(' ')

def get_command(string):
    cmd, sep, args = parse_command(string)
    return COMMANDS[cmd], args

def run_command_func(string, func, args=''):
    global _COMMAND_RUN_ID
    _COMMAND_RUN_ID += 1
    parent = THREAD_LOCAL.command
    THREAD_LOCAL.command = [_COMMAND_RUN_ID, string, func, args, parent]
    COMMAND_RUN_HOOK(
        id=_COMMAND_RUN_ID,
        string=string,
        function=func,
        args=args)
    try:
        result = func(args)
    except Exception as e:
        COMMAND_EXCEPTION_HOOK(
            id=_COMMAND_RUN_ID,
            string=string,
            function=func,
            args=args,
            exception=e)
    else:
        COMMAND_RESULT_HOOK(
            id=_COMMAND_RUN_ID,
            string=string,
            function=func,
            args=args,
            result=result)
        return result
    finally:
        THREAD_LOCAL.command = parent

def run_command(string):
    try:
        cmd, args = get_command(string)
    except KeyError:
        try:
            cmd, args = COMMAND_NOT_FOUND_HOOK(string)
        except ht3.hook.NoResult:
            raise NoCommandError(string) from None

    return run_command_func(string, cmd, args)
