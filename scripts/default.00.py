
cmd(exit)
cmd(name='l')(list_commands)
cmd(name=';',args=1)(execute_py_expression)
cmd(name='=',args=1)(evaluate_py_expression)
cmd(name='?', args=1)(help_command)

if Check.frontend('ht3.cli'):
    @cmd(name="$", args=1)
    def _shell(arg):
        p = ht3.lib.shell(arg)
        if Check.current_frontend('ht3.cli'):
            return p.wait()
        return p

    @cmd(name="!", args="shell")
    def _execute(args):
        p = ht3.lib.execute(*args)
        if Check.current_frontend('ht3.cli'):
            return p.wait()
        return p

    @cmd(name="$&", args=1)
    def _shell_bg(arg):
        p = ht3.lib.shell(arg)
        return p

    @cmd(name="!&", args="shell")
    def _execute_bg(args):
        p = ht3.lib.execute(*args)
        return p
else:
    @cmd(name="$", args=1)
    def _shell(arg):
        p = ht3.lib.shell(arg)
        return p

    @cmd(name="!", args="shell")
    def _execute(args):
        p = ht3.lib.execute(*args)
        return p


@cmd(name="+", args=COMMANDS)
def edit_command(c):
    """ Edit the location where a command was defined """
    f, l = c.origin
    f = shellescape(f)
    l = int(l)
    e = os.environ.get('EDITOR', 'gvim')
    if e.endswith('vim'):
        shell("%s %s +%d"%(e, f, l))
    else:
        shell("%s %s"%(e, f))


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


@cmd
def restart():
    import os, sys
    os.execl(sys.executable, sys.executable, "-m", "ht3", *sys.argv[1:])

if Check.frontend('ht3.gui', 'ht3.hotkey'):
    @cmd(HotKey="F8")
    def httofront():
        ht3.gui.show()

if Check.frontend('ht3.gui'):
    @ht3.gui.do_on_start
    def _():
        ht3.gui.stay_on_top()
        ht3.gui.set_rect(5,44,72,27)

