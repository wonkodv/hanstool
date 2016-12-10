from Env import *

import shlex
import shutil

@cmd(name="$")
def _procio(cmd:args.ExecutableWithArgs):
    """Get Programm output."""
    show(procio(cmd, shell=True, is_split=False))

@cmd(name="#")
def _execute(cmd:args.ExecutableWithArgs):
    """Execute a Program and wait for completion."""
    p = execute(cmd, is_split=False)
    p.wait()
    return p

@cmd(name="&")
def _execute_bg(cmd:args.ExecutableWithArgs):
    """Execute a Program and let it run in background."""
    p = execute_disconnected(cmd, is_split=False)
    return p


EXE_COMPLETERS = {}

def exe_completer(name):
    def deco(f):
        EXE_COMPLETERS[name] = deco
        return f
    return deco

@Env.updateable
def complete_executable_with_args(s):
    parts = shlex.split(s+"|")
    #TODO join with ShellArgs Code

    parts[-1] = parts[-1][:-1]

    last = parts[-1]
    prefix = s[:len(s)-len(last)]
    exe = parts[0]

    if len(parts) == 1:
        return complete_executables(exe)

    try:
        compl = EXE_COMPLETERS[exe]
    except KeyError:
        compl = complete_path(last)

    return (prefix + c for c in compl)


@COMMAND_NOT_FOUND_HOOK.register
def _executable_command_h(s):
    try:
        parts = shlex.split(s)
    except ValueError:
        pass
    else:
        if shutil.which(parts[0]):
            return _procio, s




@exe_completer('ls')
def complete_ls(parts):
    assert parts[0] == 'ls'

    if parts[-1] == '-':
        for f in 'lrst10':
            yield '-' + f
    yield from complete_path(parts[0])

