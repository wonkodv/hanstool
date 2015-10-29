import sys

cmd(name="$", args=1)(shell)
cmd(name="!", args="shell")(execute)
cmd(exit)
cmd(name='l')(list_commands)
cmd(name=';',args=1)(execute_py_expression)
cmd(name='=',args=1)(evaluate_py_expression)
cmd(name='?', args=1)(help_command)

@cmd(name="+", args=COMMANDS)
def edit_command(command):
    """ Edit the location where a command was defined """
    f, l = command.origin
    execute(EDITOR, f)

@cmd
def py():
    """ start a python repl """
    return execute(sys.executable)
