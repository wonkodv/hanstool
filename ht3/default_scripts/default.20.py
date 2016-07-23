"""The default commands that make the HT3 usable."""

from Env import *

from ht3.scripts import SCRIPTS

import ht3.scripts

import difflib
import importlib
import inspect
import os
import os.path
import pathlib
import re
import shlex
import shutil
import sys
import time



@cmd(name='l')
def list_commands():
    """ List all commands """
    text = ""
    for n in sorted(COMMANDS):
        c = COMMANDS[n]
        d = c.doc
        doc = textwrap.shorten(d,60)
        doc = "%- 20s %s\n" % (n, doc)
        text += doc
    Env.show(text)

@cmd(name='?')
def _help(what:args.Union(args.Command, args.Python)):
    """ Show help on a command or evaluated python expression """
    if what in COMMANDS:
        obj = COMMANDS[what]
    else:
        obj = evaluate_py_expression(what)
    help(obj)

def _complete_fake(string):
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

@cmd(name=':')
def test_fake(s:_complete_fake):
    sleep(0.5)
    fake(s, restore_mouse_pos=True)
    global FAKE_TEXT
    FAKE_TEXT = s

@cmd(attrs=dict(HotKey='F10'))
def repeat_fake():
    global FAKE_TEXT
    fake(FAKE_TEXT)

# Some Eval Python functions
@cmd(name='=')
def _show_eval(s:args.Python=""):
    """ Evaluate a python expression and show the result """
    r = evaluate_py_expression(s.lstrip())
    global _
    _ = r
    show(r)
    return None

@cmd(name=';')
def _execute_py_expression(s:args.Python):
    execute_py_expression(s.lstrip())


@COMMAND_NOT_FOUND_HOOK.register
def _python_command_h(s):
    try:
        c = compile(s, '<input>', 'eval')
        return (lambda s: exec(c, Env.dict)), s
    except SyntaxError:
        pass
    try:
        c = compile(s, '<input>', 'exec')
        return (lambda s: exec(c, Env.dict)), s
    except SyntaxError:
        pass


@cmd
def exit():
    sys.exit(0)

@cmd(name="+")
def edit_command(c:args.Union(args.Command, args.Python)):
    """ Edit the location where a command or function was defined """
    if c in COMMANDS:
        f, l = COMMANDS[c].origin
    else:
        o = evaluate_py_expression(c)
        l = 0
        f = None
        try:
            f = inspect.getsourcefile(o)
        except TypeError:
            # for classes defined in scripts, use location of a method
            d = getattr(o,'__dict__',{})
            for k in d:
                if not k.startswith('_'):
                    if inspect.isfunction(d[k]):
                        o = d[k]
                        f = inspect.getsourcefile(o)
        try:
            _, l = inspect.getsourcelines(o)
        except TypeError:
            l = 0
    p = edit_file(f, l)

def _complete_script_names(s):
    return reversed(list(filter_completions(s, (p.name for p in SCRIPTS))))

@cmd(name="++")
def add_command(script:_complete_script_names, name=None, text=None):
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


@cmd
def reload(module:args.Union(args.Option(sys.modules, sort=True), ["ENV", "ALL"])=None):
    if not ht3.scripts.check_all_compilable():
        return

    if CHECK.frontend('ht3.hotkey'):
        ht3.hotkey.disable_all_hotkeys() # let hotkeys and old functions be deleted
        l = list(ht3.hotkey.HotKey.HOTKEYS.values())
        ht3.hotkey.HotKey.HOTKEYS.clear() # Remove all hotkeys from the cache
        assert not any(hk.active for hk in l)

    if module:
        if module.lower() == 'env':
            log("\n==================== ENV RELOAD ===================\n")
            Env._reload()
            ht3.command.COMMANDS.clear()
        elif module.lower() == 'all':
            log("\n==================== FULL RELOAD ===================\n")
            for m in sys.modules:
                importlib.import_module(m)
                log("reloaded "+m)
            Env._reload()
            ht3.command.COMMANDS.clear()
        else:
            m = importlib.import_module(module)
            log("\n===== Reload Module "+module+" =========\n")
            importlib.reload(m)

    log("\n===== RELOAD SCRIPTS ====\n")
    ht3.scripts.reload_all()

    if CHECK.frontend('ht3.hotkey'):
        ht3.hotkey.reload_hotkeys()




@cmd
def restart(*more_args):
    """ Check if all loaded Scripts can be compiled and then restart the python
        programm using sys.executable, "-m ht3" and args, where args is all
        -f, -s and -r args, NOT -x.
    """
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
    import ht3.gui
    ht3.gui.do_on_start(ht3.gui.cmd_win_stay_on_top)

    if CHECK.frontend('ht3.hotkey'):
        HT_TO_FRONT_TIME=0
        @cmd(attrs=dict(HotKey="F8"))
        def httofront():
            """ Show the input and, if executed twice within short time, show log win """
            global HT_TO_FRONT_TIME
            if time.monotonic() - HT_TO_FRONT_TIME > 0.25:
                ht3.gui.cmd_win_to_front()
                HT_TO_FRONT_TIME = time.monotonic()
            else:
                ht3.gui.log_win_to_front()


if CHECK.frontend('ht3.hotkey'):
    import ht3.hotkey

    def complete_hotkey(s):
        return sorted(hk.hotkey for hk in ht3.hotkey.HotKey.HOTKEYS.values())

    @cmd
    def disable_hotkey(hk:complete_hotkey=None):
        if hk:
            hk = ht3.hotkey.get_hotkey(hk)
            hk.unregister()
        else:
            ht3.hotkey.disable_all_hotkeys()
