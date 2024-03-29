import collections
import pathlib

import ht3.hook
from ht3.env import Env

HISTORY_FILE_DEFAULT = "~/.config/ht3/history"

APPEND_HOOK = ht3.hook.Hook("command_string")

HISTORY = None


def get_history_file():
    p = Env.get("HISTORY", HISTORY_FILE_DEFAULT)
    p = pathlib.Path(p).expanduser()
    if not p.parent.exists():
        p.parent.mkdir(parents=True)
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
    limit = Env.get("HISTORY_LIMIT", 1000)
    with get_history_file().open("rt") as f:
        f = (l for l in f if '\0' not in l)
        if limit is not None:
            HISTORY = [line.strip() for line in collections.deque(f, limit)]
        else:
            HISTORY = [line.strip() for line in f]
    if limit is not None:
        with get_history_file().open("wt") as f:
            for line in HISTORY:
                f.write(line + "\n")


def append_history(*cmd):
    get_history().extend(cmd)
    for c in cmd:
        APPEND_HOOK(command_string=c)
    with get_history_file().open("at") as f:
        f.write("\n".join(cmd) + "\n")
