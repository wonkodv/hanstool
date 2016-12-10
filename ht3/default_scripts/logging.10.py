from Env import *

import pprint
import shlex
import itertools

@Env.updateable
def show(o):
    ALERT_HOOK(o)

@Env.updateable
def log(o):
    DEBUG_HOOK(o)


@SUBPROCESS_SPAWN_HOOK.register
def log_subprocess(p):
    if Env.get('DEBUG', False):
        print("Process spawned {}{}:{}".format(p.pid, ' shell' if p.shell else '', p.args))

@SUBPROCESS_FINISH_HOOK.register
def log_subprocess_finished(p):
    if p.returncode > 0 or Env.get('DEBUG', False):
        print("Process finished {} ({}):{}".format(p.pid, p.name, p.returncode))

@DEBUG_HOOK.register
def log_debug(o):
    if Env.get('DEBUG',0):
        log_alert(o)

@ALERT_HOOK.register
def log_alert(o):
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

    print(o)

@EXCEPTION_HOOK.register
@COMMAND_EXCEPTION_HOOK.register
def last_exception_h(exception, **kwargs):
    t = type(exception)
    tb = exception.__traceback__
    for s in traceback.format_exception(t, exception, tb):
        print(s, end='')


@COMMAND_RESULT_HOOK.register
def log_command_finished(result,**kwa):
    if result is None:
        if not Env.get('DEBUG', False):
            return
    print("Result: {0}".format(result))
