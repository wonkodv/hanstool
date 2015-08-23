import traceback
import functools
import re
import textwrap

from .args import Args

COMMANDS = {}

def cmd(func=None, *_,args=None, name=None, **attrs):
    """ use as decorator with or without arguments to register a function
        as a command. The function will be registered in its original form 
        in the module and in arg parsing form in COMMANDS """
    def decorator(func):
        """ the actual decorator """

        arg_parser = Args(args)

        @functools.wraps(func)
        def wrapper(arg_string):
            """ The function that will be executed invoked """
            return func(*arg_parser(arg_string))

        def complete(arg_string):
            raise NotImplemented("Completion for Arguments of type ", arg_parser, ar_stringg)


        if name is None:
            wrapper.name = func.__name__
        else:
            wrapper.name = name

        doc = textwrap.dedent(func.__doc__ or '')

        origin = [func.__code__.co_filename, func.__code__.co_firstlineno]
        fn, lno = origin

        doc = "Invoked as '%s'.\n%s\n\n%s\n\nDefined in:\n\t%s:%d" % (wrapper.name, arg_parser.__doc__.strip(), doc, fn, lno)

        wrapper.__doc__ = doc
        wrapper.origin = origin
        wrapper.complete = complete
        wrapper.attrs = attrs
        wrapper.arg_parser = arg_parser
        COMMANDS[wrapper.name] = wrapper

        return func
    if func is None:
        return decorator
    return decorator(func)
