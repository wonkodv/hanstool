cmd(exit)
cmd(name='l')(list_commands)
cmd(name='e')(list_env)
cmd(name=';',args=1, complete=complete_py)(execute_py_expression)
cmd(name='?', args=1, complete=complete_all)(help_command)
cmd(name=':', args=1)(fake)

@cmd(name='=',args='?', complete=complete_py)
def _show_eval(s=""):
    """ Evaluate a python expression and show the result """
    if s:
        r = evaluate_py_expression(s)
        Env._ = r
        Env.__.append(r)
    else:
        r = None
    show(r)
    return None

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

    # disconnect stdinout for bg
    @cmd(name="$&", args=1)
    def _shell_bg(arg):
        p = ht3.lib.shell(arg)
        return p

    @cmd(name="!&", args="shell")
    def _execute_bg(args):
        p = ht3.lib.execute(*args)
        return p
else:
    cmd(name="$", args=1)(shell)
    cmd(name="!", args="shell")(execute)

def edit_file(file_name, line=1):
    f = shellescape(str(file_name)) # allow paths
    l = int(line)
    e = os.environ.get('EDITOR', 'gvim')
    if e.endswith('vim'):
        shell("%s %s +%d"%(e, f, l))
    else:
        shell("%s %s"%(e, f))

@cmd(name="+", args=COMMANDS)
def edit_command(c):
    """ Edit the location where a command was defined """
    f, l = c.origin
    edit_file(f, l)

@cmd(name="++", args="shell")
def add_command(script, name=None):
    """ Add a new command to a script.
        First argument is matched against all scripts,
        second is used as command name
    """
    import ht3.lib
    for s in ht3.lib.SCRIPTS:
        if s.name.find(script) >= 0:
            if name:
                with s.open("ta") as f:
                    f.write("\n@cmd(name='"+name+"', args=0)\ndef "+name+"():\n    pass")
            with s.open("rt") as f:
                l = len(list(f))
            edit_file(s, l)

@cmd(name="<", args='path')
def run_command_file(p):
    with p.open('rt') as f:
        for l in f:
            run_command(l)


@cmd(args=1, complete=lambda s:COMMANDS.keys())
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
    """ Check if all loaded Scripts can be compiled and then restart the python
        programm using sys.executable, "-m ht3" and args, where args is all
        -f, -s and -r args, NOT -x.
    """
    import os, sys
    for path in ht3.lib.SCRIPTS:
        with path.open("rt") as f:
            c = f.read()
        try:
            compile(c, str(path), "exec")
        except Exception as e:
            handle_exception(e)
            return
    args = []
    if Check.os.win:
        args.append('"' + sys.executable + '"')
    else:
        args.append(sys.executable)
    args += ['-m','ht3']
    if not '_RESTARTED' in Env.dict:
        args += ['-e', '_RESTARTED', '1']

    it = iter(sys.argv[1:])
    for a in it:
        if a in ['-f', '-s']:
            args += [a, next(it)]
        elif a == '-e':
            k = next(it)
            v = next(it)
            if v == '_RESTARTED':
                v=str(int(v)+1)
            args += [a, k, v]
        elif a == '-r':
            args += [a]
        else:
            assert a == '-x'
            next(it)    # dont execute -x
    os.execv(sys.executable, args)

if Check.frontend('ht3.gui', 'ht3.hotkey'):
    @cmd(HotKey="F8")
    def httofront():
        ht3.gui.cmd_win_to_front()

if Check.frontend('ht3.gui'):
    @ht3.gui.do_on_start
    def _():
        ht3.gui.cmd_win_stay_on_top()
