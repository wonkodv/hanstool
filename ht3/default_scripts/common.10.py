import os
import shutil
import shlex

from Env import *

if 'EDITOR' in os.environ:
    e = shlex.split(os.environ['EDITOR'])
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
        e = ['notepad.exe']
else:
    if CHECK.frontend('ht3.cli'):
        editors =['vim', 'nano', 'emacs']
    else:
        editors =['gvim', 'gedit']
    for s in editors:
        s = shutil.which(s)
        if s:
            e = [s]
            break
    else:
        e = ['ed'] # haha

EDITOR = Env['EDITOR'] = tuple(e) # make unmodifiable

@Env.updateable
@cmd
def edit_file(file_name:Path, line:int=0):
    """Edit a file using EDITOR."""
    f = str(file_name) # allow pathlib.Path
    l = int(line)
    e = Env.EDITOR[0].lower()

    args = list(EDITOR)
    args.append(f)
    if line:
        if 'vim' in e:
            args.append('+%d'%l )
        elif 'notepad++' in e:
            args.append('-n%d'%l)
    p = execute_auto(*args)
    return p


