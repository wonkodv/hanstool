
cmd(name="$", args=1)(shell)
cmd(name="!", args="shell")(execute)
cmd(exit)
cmd(name='l')(list_commands)
cmd(name=';',args=1)(execute_py_expression)
cmd(name='=',args=1)(evaluate_py_expression)
cmd(name='?', args=1)(help_command)

@cmd(name="+", args=COMMANDS)
def edit_command(cmd):
    """ Edit the location where a command was defined """
    f, l = command.origin

@cmd(name="<", args='path')
def run_command_file(p):
    with p.open('rt') as f:
        for l in f:
            run_command(l)


@cmd(args=1)
def debug(what):
    """ Debug a Command """
    import pdb, ht3.lib
    pdb.runcall(ht3.lib.run_command, what)


@cmd
def py():
    """ start a python repl """
    import sys
    return execute(sys.executable)


@cmd(HotKey="F8")
def httofront():
    show_input_window()
