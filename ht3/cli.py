"""The Command Line Frontend. Like a shell."""
import traceback
import os
import atexit
import os.path
import threading

from .env import Env
from .command import run_command
from .complete import complete_all

try:
    import readline
except ImportError:
    readline = None

_evt = threading.Event()

def start():
    _evt.clear()

def loop():
    _setup_readline()
    for c in _do_on_start:
        c()
    while not _evt.is_set():
        try:
            prompt = Env.CLI_PROMPT
            if callable(prompt):
                prompt = prompt()
            s = input(prompt) #TODO: let this be interrupted from stop.
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            print()
            return
        if s:
            try:
                result = run_command(s)
            except KeyboardInterrupt:
                print("\n!!Aborted")
            except SystemExit:
                print("\nQuitting")
                raise
            except Exception:
                traceback.print_exc()

def stop():
    _evt.set()


def _setup_readline():
    if not readline:
        return False

    history = Env.get('RL_HISTORY', "~/.config/ht3/rlhistory")
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
        if n == 0:
            try:
                # rl consumes entire list, so no lazy evaluation possible
                completion_cache.clear()
                completion_cache.extend(complete_all(text))
            except Exception as e:
                Env.log_error(e) # readline ignores all exceptions
        return completion_cache[n]
    readline.set_completer(rl_complete)
    readline.set_completer_delims('') # complete with the whole line
    readline.parse_and_bind('tab: complete')


# Basic API

Env['help'] = help

# Extended API

Env['CLI_PROMPT'] = "ht3> "

_do_on_start=[]
def cli_do_on_start(f):
    _do_on_start.append(f)

