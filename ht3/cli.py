import sys
import traceback
import os
import atexit
import configparser
import os.path
import logging
import threading

from . import lib
from .lib import Env

try:
    import readline
except:
    readline = None

_evt = threading.Event()

def loop():
    setup_readline()
    _evt.clear()
    for c in _do_on_start:
        c()
    while not _evt.is_set():
        try:
            prompt = Env.CLI_PROMPT
            if callable(prompt):
                prompt = prompt()
            s = input(prompt)
        except KeyboardInterrupt:
            continue
        except EOFError:
            return
        if s:
            try:
                result = lib.run_command(s)
            except KeyboardInterrupt:
                print("\n!!Aborted")
            except SystemExit:
                print("\nQuitting")
                raise
            except:
                traceback.print_exc()
            else:
                if result is not None:
                    Env._ = result
                    print(result)

def stop():
    _evt.set()


def setup_readline():
    if not readline:
        return False

    history = Env.get('RL_HISTORY', None)
    if history:
        history = os.path.expanduser(history)
        try:
            readline.read_history_file(history)
        except FileNotFoundError:
            open(history, 'wb').close()
        hlen = readline.get_history_length()

        def save():
            newhlen = readline.get_current_history_length()
            l = newhlen - hlen
            if hasattr(readline, 'append_history_file'):
                readline.append_history_file(l, history)
            else:
                readline.write_history_file(history)
        atexit.register(save)

    completion_cache=[]

    def rl_complete(text, n):
        nonlocal completion_cache
        if n == 0:
            try:
                completion_cache = list(lib.get_all_completions(text))
            except:
                traceback.print_exc()
            #print("\nCompletion of %s, cache: %s\n--> %s" % (text, completion_cache, text),end='')
        return completion_cache[n]
    readline.set_completer(rl_complete)
    readline.set_completer_delims('')
    readline.parse_and_bind('tab: complete')


# Basic API

@Env
def show(s, *args, **kwargs):
    print (str(s) % args)

@Env
def log(s, *args, **kwargs):
    print (str(s) % args)

Env['help'] = help

# Extended API

Env['CLI_PROMPT'] = "ht3> "

_do_on_start=[]
def cli_do_on_start(f):
    _do_on_start.append(f)

