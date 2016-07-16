import pprint


def show(o):
    ALERT_HOOK(o)

def log(o):
    DEBUG_HOOK(o)


@SUBPROCESS_SPAWN_HOOK.register
def _log_subprocess(p):
    if Env.get('DEBUG', False):
        print("spawned process: %d, %r" % (p.pid, p.args))

@SUBPROCESS_FINISH_HOOK.register
def _log_subprocess_finished(p):
    if p.returncode > 0 or Env.get('DEBUG', False):
        print("process finished: %d with %d" % (p.pid, p.returncode))

@DEBUG_HOOK.register
def _log_debug(o):
    if Env.get('DEBUG',0):
        _log_alert(o)

@ALERT_HOOK.register
def _log_debug(o):
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
def _last_exception_h(exception, **kwargs):
    t = type(exception)
    tb = exception.__traceback__
    for s in traceback.format_exception(t, exception, tb):
        print(s, end='')


@COMMAND_RESULT_HOOK.register
def _log_command_finished(result,**kwa):
    if result is None:
        if not Env.get('DEBUG', False):
            return
    print("Result: {0}".format(result))
