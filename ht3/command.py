"""Register commands."""
import functools
import inspect
import traceback

import ht3.args
from . import env
from .lib import THREAD_LOCAL, start_thread

COMMANDS = {}
_DEFAULT = object()

_COMMAND_RUN_ID = 0

def register_command(func, *, origin_stacked, args='auto', name=_DEFAULT,
                     func_name=_DEFAULT,
                     async=False, complete=_DEFAULT,
                     doc=_DEFAULT, **attrs):
    """ Register a function as Command """

    origin = traceback.extract_stack()
    origin = origin[-origin_stacked]
    origin = origin[0:2]

    @functools.wraps(func)
    def Command(arg_string=""):
        """ The function that will be executed """
        nonlocal arg_parser, func
        args, kwargs = arg_parser(arg_string)
        if async:
            t = start_thread(func, args=args, kwargs=kwargs)
            return t
        r = func(*args, **kwargs)
        return r

    arg_parser = ht3.args.Args(args, _command=Command, **attrs)

    if func_name is _DEFAULT:
        func_name = func.__name__

    if name is _DEFAULT:
        name = func_name

    if complete is _DEFAULT:
        complete = arg_parser.complete

    if doc is _DEFAULT:
        doc = inspect.getdoc(func) or ''

    long_doc = "".join(["Command '%s'" % name, "\n",
        ("Calls %s\n" % func_name ) if func_name != name else "",
        inspect.getdoc(arg_parser), "\n",
        "Executed in a seperate Thread\n" if async else "",
        "\n",
        doc, "\n",
        "\n",
        "Defined in:\n\t%s:%d" % origin
    ])

    Command.__doc__ = long_doc
    Command.doc = doc
    Command.__name__ = func_name
    Command.name = name
    Command.async = async
    Command.origin = origin
    Command.complete = complete
    Command.attrs = attrs
    Command.arg_parser = arg_parser

    COMMANDS[name] = Command

def cmd(func=None, **kwargs):
    """ use as decorator with or without arguments to register a function
        as a command. The function will be registered in its original form
        in the module and in arg parsing form in COMMANDS """

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
    i=0
    for c in string:
        if c in [' ','\t']:
            cmd = string[:i]
            sep = string[i]
            arg = string[i+1:]
            break
        i += 1
    else:
        cmd = string
        sep = ""
        arg = ""

    return cmd, sep, arg

def run_command_func(c, *args, **kwargs):
    global _COMMAND_RUN_ID
    _COMMAND_RUN_ID += 1

    parent = THREAD_LOCAL.command
    THREAD_LOCAL.command = [_COMMAND_RUN_ID, c.name, parent]

    env.Env.log_command(c.name)
    r = c(*args, **kwargs);
    env.Env.log_command_finished(r)

    _, _, p = THREAD_LOCAL.command
    THREAD_LOCAL.command = p

    env.Env.__.append(r)
    if r is not None:
        env.Env._ = r
    return r

def run_command(string):
    global _COMMAND_RUN_ID
    _COMMAND_RUN_ID += 1

    parent = THREAD_LOCAL.command
    THREAD_LOCAL.command = [_COMMAND_RUN_ID, string, parent]

    cmd, _, arg = parse_command(string)
    env.Env.log_command(string)
    try:
        c = COMMANDS[cmd]
    except KeyError:
        try:
            r = env.Env.command_not_found_hook(string)
        except Exception as e:
            # prevent this exception from being chained to the KeyError
            raise e from None
    else:
        r = c(arg)
    env.Env.log_command_finished(r)

    _, _, p = THREAD_LOCAL.command
    THREAD_LOCAL.command = p

    env.Env.__.append(r)
    if r is not None:
        env.Env._ = r
    return r
