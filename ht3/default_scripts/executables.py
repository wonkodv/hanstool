from Env import *

import shlex
import shutil
import queue
import shutil

from subprocess import PIPE

@Env.updateable
def complete_executable_with_args(string):
    """Complete a executable with its args"""


        #TODO deduplicate with ShellArgParser

    for quote in ['', '"', "'"]:
        try:
            parts = shlex.split(string+quote+'|') # pipe for cursor pos
        except ValueError:
            continue
        else:
            break
    else:
        # raise the error:
        shelx.split(string)

    assert parts[-1][-1] == '|'

    current = parts[-1][:-1]
    parts[-1] = current

    prefix = string[:len(string)-len(current)]

    for v in EXECUTABLE_W_ARGS_COMPLETE_HOOK(parts=parts):
        if shlex._find_unsafe(v) is None:
            s = prefix + v + quote
            if s.startswith(string):
                yield s
        else:
            if quote:
                s = prefix + v.replace(quote, "\\"+quote) + quote
                if s.startswith(string):
                    yield s
            else:
                if v.startswith(current):
                    s = (
                        prefix +
                        current +
                        '"'+
                        v[len(current):].replace('"', r'\"') +
                        '"'
                    )
                    assert s.startswith(string)
                    yield s

args.ExecutableWithArgs = args.Param(complete=complete_executable_with_args, doc="ExecutableWithArgs")

@cmd(name="$")
def _procio(cmd:args.ExecutableWithArgs):
    """Show output of a shell command."""
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

@cmd(name="")
def _execute_auto(cmd:args.ExecutableWithArgs):
    p = execute_auto(cmd, is_split=False)

@COMMAND_NOT_FOUND_HOOK.register
def _executable_command_h(command_string):
    s = command_string
    try:
        parts = shlex.split(s)
    except ValueError:
        pass
    else:
        #TODO use Env.which and decide how to execute this
        if shutil.which(parts[0]):
            return _procio.command(s, s)


"""Completion hook for executables with args.

The string is shlex.split and passed as `parts`.
functions should yield completed versions of `parts[-1],
The completers that are 
"""
EXECUTABLE_W_ARGS_COMPLETE_HOOK = ht3.hook.GeneratorHook("parts")


@EXECUTABLE_W_ARGS_COMPLETE_HOOK.register
def _complete_executeble_wo_args(parts):
    if len(parts) > 1:
        return
    yield from complete_executable(parts[0])

@EXECUTABLE_W_ARGS_COMPLETE_HOOK.register
def _complete_w_file(parts):
    if len(parts) > 0:
        return complete_path(parts[-1])
    return []


@EXECUTABLE_W_ARGS_COMPLETE_HOOK.register
def complete_ls(parts):
    if parts[0] != 'ls':
        return

    if parts[-1] == '-':
        for f in 'lrst10':
            yield '-' + f
        return True


if shutil.which('bash') and False:

    # TODO: make this like
    #   https://github.com/Kloadut/awesome-debian/blob/master/lib/awful/completion.lua

    @EXECUTABLE_W_ARGS_COMPLETE_HOOK.register
    def bash_completion(parts):
        if len(parts) < 2:
            return
        t = procio("bash -c " +
                shellescape("""
                    [ -f /etc/bash_completion ] && source /etc/bash_completion ;
                    [ -f /usr/share/bash-completion/bash_completion ] && source /usr/share/bash-completion/bash_completion ;
                    complete -p """ + shellescape(parts[0])),
                shell=False,
                is_split=False)

        function = t.partition(" -F ")[3].partition(" ")[0]

        print(function)

        exe         = shellescape(parts[0])
        COMP_WORDS  = shlex.join(parts)
        COMP_LINE   = shellescape(COMP_WORDS)
        COMP_POINT  = len(COMP_LINE)
        COMP_CWORD  = len(parts) - 1

        t = procio("bash -c " +
                shellescape("""
                    [ -f /etc/bash_completion ] && source /etc/bash_completion ;
                    [ -f /usr/share/bash-completion/bash_completion ] && source /usr/share/bash-completion/bash_completion ;
                    _completion_loader {}
                    COMP_WORDS=({})
                    COMP_LINE={}
                    COMP_POINT={}
                    COMP_CWORD={}
                    {}
                    printf '%s\n' "${COMPREPLY[@]}"
                    """.format(
                        exe,
                        COMP_WORDS,
                        COMP_LINE,
                        COMP_POINT,
                        COMP_CWORD,
                        function
                        )),
                shell=False,
                is_split=False)
        print(t)

