import shlex

from Env import *


@cmd(name="$")
def _procio(cmd: args.ExecutableWithArgs):
    """Show output of a shell command."""
    out = procio(cmd, shell=True, is_split=False)
    show(out)
    return out


@cmd(name="#")
def _execute(cmd: args.ExecutableWithArgs):
    """Execute a Program and wait for completion."""
    p = execute(cmd, is_split=False)
    return p.wait()


@cmd(name="&")
def _execute_bg(cmd: args.ExecutableWithArgs):
    """Execute a Program and let it run in background."""
    p = execute_disconnected(cmd, is_split=False)
    return p


@cmd(name="")
def _execute_auto(cmd: args.ExecutableWithArgs):
    p = execute_auto(cmd, is_split=False)


@COMMAND_NOT_FOUND_HOOK.register
def _executable_command_h(command_string):
    s = command_string
    try:
        parts = shlex.split(s)
    except ValueError:
        pass
    else:
        if which(parts[0]):
            if CHECK.is_cli_frontend:
                return _procio.command(s, s)
            else:
                return _execute_bg.command(s, s)


@cmd(name="which")
def _which(cmd: args.Executable):
    p = which(cmd)
    show(p)
    return p
