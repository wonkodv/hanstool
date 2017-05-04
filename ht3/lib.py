"""Module for loading frontends and miscelaneous functions"""

import sys
import importlib
import threading

import ht3.hook

from .env import Env
from . import check


EXCEPTION_HOOK = ht3.hook.Hook("exception")
DEBUG_HOOK = ht3.hook.Hook("message")
ALERT_HOOK = ht3.hook.Hook("message")


FRONTENDS = []
FRONTEND_MODULES = []

THREAD_LOCAL = threading.local()
THREAD_LOCAL.command = None
THREAD_LOCAL.frontend = 'ht3.main'


check.CHECK.frontend = check.Group(FRONTENDS)
check.CHECK.current_frontend = check.Value(lambda:THREAD_LOCAL.frontend)
check.CHECK.frontends_running = False

def _is_cli_frontend():
    fe = THREAD_LOCAL.frontend
    if fe is None:
        return False
    m = importlib.import_module(fe)
    return getattr(m,'_IS_CLI_FRONTEND', None)

check.CHECK.is_cli_frontend = check.Value(_is_cli_frontend)

def load_frontend(name):
    """Load a the frontend with qualified name: ``name``"""
    mod = importlib.import_module(name)
    assert callable(mod.start)
    assert callable(mod.loop)
    assert callable(mod.stop)
    FRONTEND_MODULES.append(mod)
    FRONTENDS.append(name)

_FrontendWaitEvt = threading.Event()

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
        _FrontendWaitEvt.set()
        thread.name = old_thread_name

def _wait_and_stop_frontends(frontends):
    check.CHECK.frontends_running = True

    try:
        _FrontendWaitEvt.wait() # wait till some Frontend's loop() method returns
    finally:
        # stop all frontends
        check.CHECK.frontends_running = False
        for f in frontends:
            try:
                f.stop()
            except Exception as e:
                EXCEPTION_HOOK(exception=e)

def _run_1_fe(fe):
    """Run a single FrontEnd in MainThread."""
    fe.start()

    # Use an extra thread that notices _FrontendWaitEvt and stops the fe.
    t = threading.Thread(
            target=_wait_and_stop_frontends,
            daemon=True,
            args=[[fe]],
            name="Wait and Stop FE")
    t.start()

    _run_fe(fe)

def _run_many_frontends(frontends):
    """Run Many Frontends.

    Execute the ``loop`` function of every loaded Frontend in a seperate thread.
    If any frontend returns from its ``loop()``,``stop()`` of all
    frontends is called (from a different thread so stop must be threadsafe) afters
    all threads ``loop()`` functions finished.

    The first Frontend is run in MainThread (allows e.g. KeyboardInterrupt for CLIs,
    tkinter also likes mainthread, ...)

    """

    threads = []

    _FrontendWaitEvt.clear()

    for fe in frontends:
        fe.start()

    for fe in frontends[1:]:
        t = threading.Thread(target=_run_fe, args=[fe], name=fe.__name__)
        t.start()
        threads.append(t)

    t = threading.Thread(
            target=_wait_and_stop_frontends,
            daemon=True,
            args=[frontends],
            name="Wait and Stop FEs")
    t.start()

    _run_fe(frontends[0])

    # wait for all other frontends to finish.
    for t in threads:
        t.join()

def run_frontends():
    """
    Start all loaded frontends.

    """
    frontends = tuple(FRONTEND_MODULES) # avoid concurrency if modules load modules

    l = len(frontends)
    if l == 0:
        raise ValueError("No Frontend Loaded yet")

    if l == 1:
        _run_1_fe(frontends[0])
    else:
        _run_many_frontends(frontends)

def stop_frontends():
    _FrontendWaitEvt.set()

def execute_py_expression(s):
    """Execute a python expression"""
    c = compile(s, "<input>", "exec")
    return eval(c, Env.dict)


def evaluate_py_expression(s):
    """Evaluate a python expression"""
    c = compile(s, "<input>", "eval")
    r = eval(c, Env.dict)
    return r

def threaded(f=None,**kwargs):
    if f is None:
        def deco(f):
            start_thread(f,**kwargs)
            return f
        return deco
    start_thread(f,**kwargs)
    return f


def start_thread(func, args=None, kwargs=None, name=None, on_exception=None, on_finish=None):
    """
    Start a thread that is HT3 aware

    Copys the thread local information active frontend and active command and
    then executes `func`.  Calls `on_finished` with the function result or/and
    on_exception on error.
    """
    if name is None:
        name = func.__name__
    if on_finish is None:
        on_finish = lambda *a:None #Env.log_thread_finished #TODO
    if on_exception is None:
        on_exception = lambda e:EXCEPTION_HOOK(exception=e)
    if args is None:
        args=tuple()
    if kwargs is None:
        kwargs = dict()
    fe = THREAD_LOCAL.frontend
    cmd = THREAD_LOCAL.command
    def target():
        THREAD_LOCAL.frontend = fe
        THREAD_LOCAL.command = cmd
        try:
            r = func(*args, **kwargs)
            on_finish(r)
        except SystemExit:
            stop_frontends()
        except Exception as e:
            on_exception(e)
    t = threading.Thread(target=target, name=name)
    t.start()
    return t
