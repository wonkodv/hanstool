"""Completion hook for executables with args.

One function can be registered for every executable
(Path(parts[0]).name.lower()) using the exe_completer decorator. A function is passed
the string parts of shlex.split. parts[0] is the exe, parts[1] the 1st argument if any.
Functions should yield completed versions of `parts[-1]` and return True if this
is all, or nothing if File-Completion should be tried.
"""
import shlex

from Env import *

import ht3.hook

EXECUTABLE_W_ARGS_COMPLETE_HOOK = ht3.hook.GeneratorHook("parts")
Env["EXECUTABLE_W_ARGS_COMPLETE_HOOK"] = EXECUTABLE_W_ARGS_COMPLETE_HOOK


@Env.updateable
def complete_executable_with_args(string):
    """Complete a executable with its args"""

    # TODO deduplicate with ShellArgParser

    # Example 1: dir C:/Program" Files/"

    for quote in ["", '"', "'"]:
        try:
            parts = shlex.split(string + quote + "|")  # pipe for cursor pos
        except ValueError:
            continue
        else:
            break
    else:
        # raise the error:
        shelx.split(string)

    # Ex1   dir
    #       C:/Program files/|

    assert parts[-1][-1] == "|"

    current = parts[-1][:-1]
    parts[-1] = current

    for v in EXECUTABLE_W_ARGS_COMPLETE_HOOK(parts=parts):
        v = str(v)
        if not v.startswith(current):
            continue
        v = v[len(current) :]
        if shlex._find_unsafe(v) is None:
            yield string + v + quote
        else:
            if quote:
                yield string + v.replace(quote, "\\" + quote) + quote
            else:
                yield string + '"' + v.replace('"', r"\"") + '"'


args.ExecutableWithArgs = args.Param(
    complete=complete_executable_with_args, doc="ExecutableWithArgs"
)


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


if which("bash") and False:
    # TODO: make this like
    #   https://github.com/Kloadut/awesome-debian/blob/master/lib/awful/completion.lua

    @EXECUTABLE_W_ARGS_COMPLETE_HOOK.register
    def bash_completion(parts):
        if len(parts) < 2:
            return
        t = procio(
            "bash -c "
            + shellescape(
                """
                    [ -f /etc/bash_completion ] && source /etc/bash_completion ;
                    [ -f /usr/share/bash-completion/bash_completion ] && source /usr/share/bash-completion/bash_completion ;
                    complete -p """
                + shellescape(parts[0])
            ),
            shell=False,
            is_split=False,
        )

        function = t.partition(" -F ")[3].partition(" ")[0]

        print(function)

        exe = shellescape(parts[0])
        COMP_WORDS = shlex.join(parts)
        COMP_LINE = shellescape(COMP_WORDS)
        COMP_POINT = len(COMP_LINE)
        COMP_CWORD = len(parts) - 1

        t = procio(
            "bash -c "
            + shellescape(
                """
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
                    exe, COMP_WORDS, COMP_LINE, COMP_POINT, COMP_CWORD, function
                )
            ),
            shell=False,
            is_split=False,
        )
        print(t)


SPECIFIC_COMPLETERS = {}
Env["SPECIFIC_COMPLETERS"] = SPECIFIC_COMPLETERS


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
        SPECIFIC_COMPLETERS[e.lower()] = f

    return deco
