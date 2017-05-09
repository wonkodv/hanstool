"""Completion hook for executables with args.

The string is shlex.split and passed as `parts`.
functions should yield completed versions of `parts[-1],
The completers that are 
"""
from Env import *

import shlex
import ht3.hook

EXECUTABLE_W_ARGS_COMPLETE_HOOK = ht3.hook.GeneratorHook("parts")
Env['EXECUTABLE_W_ARGS_COMPLETE_HOOK'] = EXECUTABLE_W_ARGS_COMPLETE_HOOK

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

    #TODO: Does not work if string is `foo b"a"r` because current is `bar` not `b"a"r`
    prefix = string[:len(string)-len(current+quote)]

    for v in EXECUTABLE_W_ARGS_COMPLETE_HOOK(parts=parts):
        v = str(v)
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
                    assert s.startswith(string), (s, string)
                    yield s

args.ExecutableWithArgs = args.Param(complete=complete_executable_with_args, doc="ExecutableWithArgs")

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

if which('bash') and False:

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

SPECIFIC_COMPLETERS = {}
Env['SPECIFIC_COMPLETERS'] = SPECIFIC_COMPLETERS

@EXECUTABLE_W_ARGS_COMPLETE_HOOK.register
def specific_completions(parts):
    main = Path(parts[0])
    exe = main.name.lower()
    try:
        c = SPECIFIC_COMPLETERS[exe]
    except KeyError:
        return ()
    return c(parts)

@Env
def exe_completer(e):
    assert not callable(e)
    def deco(f):
        SPECIFIC_COMPLETERS[e] = f
    return deco

