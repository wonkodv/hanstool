import threading
import traceback
import functools
import re
import textwrap

from .args import Args

COMMANDS = {}

def cmd(func=None, *,args=None, name=None, async=False, complete=..., **attrs):
    """ use as decorator with or without arguments to register a function
        as a command. The function will be registered in its original form 
        in the module and in arg parsing form in COMMANDS """
    def decorator(func):
        """ the actual decorator """

        nonlocal args, name, async, complete, attrs

        if name is None:
            name = func.__name__

        arg_parser = Args(args, **attrs)

        @functools.wraps(func)
        def wrapper(arg_string=""):
            """ The function that will be executed """
            args, kwargs = arg_parser(arg_string)

            if async:
                t = threading.Thread(target=func, args=args,
                        kwargs=kwargs,
                        name="CommandThread :"+name)
                t.start()
                return t
            else:
                r = func(*args, **kwargs)
                return r
        if complete is ...:
            def complete(arg_string):
                return arg_parser.complete(arg_string)


        doc = textwrap.dedent(func.__doc__ or '')

        origin = [func.__code__.co_filename, func.__code__.co_firstlineno] # TODO: use calltrace of cmd()?
        fn, lno = origin

        doc = "".join(["Invoked as '%s'" % name, "\n",
            arg_parser.__doc__.strip(), "\n",
            "Executed in a seperate Thread\n" if async else "",
            "\n",
            "\n",
            doc, "\n",
            "\n",
            "Defined in:\n\t%s:%d" % (fn, lno)
        ])

        wrapper.__doc__ = doc
        wrapper.name = name
        wrapper.async = async
        wrapper.origin = origin
        wrapper.complete = complete
        wrapper.attrs = attrs
        wrapper.arg_parser = arg_parser
        COMMANDS[wrapper.name] = wrapper

        return func
    if func is None:
        return decorator
    return decorator(func)
