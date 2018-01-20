"""Register commands."""
import functools
import inspect
import traceback

from .lib import THREAD_LOCAL, start_thread
import ht3.args
import ht3.history
import ht3.hook

COMMANDS = {}

COMMAND_RUN_HOOK = ht3.hook.Hook("command")
COMMAND_FINISHED_HOOK = ht3.hook.Hook("command")
COMMAND_EXCEPTION_HOOK = ht3.hook.Hook("exception", "command")
COMMAND_NOT_FOUND_HOOK = ht3.hook.ResultHook("command_string")

_DEFAULT = object()

class NoCommandError(Exception):
    pass

class Command():
    """Base class of commands.

    each Command will be a derived class. Objects of that class contain
    args and the invocation string
    """

    # Must be overwritten by subclasses
    run = None
    attrs = False
    origin = False

    # Must be overwritten by instances
    started = False
    finished = False
    parent = None

    def __init__(self, invocation):
        self.invocation = invocation
        self.name = type(self).__name__

    def __call__(self):
        assert not self.started
        self.started = True

        self.parent = THREAD_LOCAL.command
        self.frontend = THREAD_LOCAL.frontend
        try:
            THREAD_LOCAL.command = self
            COMMAND_RUN_HOOK(command=self)
            try:
                result = self.result = self.run()
            except Exception as e:
                if self.parent is None:
                    if COMMAND_EXCEPTION_HOOK(command=self, exception=e):
                        return
                raise
            else:
                COMMAND_FINISHED_HOOK(command=self)
                return result
            finally:
                self.finished = True
        finally:
            THREAD_LOCAL.command = self.parent

    def __repr__(self):
        if not self.started:
            state = "New"
        elif not self.finished:
            state = "Running"
        else:
            state = "Finished"
        return "Command(name={0.name}, invocation={0.invocation}, state={1})".format(self, state)

    def __str__(self):
        if self.invocation.startswith(self.name):
            return self.invocation
        return self.invocation + " => " + self.name

class NamedFunctionCommand(Command):
    """Command that has a Function, Name and gets an argument string."""

    target = None # to be overwritten by subclasses

    def __init__(self, invocation, arg_string):
        super().__init__(invocation)
        self.arg_string = arg_string
        self.args, self.kwargs = self.parse(arg_string)

    def run(self):
        t = type(self).target   # do not bind the target function to self
        r = t(*self.args, **self.kwargs)
        return r

    def complete(self, s):
        return self.arg_parser.complete(s)

    def parse(self, s):
        return self.arg_parser.convert(s)

def register_command(func, *,
                origin_stacked,
                name=_DEFAULT,
                args='auto',
                apply_default_param_anotations=False,
                doc=_DEFAULT,
                attrs=_DEFAULT):
    """ Register a function as Command """

    origin = traceback.extract_stack()
    origin = origin[-origin_stacked]
    origin = origin[0:2]


    arg_parser = ht3.args.ArgParser(func, args, apply_default_param_anotations)

    if attrs is _DEFAULT:
        attrs = {}

    if isinstance(func, functools.partial):
        func_name = func.func.__name__
    else:
        func_name = func.__name__
    if name is _DEFAULT:
        name = func_name

    if doc is _DEFAULT:
        doc = inspect.getdoc(func) or ''

    long_doc = "".join([
        doc,
        "\n",
        "\n",
        "Invoked as '%s'" % name,
        (", calls %s\n" % func_name ) if func_name != name else "",
        "\n",
        arg_parser.describe_params(), "\n",
        "Defined in:\n\t%s:%d" % origin
    ])

    d = dict(
        target=func,
        origin=origin,
        arg_parser=arg_parser,
        __doc__=long_doc,
        short_doc=doc,
        attrs=attrs)
    cmd = type(name, (NamedFunctionCommand,), d)

    COMMANDS[name] = cmd

    func.command = cmd

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

def get_registered_command(string):
    cmd, sep, args = parse_command(string)
    if cmd in COMMANDS:
        return COMMANDS[cmd](string, args)
    raise NoCommandError(cmd, sep, args) from None

def get_command(string):
    if THREAD_LOCAL.command is None:
        ht3.history.append_history(string)
    try:
        cmd = get_registered_command(string)
    except NoCommandError:
        try:
            cmd = COMMAND_NOT_FOUND_HOOK(command_string=string)
        except ht3.hook.NoResult:
            raise NoCommandError(string) from None

    assert isinstance(cmd, Command), "{} should be a Command".format(cmd)

    return cmd

def run_command(string):
    return get_command(string)()
