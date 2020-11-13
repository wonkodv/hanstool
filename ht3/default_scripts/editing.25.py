import os
import shutil
import shlex

from Env import *

if "EDITOR" in os.environ:
    e = shlex.split(os.environ["EDITOR"])
elif CHECK.os.win:
    editors = [
        "gvim",
        r"C:\Program Files (x86)\Notepad++\notepad++.exe",
        r"C:\Program Files\Notepad++\notepad++.exe",
        "notepad",
    ]

    for e in editors:
        if os.path.exists(e) or shutil.which(e):
            e = [e]
            break
    else:
        e = ["notepad.exe"]
else:
    if CHECK.frontend("ht3.cli"):
        editors = ["nvim", "vim", "nano", "emacs"]
    else:
        editors = ["nvim-qt", "gvim", "gedit"]
    for s in editors:
        s = shutil.which(s)
        if s:
            e = [s]
            break
    else:
        e = ["ed"]  # haha

Env["EDITOR"] = tuple(e)  # make unmodifiable


@Env.updateable
@args.enforce_args
@cmd
def edit_file(file_name: Path, line: int = 0):
    """Edit a file using EDITOR."""
    e = " ".join(Env.EDITOR).lower()

    args = list(Env.EDITOR)
    args.append(str(file_name))
    if line:
        if "vim" in e:
            args.append("+%d" % line)
        elif "notepad++" in e:
            args.append("-n%d" % line)
    p = execute_auto(*args)
