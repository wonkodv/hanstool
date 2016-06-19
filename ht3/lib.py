"""Module for loading frontends, scripts and miscelaneous functions"""

import sys
import importlib
import threading

from .env import Env
from . import check

FRONTENDS = []
FRONTEND_MODULES = []

THREAD_LOCAL = threading.local()
THREAD_LOCAL.command = None
THREAD_LOCAL.frontend = None


check.CHECK.frontend = check.Group(FRONTENDS)
check.CHECK.current_frontend = check.Value(lambda:THREAD_LOCAL.frontend)


def load_frontend(name):
    """Load a the frontend with wualified name: ``name``"""
    mod = importlib.import_module(name)
    assert callable(mod.start)
    assert callable(mod.loop)
    assert callable(mod.stop)
    FRONTEND_MODULES.append(mod)
    FRONTENDS.append(name)


def run_frontends():
    """
    Start all loaded frontends.

    Execute the ``loop`` function of every loaded Frontend in a seperate thread.
    If any frontend returns from its ``loop``,``stop()`` of all
    frontends is called (from the main thread so stop must be threadsafe) after all threads finished
    (the ``loop`` functions return), this function returns.
    """
    frontends = tuple(FRONTEND_MODULES) # avoid concurrency if modules load modules

    if not frontends:
        raise ValueError("No Frontend Loaded yet")

    if len(frontends) == 1:     # Shortcut if there is no need for threading stuff
        fe = frontends[0]
        THREAD_LOCAL.frontend = fe.__name__
        fe.start()
        try:
            fe.loop()
        except Exception as e:
            Env.error_hook(e)
        try:
            fe.stop()
        except Exception as e:
            Env.error_hook(e)
        THREAD_LOCAL.frontend = None
    else:
        threads = []
        evt = threading.Event()

        for fe in frontends:
            fe.start()
        def _run_fe(fe):
            THREAD_LOCAL.frontend = fe.__name__
            THREAD_LOCAL.command = None
            try:
                fe.loop()
            except Exception as e:
                Env.error_hook(e)
            finally:
                evt.set()
        for fe in frontends:
            t = threading.Thread(target=_run_fe, args=[fe], name=fe.__name__)
            t.start()
            threads.append((t, fe))

        try:
            evt.wait() # wait till some Frontend's loop() method returns
        finally:
            # stop all frontends
            for t, f in threads:
                try:
                    f.stop()
                except Exception as e:
                    Env.error_hook(e)

            # wait for all frontends to finish.
            for t, f in threads:
                t.join()

def execute_py_expression(s):
    """Execute a python expression"""
    c = compile(s, "<input>", "exec")
    return eval(c, Env.dict)


def evaluate_py_expression(s):
    """Evaluate a python expression"""
    c = compile(s, "<input>", "eval")
    r = eval(c, Env.dict)
    return r


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
        on_finish = Env.log_thread_finished
    if on_exception is None:
        on_exception = Env.error_hook
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
        except Exception as e:
            on_exception(e)
    t = threading.Thread(target=target, name=name)
    t.start()
    return t
