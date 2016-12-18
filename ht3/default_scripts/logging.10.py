from Env import *

import pprint
import shlex
import itertools
import textwrap


def _print(s, **kwargs):
    try:
        print(s, **kwargs)
    except UnicodeError:
        print(s.encode("ASCII","backslashreplace").decode("ASCII"), **kwargs) # This happens on windows sometimes

@Env.updateable
def show(o):
    ALERT_HOOK(message=o)

@Env.updateable
def log(o):
    DEBUG_HOOK(message=o)


@SUBPROCESS_SPAWN_HOOK.register
def log_subprocess(process):
    if Env.get('DEBUG', False):
        _print("Process spawned {}{}:{}".format(process.pid, ' shell' if process.shell else '', process.args))

@SUBPROCESS_FINISH_HOOK.register
def log_subprocess_finished(process):
    if process.returncode > 0 or Env.get('DEBUG', False):
        _print("Process finished {} ({}):{}".format(process.pid, process.name, process.returncode))

@DEBUG_HOOK.register
def log_debug(message):
    if Env.get('DEBUG',0):
        log_alert(message)

@ALERT_HOOK.register
def log_alert(message):
    o = message
    if isinstance(o, str):
        pass
    elif isinstance(o, bool):
        o = str(o)
    elif isinstance(o, int):
        o = "0b{0:b}\t0x{0:X}\t{0:d}".format(o)
    elif inspect.isfunction(o):
        s, l = inspect.getsourcelines(o)
        o = "".join("{0:>6d} {1}".format(n,s) for (n,s) in zip(itertools.count(l),s))
    else:
        o = pprint.pformat(o)

    _print(o)

@EXCEPTION_HOOK.register
@COMMAND_EXCEPTION_HOOK.register
def last_exception_h(exception, command=None):
    if isinstance(exception, ProcIOException):
        _print(
            (   "Returncode: {}\n"
                "stdout:\n"
                "{}\n"
                "stderr:\n"
                "{}\n"
            ).format(
                exception.returncode,
                textwrap.indent(exception.out.rstrip(),'> ', lambda s:True),
                textwrap.indent(exception.err.rstrip(),'> ', lambda s:True),
            )
        )
    else:
        t = type(exception)
        tb = exception.__traceback__
        for s in traceback.format_exception(t, exception, tb):
            _print(s, end='')


@COMMAND_RESULT_HOOK.register
def log_command_finished(result, command):
    if result is None:
        if not Env.get('DEBUG', False):
            return
    _print("Result: {0}".format(result))
