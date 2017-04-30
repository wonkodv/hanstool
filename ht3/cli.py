"""The Command Line Frontend. Like a shell."""
import traceback
import os
import os.path
import threading

from .env import Env
from .command import get_command
from .complete import complete_command_with_args

import ht3.lib
import ht3.history

try:
    import readline
except ImportError:
    readline = None

#TODO: resgister with ht3.history.APPEND_HOOK to add to history if not self

_IS_CLI_FRONTEND = True

_evt = threading.Event()

def start():
    _evt.clear()

def loop():
    _setup_readline()
    for c in _do_on_start:
        c()
    while not _evt.is_set():
        try:
            prompt = Env.get('CLI_PROMPT', 'ht3> ')
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
                cmd = get_command(s)
                cmd()
            except KeyboardInterrupt:
                print("\n!!Aborted")
            except SystemExit:
                print("\nQuitting")
                raise
            except Exception as e:
                ht3.lib.EXCEPTION_HOOK(exception=e)

def stop():
    _evt.set()

def _setup_readline():
    if not readline:
        return False

    for l in ht3.history.get_history():
        readline.add_history(l)

    completion_cache=[]

    def rl_complete(text, n):
        if n == 0:
            try:
                # rl consumes entire list, so no lazy evaluation possible
                completion_cache.clear()
                completion_cache.extend(complete_command_with_args(text))
            except Exception as e:
                ht3.lib.EXCEPTION_HOOK(exception=e) # readline ignores all exceptions
        return completion_cache[n]
    readline.set_completer(rl_complete)
    readline.set_completer_delims('') # complete with the whole line
    readline.parse_and_bind('tab: complete')

_do_on_start=[]
def do_on_start(f):
    _do_on_start.append(f)
