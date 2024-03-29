import itertools
import pprint
import shlex
import textwrap

from Env import *


def _print(s, **kwargs):
    try:
        print(s, **kwargs)
    except UnicodeError:
        print(
            s.encode("ASCII", "backslashreplace").decode("ASCII"), **kwargs
        )  # This happens on windows sometimes


@Env.updateable
def show(o):
    ALERT_HOOK(message=o)


@Env.updateable
def log(o):
    DEBUG_HOOK(message=o)


@SUBPROCESS_SPAWN_HOOK.register
def log_subprocess(process):
    if Env.get("DEBUG", False):
        args = process.args
        if not isinstance(args, str):
            args = shellescape(*args)
        _print(
            "Process spawned {}{}:{}".format(
                process.pid, " shell" if process.shell else "", args
            )
        )


@SUBPROCESS_FINISH_HOOK.register
def log_subprocess_finished(process):
    if process.returncode > 0 or Env.get("DEBUG", False):
        _print(
            "Process finished {} ({}):{}".format(
                process.pid, process.name, process.returncode
            )
        )


@DEBUG_HOOK.register
def log_debug(message):
    if not CHECK.frontend("ht3.cli") or Env.get("DEBUG", 0):
        log_alert(message)


@ALERT_HOOK.register
def log_alert(message):
    o = message
    if isinstance(o, str):
        pass
    elif isinstance(o, bool):
        o = str(o)
    elif isinstance(o, int):
        o = "0b{0:_b}\t0x{0:_X}\t{0:_d}".format(o)
    elif inspect.isfunction(o):
        try:
            s, l = inspect.getsourcelines(o)
            o = "".join(
                "{0:>6d} {1}".format(n, s) for (n, s) in zip(itertools.count(l), s)
            )
        except OSError:
            o = repr(o)
    else:
        o = pprint.pformat(o)

    _print(o)


@EXCEPTION_HOOK.register
@COMMAND_EXCEPTION_HOOK.register
def last_exception_h(exception, command=None):
    if isinstance(exception, ProcIOException):
        _print(
            ("Returncode: {}\n" "stdout:\n" "{}\n" "stderr:\n" "{}\n").format(
                exception.returncode,
                textwrap.indent(exception.out.rstrip(), "> ", lambda s: True),
                textwrap.indent(exception.err.rstrip(), "> ", lambda s: True),
            )
        )
    else:
        t = type(exception)
        tb = exception.__traceback__
        for s in traceback.format_exception(t, exception, tb):
            _print(s, end="")


@COMMAND_FINISHED_HOOK.register
def log_command_finished(command):
    if not Env.get("DEBUG", False):
        return
    _print("Finished: {0}".format(command))
