"""The default commands that make the HT3 usable."""

# Helpers
cmd(name='l')(list_commands)
cmd(name='e')(list_env)
cmd(name='?', args=1, complete=complete_all)(help_command)

# Some Eval Python functions
@cmd(name=';',args=1, complete=complete_py)
def _execute_py_expression(s):
    execute_py_expression(s.lstrip())

def _complete_fake(string):
    import re
    parts = re.split('[^A-Za-z0-9]+', string)
    if len(parts) > 0:
        p = parts[-1]
    else:
        p=''

    prefix = string[:len(string)-len(p)]
    values = filter_completions_i(p, ht3.utils.fake_input.KEY_CODES)
    values = sorted(values)
    values = (prefix + x for x in values)
    return values

@cmd(name=':', args=1, complete=_complete_fake)
def test_fake(s):
    sleep(0.5)
    fake(s)
    global FAKE_TEXT
    FAKE_TEXT = s

@cmd(HotKey='F10')
def repeat_fake():
    global FAKE_TEXT
    fake(FAKE_TEXT)

@cmd(name='=',args='?', complete=complete_py)
def _show_eval(s=""):
    """ Evaluate a python expression and show the result """
    r = evaluate_py_expression(s.lstrip())
    global _
    _ = r
    show(r)
    return None

@cmd
def exit():
    import sys
    sys.exit(0)


# Execute Programms and Shell

if CHECK.frontend('ht3.cli'):
    # Programms should run in foreground when invoked from CLI
    @cmd(name="$", args=1, complete=complete_executable)
    def _shell(arg):
        p = shell(arg)
        if CHECK.current_frontend('ht3.cli'):
            return p.wait()
        return p

    @cmd(name="!")
    def _execute(exe:"executable", *args:Path):
        p = execute(exe, *args)
        if CHECK.current_frontend('ht3.cli'):
            return p.wait()
        return p

    # TODO disconnect stdinout for bg
    @cmd(name="$&", args=1, complete=complete_executable)
    def _shell_bg(arg):
        p = shell(arg)
        return p

    @cmd(name="!&")
    def _execute_bg(exe:"executable", *args:Path):
        p = execute(exe, *args)
        return p
else:
    cmd(name="$", args=1, complete=complete_executable)(shell)
    @cmd(name="!")
    def _execute(exe:"executable", *args:Path):
        p = execute(exe, *args)
        return p

def _get_the_editor():
    import os
    import os.path
    import shutil

    if 'EDITOR' in os.environ:
        import shlex
        e = shlex.split(os.environ['EDITOR'])
    elif CHECK.os.win:
        editors = [
            "gvim",
            r"C:\Program Files (x86)\Notepad++\notepad++.exe",
            r"C:\Program Files\Notepad++\notepad++.exe"
        ]

        for e in editors:
            if os.path.exists(e) or shutil.which(e):
                e = [e]
                break
        else:
            e = ['notepad.exe']
    else:
        if CHECK.frontend('ht3.cli'):
            editors =['vim', 'nano', 'emacs']
        else:
            editors =['gvim']
        for s in editors:
            s = shutil.which(s)
            if s:
                e = [s]
                break
        else:
            e = ['ed'] # haha
    global EDITOR
    EDITOR = tuple(e) # make unmodifiable
_get_the_editor()
del _get_the_editor

@cmd
def edit_file(file_name:Path, line:int=0):
    """Edit a file using EDITOR."""
    f = str(file_name) # allow pathlib.Path
    l = int(line)
    e = EDITOR[0].lower()
    if e[-4:] == '.exe' or e[-4:] == '.bat':
        e = e[:-4]

    args = EDITOR + (f, )
    if line:
        if e.endswith('vim'):
            args = EDITOR + (f, '+%d'%l )
        elif e.endswith('notepad++'):
            args = EDITOR + ('-n%d'%l, f)

    p = execute(*args)
    if CHECK.current_frontend == 'ht3.cli':
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

def _complete_script_names(s):
    from ht3.scripts import SCRIPTS
    return filter_completions(s, (p.name for p in SCRIPTS))

@cmd(name="++", args="auto", complete=_complete_script_names)
def add_command(script, name=None, text=None):
    """ define a command in a script.
        1.  If `script` matches a loaded one, it is edited, otherwise
            a new script with the name
            (it must end in .py) is created in the directory of
            the most recently loaded script.
        2. If `name` is given, a command definition is added with the name.
        3. If text is given, it is added as comment to the function
        4. The script is edited.
        5. you should restart for the new command to be activated.

    """
    from ht3.scripts import SCRIPTS
    import pathlib
    import difflib

    name_path = dict((p.name, p) for p in SCRIPTS)

    s = difflib.get_close_matches(script, name_path, 1, 0.5)
    if s:
        s = name_path[s[0]]
    else:
        if not script.endswith('.py'):
            raise ValueError('The first arg must either match a loaded script'
                ' or be a valid name of a new one (foo.10.py)')
        s = SCRIPTS[-1].parent
        if s.name == 'default_scripts':
            s = expanduser('~/.config/ht3')
            s = pathlib.Path(s)
            if not s.exists():
                show("Creating Directory "+str(s))
                s.mkdir(parents=True)
        s = s / script
        assert not s.exists() # s should have matched above.
        show("New Script "+str(s))
        with s.open('wt') as f:
            f.write('"""" A new Script """')

    if name:
        with s.open("ta") as f:
            f.write("\n@cmd"
                    "\ndef "+name+"():"
                    "\n    "+ (text if text else 'pass'))

    with s.open("rt") as f:
        l = len(list(f))
    p = edit_file(s, l)
    p.wait()

@cmd(args=1, complete=general_completion)
def debug(what):
    """ Debug a Command """
    import pdb, ht3.command, inspect
    try:
        cmd, _, args = ht3.command.get_command(what)
        pdb.set_trace()
        return cmd(args)
    except KeyError:
        x = pdb.runeval(what, Env.dict)
        return x

@cmd
def py():
    """ start a python repl """
    import sys
    return execute(sys.executable)

@cmd
def reload(full:WordBool=False):
    import ht3.env
    import ht3.scripts

    if not ht3.scripts.check_all_compilable():
        return
    if full:
        log("\n==================== FULL RELOAD ===================\n")
        Env._reload()
        ht3.command.COMMANDS.clear()
    else:
        log("\n===== RELOAD SCRIPTS ====\n")
    ht3.scripts.reload_all()

    if CHECK.frontend('ht3.hotkey'):
        ht3.hotkey.reload_hotkeys()




@cmd(args="shell")
def restart(*more_args):
    """ Check if all loaded Scripts can be compiled and then restart the python
        programm using sys.executable, "-m ht3" and args, where args is all
        -f, -s and -r args, NOT -x.
    """
    import os, sys
    import ht3.scripts

    if not ht3.scripts.check_all_compilable():
        return

    args = []
    if CHECK.os.win:
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
            assert a == '-x', "Unknown arg "+a+" in restart"
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
    #print not show since gui disappears

    os.execv(sys.executable, args)

if CHECK.frontend('ht3.gui'):
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

    @gui_do_on_start
    def _():
        ht3.gui.cmd_win_stay_on_top()

if CHECK.frontend('ht3.hotkey'):
    @cmd(name="disable_hotkey", args='?', complete=lambda s:sorted(hk for _,hk,_,_ in ht3.hotkey._hotkeys.values()))
    def _disable_hotkey(hk=None):
        if hk:
            disable_hotkey(hk)
        else:
            disable_all_hotkeys()
