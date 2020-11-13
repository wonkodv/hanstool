"""Module for loading frontends and miscelaneous functions"""

import sys
import importlib
import threading

import ht3.hook
import inspect

from .env import Env
from . import check


EXCEPTION_HOOK = ht3.hook.Hook("exception")
DEBUG_HOOK = ht3.hook.Hook("message")
ALERT_HOOK = ht3.hook.Hook("message")


@EXCEPTION_HOOK.register
def _exception_hook_fallback(exception):
    """ If no other handlers are installed, raise Exc. """
    if len(EXCEPTION_HOOK.callbacks) == 1:
        raise exception


@ALERT_HOOK.register
def _alert_hook_fallback(message):
    """ If no other handlers are installed, print. """
    if len(EXCEPTION_HOOK.callbacks) == 1:
        print(message)


FRONTENDS = []
FRONTEND_MODULES = []
_RUNNING_FRONTENDS = None
_Stop_FrontEnds_Sem = None

THREAD_LOCAL = threading.local()
THREAD_LOCAL.command = None
THREAD_LOCAL.frontend = "ht3.main"


check.CHECK.frontend = check.Group(FRONTENDS)
check.CHECK.current_frontend = check.Value(lambda: THREAD_LOCAL.frontend)
check.CHECK.frontends_running = False


def _is_cli_frontend():
    fe = THREAD_LOCAL.frontend
    if fe is None:
        return False
    m = importlib.import_module(fe)
    return getattr(m, "_IS_CLI_FRONTEND", None)


check.CHECK.is_cli_frontend = check.Value(_is_cli_frontend)


def load_frontend(name):
    """Load a the frontend with qualified name: ``name``"""

    if name in FRONTENDS:
        raise TypeError("Frontend already loaded", name)

    mod = importlib.import_module(name)

    for m in "start", "loop", "stop":
        if not callable(getattr(mod, m)):
            raise TypeError(
                "Frontend is missing a function",
                m,
                name,
                mod,
            )

    FRONTEND_MODULES.append(mod)
    FRONTENDS.append(name)


def run_frontends():
    """Run all Frontends.

    Execute the `loop` function of every loaded Frontend in a seperate thread.
    The first Frontend is run in MainThread (allows e.g. KeyboardInterrupt for CLIs,
    tkinter also likes mainthread, ...)

    The first frontend which returns from its `loop()`, calls `stop()` on all
    frontends, so stop must be threadsafe. After All frontends returned from their
    `loop()`, this function returns.
    """

    # avoid concurrency if modules load modules
    frontends = tuple(FRONTEND_MODULES)

    if not frontends:
        raise ValueError("No Frontend Loaded yet")

    threads = []

    for fe in frontends:
        fe.start()

    global _RUNNING_FRONTENDS, _Stop_FrontEnds_Sem
    _RUNNING_FRONTENDS = frontends
    _Stop_FrontEnds_Sem = threading.Semaphore(1)
    check.CHECK.frontends_running = True

    def _run_fe(fe):
        name = fe.__name__
        THREAD_LOCAL.frontend = name
        THREAD_LOCAL.command = None
        thread = threading.current_thread()
        old_thread_name = thread.name
        if thread is threading.main_thread():
            thread.name = "MainThread({})".format(name)
        else:
            thread.name = "FrontendThread({})".format(name)

        try:
            fe.loop()
        except Exception as e:
            EXCEPTION_HOOK(exception=e)
        finally:
            stop_frontends()
            thread.name = old_thread_name

    for fe in frontends[1:]:
        t = threading.Thread(target=_run_fe, args=[fe], name=fe.__name__)
        t.start()
        threads.append(t)

    _run_fe(frontends[0])
    check.CHECK.frontends_running = False

    for t in threads:
        t.join()

    _Stop_FrontEnds_Sem = None
    _RUNNING_FRONTENDS = None


def stop_frontends():
    if _Stop_FrontEnds_Sem.acquire(False):  # the first to return stops all
        for f in _RUNNING_FRONTENDS:
            try:
                f.stop()
            except Exception as e:
                EXCEPTION_HOOK(exception=e)


def execute_py_expression(s):
    """Execute a python expression"""
    c = compile(s, "<input>", "exec")
    return exec(c, {}, Env.dict)


def evaluate_py_expression(s):
    """Evaluate a python expression"""
    c = compile(s, "<input>", "eval")
    r = eval(c, {}, Env.dict)
    return r


def threaded(f=None, **kwargs):
    if f is None:

        def deco(f):
            start_thread(f, **kwargs)
            return f

        return deco
    start_thread(f, **kwargs)
    return f


def start_thread(
    func, args=None, kwargs=None, name=None, on_exception=None, on_finish=None
):
    """
    Start a thread that is HT3 aware

    Copys the thread local information active frontend and active command and
    then executes `func`.  Calls `on_finished` with the function result or/and
    on_exception on error.
    """
    if name is None:
        name = func.__name__
    if on_finish is None:
        on_finish = lambda *a: None  # Env.log_thread_finished #TODO
    if on_exception is None:
        del on_exception

        def on_exception(e):
            return EXCEPTION_HOOK(exception=e)

    if args is None:
        args = tuple()
    if kwargs is None:
        kwargs = dict()
    fe = THREAD_LOCAL.frontend
    cmd = THREAD_LOCAL.command

    stack = inspect.stack(0)

    def target(stack):
        __STACK_FRAMES__ = stack
        THREAD_LOCAL.frontend = fe
        THREAD_LOCAL.command = cmd
        try:
            r = func(*args, **kwargs)
            on_finish(r)
        except SystemExit:
            stop_frontends()
        except Exception as e:
            on_exception(e)
        # Let go of stack if there were no exceptions
        del stack

    t = threading.Thread(target=target, name=name, args=(stack,))
    t.start()
    del stack
    return t
