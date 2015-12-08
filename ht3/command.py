import threading
import traceback
import functools
import inspect
import re
import textwrap
import threading


from .args import Args
from . import env

COMMANDS = {}
_DEFAULT = object()

def register_command(func, *, origin_stacked, args=None, name=_DEFAULT,
                     func_name=_DEFAULT,
                     async=False, complete=_DEFAULT,
                     doc=_DEFAULT, **attrs):
    """ Register a function as Command """
    origin = traceback.extract_stack()
    origin = origin[-origin_stacked]
    origin = origin[0:2]

    arg_parser = Args(args, **attrs)

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

    @functools.wraps(func)
    def Command(arg_string=""):
        """ The function that will be executed """
        args, kwargs = arg_parser(arg_string)
        if async:
            def CommandThread():
                try:
                    env.Env.log("Command Thread %s started", name)
                    r = func(*args, **kwargs)
                    env.Env.log("Command Thread %s Finished: %r", name, r)
                except Exception as e:
                    env.Env.handle_exception(e)
            t = threading.Thread(target=CommandThread, name=name)
            t.start()
            return t
        r = func(*args, **kwargs)
        return r

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

def run_command(string):
    cmd, sep, arg = parse_command(string)
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
    if r is not None:
        env.Env._ = r
        env.Env.__.append(r)
    return r
