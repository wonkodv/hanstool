
# Helpers
cmd(name='l')(list_commands)
cmd(name='e')(list_env)
cmd(name='?', args=1, complete=complete_all)(help_command)

# Some Eval Python functions
cmd(name=';',args=1, complete=complete_py)(execute_py_expression)
cmd(name=':', args=1)(fake)

@cmd(name='=',args='?', complete=complete_py)
def _show_eval(s=""):
    """ Evaluate a python expression and show the result """
    r = evaluate_py_expression(s)
    Env._ = r
    show(r)
    return None

@cmd
def exit():
    import sys
    sys.exit(0)


# Execute Programms and Shell

if Check.frontend('ht3.cli'):
    # Programms should run in foreground when invoked from CLI
    @cmd(name="$", args=1)
    def _shell(arg):
        p = shell(arg)
        if Check.current_frontend('ht3.cli'):
            return p.wait()
        return p

    @cmd(name="!", args="shell")
    def _execute(args):
        p = execute(*args)
        if Check.current_frontend('ht3.cli'):
            return p.wait()
        return p

    # TODO disconnect stdinout for bg
    @cmd(name="$&", args=1)
    def _shell_bg(arg):
        p = shell(arg)
        return p

    @cmd(name="!&", args="shell")
    def _execute_bg(args):
        p = execute(*args)
        return p
else:
    cmd(name="$", args=1)(shell)
    cmd(name="!", args='shell')(execute)

def _():
    import os
    import os.path

    if 'EDITOR' in os.environ:
        import shlex
        e = shlex.split(os.environ['EDITOR'])
    elif Check.os.posix:
        if Check.frontend('ht3.cli'):
            EDITOR=['vim']
        else:
            EDITOR=['gvim']
    elif Check.os.win:
        e = r"C:\Program Files (x86)\Notepad++\notepad++.exe"
        if os.path.exists(e):
            e = [e]
        else:
            e = ['notepad.exe']
    Env.EDITOR = e
_()

def edit_file(file_name, line=1):
    f = str(file_name) # allow pathlib.Path
    l = int(line)
    e = Env.EDITOR[0]
    if e[-4:] == '.exe':
        e = e[:-4]
    if e.endswith('vim'):
        args = Env.EDITOR + [f, '+%d'%l ]
    elif e.endswith('notepad++'):
        args = Env.EDITOR + ['-n%d'%l, f]
    else:
        args = EDITOR + [f]
    p = execute(*args)
    if Check.current_frontend == 'ht3.cli':
        p.wait()

@cmd(name="+", args="1", complete=complete_all)
def edit_command(c):
    """ Edit the location where a command or function was defined """
    if c in COMMANDS:
        f, l = COMMANDS[c].origin
    else:
        o = evaluate_py_expression(c)
        import inspect
        if not inspect.isfunction(o):
            raise TypeError("Not a function", o)
        f, l = inspect.getsourcefile(o), o.__code__.co_firstlineno
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
    import pdb, ht3.command
    pdb.set_trace()
    ht3.command.run_command(what)


@cmd
def py():
    """ start a python repl """
    import sys
    return execute(sys.executable)

@cmd(args="shell")
def restart(*more_args):
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
            log_error(e)
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

    it = iter(more_args)
    for a in it:
        if a in ['-f', '-s', '-x']:
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
            raise ValueError("Unsupported Argument", a)

    print ("\n==================== RESTART ===================\n")
    os.execv(sys.executable, args)

if Check.frontend('ht3.gui', 'ht3.hotkey'):
    _httofront_time=0
    @cmd(HotKey="F8")
    def httofront():
        """ Show the input and, if executed twice within short time, show log win """
        global _httofront_time
        import time
        if time.monotonic() - _httofront_time > 0.25:
            ht3.gui.cmd_win_to_front()
            _httofront_time = time.monotonic()
        else:
            ht3.gui.log_win_to_front()

if Check.frontend('ht3.gui'):
    @ht3.gui.do_on_start
    def _():
        ht3.gui.cmd_win_stay_on_top()
