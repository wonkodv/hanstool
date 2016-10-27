import pathlib
import os.path
import collections
import ht3.hook
from ht3.env import Env


HISTORY_FILE_DEFAULT = '~/.config/ht3/history'

APPEND_HOOK = ht3.hook.Hook()


def get_history_file():
    p = Env.get('HISTORY', HISTORY_FILE_DEFAULT)
    p = str(p) # in case it's a Path
    p = os.path.expanduser(p)
    p = pathlib.Path(p)
    global get_history_file
    get_history_file = lambda:p
    return p

def get_history():
    try:
        with get_history_file().open("rt") as f:
            for l in f:
                yield l.strip()
    except FileNotFoundError:
        pass

def append_history(*cmd):
    for c in cmd:
        APPEND_HOOK(c)
    limit = Env.get('HISTORY_LIMIT',1000)
    if limit is not None:
        try:
            with get_history_file().open("rt") as f:
                q = collections.deque((l.strip() for l in f), limit)
        except FileNotFoundError:
            q = []
        q.extend(cmd)
        with get_history_file().open("wt") as f:
            for l in q:
                f.write(l + "\n")
    else:
        with get_history_file().open("at") as f:
            f.write("\n".join(cmd) + "\n")



