"""Register commands."""
import functools
import inspect
import traceback

import ht3.args
from .env import Env
from .lib import THREAD_LOCAL, start_thread

COMMANDS = {}
RESULT_HISTORY = []
_DEFAULT = object()

_COMMAND_RUN_ID = 0



def register_command(func, *, origin_stacked, name=_DEFAULT,
                     async=False,
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

    arg_parser = ht3.args.ArgParser(func)

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
    return COMMANDS[cmd], sep, args

def run_command_func(c, *args, **kwargs):
    global _COMMAND_RUN_ID
    _COMMAND_RUN_ID += 1

    parent = THREAD_LOCAL.command
    THREAD_LOCAL.command = [_COMMAND_RUN_ID, c.name, parent]

    Env.log_command(c.name)
    r = c(*args, **kwargs);
    Env.log_command_finished(r)

    _, _, p = THREAD_LOCAL.command
    THREAD_LOCAL.command = p

    RESULT_HISTORY.append(r)
    if r is not None:
        Env['_'] = r
    return r

def run_command(string):
    global _COMMAND_RUN_ID
    _COMMAND_RUN_ID += 1

    parent = THREAD_LOCAL.command
    THREAD_LOCAL.command = [_COMMAND_RUN_ID, string, parent]

    Env.log_command(string)
    cmd, _, arg = parse_command(string)
    try:
        cmd = COMMANDS[cmd]
    except KeyError:
        try:
            r = Env.command_not_found_hook(string)
        except Exception as e:
            # prevent this exception from being chained to the KeyError
            raise e from None
    else:
        r = cmd(arg)
    Env.log_command_finished(r)

    _, _, p = THREAD_LOCAL.command
    THREAD_LOCAL.command = p

    RESULT_HISTORY.append(r)
    if r is not None:
        Env['_'] = r
    return r
