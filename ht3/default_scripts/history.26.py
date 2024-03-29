from Env import *

import ht3.history


def strings_in(needles, haystack):
    try:
        x = 0
        for n in needles:
            x = haystack.index(n, x) + len(n)
    except ValueError:
        return False
    return True


@cmd
def history(*search):
    """Search for a command in the history file."""
    if not search:
        edit_file(ht3.history.get_history_file())
    else:
        for i, l in enumerate(ht3.history.get_history()):
            if strings_in(search, l):
                if not l.startswith("history"):
                    show("{0: 4d} {1}".format(i, l.strip()))


@cmd(name="!")
def rerun(x: args.Union(args.Int, args.Str)):
    """Redo a command from the history by its number or starting text."""
    if x == "!":
        x = -1
    history = list(ht3.history.get_history())[:-1]  # skip newest, thats the ! itself
    if isinstance(x, int):
        c = history[x]
    else:
        search = x.split()
        for c in reversed(history):
            if c.startswith(search[0]):
                if strings_in(search, c):
                    break
        else:
            raise KeyError("Nothing in history", x)

    log("Rerun: " + c)
    get_command(c)()
    ht3.history.append_history(c)
