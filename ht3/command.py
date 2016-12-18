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
COMMAND_RESULT_HOOK = ht3.hook.Hook("command", "result")
COMMAND_EXCEPTION_HOOK = ht3.hook.Hook("exception", "command")
COMMAND_NOT_FOUND_HOOK = ht3.hook.ResultHook("command_string")

_DEFAULT = object()
_COMMAND_RUN_ID = 0

class NoCommandError(Exception):
    pass

class Command():
    """Base class of commands.

    each Command will be a derived class. Objects of that class contain
    args, invocation string, result, possibly the thread.
    """
    def __init__(self, invocation):
        self.invocation = invocation
        self.target = type(self).target # TODO this is ugly

    def __call__(self):
        self._setup()
        try:
            if self.threaded:
                result = self.thread = start_thread(self._run())
            else:
                result = self._run()
        except Exception as e:
            self._exception(e)
        else:
            self._result(result)
            return result

    def _run(self):
        self.result = self.target(*self.args, **self.kwargs)
        return self.result

    def _setup(self):
        global _COMMAND_RUN_ID
        _COMMAND_RUN_ID += 1

        self.id = _COMMAND_RUN_ID
        self.parent = THREAD_LOCAL.command
        THREAD_LOCAL.command = self
        COMMAND_RUN_HOOK(command=self)

    def _exception(self, e):
        COMMAND_EXCEPTION_HOOK(command=self, exception=e)
        THREAD_LOCAL.command = self.parent

    def _result(self, r):
        COMMAND_RESULT_HOOK(command=self, result=r)
        THREAD_LOCAL.command = self.parent

    def __repr__(self):
        name = type(self).__name__
        return "Command(name={1} id={0.id} invocation={0.invocation})".format(self, name)

    def __str__(self):
        name = type(self).__name__
        if self.invocation.startswith(name):
            return "{0.id}: {0.invocation}".format(self)
        else:
            return "{0.id}: {0.invocation} {1}".format(self, name)


class CommandWithArgs(Command):
    """Arguments with name and an argument string."""

    def __init__(self, invocation, arg_string):
        super().__init__(invocation)
        self.arg_string = arg_string
        self.args, self.kwargs = self.parse(arg_string)

    def complete(self, s):
        return self.arg_parser.complete(s)

    def parse(self, s):
        return self.arg_parser.convert(s)

def register_command(func, *,
                origin_stacked, name=_DEFAULT,
                threaded=False, args='auto',
                apply_default_param_anotations=False,
                doc=_DEFAULT, attrs=_DEFAULT):
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

    long_doc = "".join(["Command '%s'" % name, "\n",
        ("Calls %s\n" % func_name ) if func_name != name else "",
        arg_parser.describe_params(), "\n",
        "Executed in a seperate Thread\n" if threaded else "",
        "\n",
        doc + "\n" if doc else '',
        "\n",
        "Defined in:\n\t%s:%d" % origin
    ])

    d = dict(
        target=func,
        origin=origin,
        arg_parser=arg_parser,
        __doc__=long_doc,
        threaded=threaded,
        attrs=attrs)
    cmd = type(name, (CommandWithArgs,), d)

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

def get_command(string):
    cmd, sep, args = parse_command(string)
    try:
        return COMMANDS[cmd](string, args)
    except KeyError:
        raise NoCommandError(cmd, sep, args) from None

def run_command(string):
    if THREAD_LOCAL.command is None:
        ht3.history.append_history(string)
    try:
        cmd = get_command(string)
    except NoCommandError:
        try:
            cmd = COMMAND_NOT_FOUND_HOOK(command_string=string)
        except ht3.hook.NoResult:
            raise NoCommandError(string) from None

    assert isinstance(cmd, Command)

    return cmd()
