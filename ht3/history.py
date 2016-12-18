import pathlib
import os.path
import collections
import ht3.hook
from ht3.env import Env


HISTORY_FILE_DEFAULT = '~/.config/ht3/history'

APPEND_HOOK = ht3.hook.Hook("command_string")

HISTORY = None

def get_history_file():
    p = Env.get('HISTORY', HISTORY_FILE_DEFAULT)
    p = str(p) # in case it's a Path
    p = os.path.expanduser(p)
    p = pathlib.Path(p)
    global get_history_file
    get_history_file = lambda:p
    return p

def get_history():
    global HISTORY
    if HISTORY is None:
        try:
            load_history()
        except FileNotFoundError:
            HISTORY = []
    return HISTORY


def load_history():
    """Load the history from file, enforce Limit."""
    global HISTORY
    limit = Env.get('HISTORY_LIMIT',1000)
    with get_history_file().open("rt") as f:
        if limit is not None:
            HISTORY = list(collections.deque((l.strip() for l in f), limit))
        else:
            h = [l.strip() for l in f]
    if limit is not None:
        with get_history_file().open("wt") as f:
            for l in HISTORY:
                f.write(l + "\n")

def append_history(*cmd):
    get_history().extend(cmd)
    for c in cmd:
        APPEND_HOOK(command_string=c)
    with get_history_file().open("at") as f:
        f.write("\n".join(cmd) + "\n")



