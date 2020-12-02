"""Commands that make HT Usable."""

import contextlib
import importlib
import inspect
import io
import os
import os.path
import pathlib
import sys
import textwrap
import time

import ht3.scripts
from Env import *
from ht3.scripts import SCRIPTS


@cmd(name="l")
def list_commands():
    """ List all commands."""
    text = ""
    for n in sorted(COMMANDS):
        c = COMMANDS[n]
        d = inspect.getdoc(c).partition("\n\n")[0]
        doc = textwrap.shorten(d, 60)
        doc = "%- 20s %s\n" % (n, doc)
        text += doc
    Env.show(text)


@cmd(name="?")
def _help(what: args.Union(args.Command, args.Python)):
    """ Show help on a command or evaluated python expression """
    if what in COMMANDS:
        obj = COMMANDS[what]
        show(inspect.getdoc(obj))
    else:
        obj = evaluate_py_expression(what)
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            help(obj)
        s = f.getvalue()
        show(s)


@cmd
def exit(returncode: int = 0):
    """Quit with return code or 0."""
    sys.exit(returncode)


cmd(exit, name="quit")


@cmd(name="+")
def edit_command(c: args.Union(args.Command, args.Python)):
    """Edit the location where a command or function was defined."""
    if c in COMMANDS:
        file_name, line = COMMANDS[c].origin
    else:
        o = evaluate_py_expression(c)
        o = inspect.unwrap(o)  # unwrap @Env.updateable functions
        try:
            file_name = inspect.getsourcefile(o)
        except TypeError as e:
            try:
                file_name = inspect.getsourcefile(type(o))
            except TypeError:
                raise e
        try:
            _, line = inspect.getsourcelines(o)
        except TypeError:
            line = 0
    edit_file(file_name, line)


@Env
def _complete_script_names(s):
    return (Path(m.__file__).name for m in reversed(SCRIPTS))


@Env
@cmd(name="++")
def add_command(script: _complete_script_names, name=None, text=None):
    """Define a command in a script.

    1.  If `script` matches a loaded one, it is edited, otherwise
        a new script with the name (it must end in .py) is created in the
        directory of the most recently loaded script.
    2. If `name` is given, a command definition is added with the name.
    3. If text is given, it is added as comment to the function
    4. The script is edited.
    5. you should restart for the new command to be activated.

    """
    for m in SCRIPTS:
        s = Path(m.__file__)
        if s.name == script:
            break
    else:
        if not script.endswith(".py"):
            raise ValueError(
                "The script must be the name of a loaded script or"
                " a valid name for a new one"
            )
        s = s.parent  # parent of last loaded script
        if s.name == "default_scripts":
            s = pathlib.Path("~/.config/ht3").expanduser()
            if not s.exists():
                show("Creating Directory " + str(s))
                s.mkdir(parents=True)
        s = s / script
        if s.exists():
            show(f"Script already exists: {s}")
        else:
            show(f"New Script {s}")
            with s.open("wt") as f:
                f.write('"""" A new Script """\n\nfrom Env import *\n\n')

    if name:
        with s.open("ta") as f:
            f.write(
                "\n"
                "\n@cmd"
                "\ndef " + name + "():"
                "\n    " + (text if text else "pass")
            )

    with s.open("rt") as f:
        line_no = len(list(f))
    edit_file(s, line_no)


@cmd
def reload(*modules: args.Union(["ENV"], args.Option(sys.modules, sort=True))):
    """Reload some modules and all scripts.

    Check if all loaded Scripts can be compiled, then reload the specified module
    and reload all scripts.
    Can be used after editing a script."""
    # Things we don't want to loose by Env._reload
    from ht3.command import COMMANDS
    from ht3.scripts import reload_all
    from Env import CHECK

    try:
        from Env import _RELOADED
    except ImportError:
        _RELOADED = 0

    if not ht3.scripts.check_all_compilable():
        return

    debug = print

    # disable and delete hotkeys
    if CHECK.frontend("ht3.hotkey"):
        debug("Reload: Disable all hotkeys")
        ht3.hotkey.disable_all_hotkeys()  # let hotkeys and old functions be deleted
        hotkeys = list(ht3.hotkey.HotKey.HOTKEYS.values())
        ht3.hotkey.HotKey.HOTKEYS.clear()  # Remove all hotkeys from the cache
        assert not any(hk.active for hk in hotkeys)

    # remove hooks defined in scripts
    for h in ht3.hook.Hook.HOOKS:
        for c in list(h.callbacks):
            if c.__module__.startswith("Env."):
                debug(
                    f"Reload: Remove Hook {c.__name__} defined in script {c.__module__}"
                )
                h.callbacks.remove(c)

    debug("Reload: Clear commands")
    COMMANDS.clear()

    debug("Reload: Modules")
    for module in modules:
        if module == "ENV":
            debug("Reload: ENV")
            Env._reload()
        else:
            debug(f"Reload: module {module}")
            m = importlib.import_module(module)
            importlib.reload(m)

    debug("Reload: ===== Cleanup Done, Begin reloading =====")

    Env["_RELOADED"] = _RELOADED + 1

    try:
        debug("Reload: Scripts")
        reload_all()
    finally:
        if CHECK.frontend("ht3.hotkey"):
            debug("Reload: Hotkeys")
            ht3.hotkey.reload_hotkeys()

    log("Reload: ===== Done =====")


@cmd
def restart(*more_args):
    """Restart ht.

    Check if all loaded Scripts can be compiled and then restart the python
    programm using sys.executable, "-m ht3" and args, where args is all
    args without --command. a _RESTARTED counter is incremented.
    """
    if not ht3.scripts.check_all_compilable():
        return

    args = []
    if CHECK.os.win:
        args.append('"' + sys.executable + '"')
    else:
        args.append(sys.executable)

    args += ["-m", "ht3"]

    arg_iter = iter(sys.argv[1:])

    # Copy from ht3.main.parse. Filters "command" arguments
    for a in arg_iter:
        if a.startswith("-"):
            for short, long, function, params, done in ht3.main.POSSIBLE_ARGUMENTS:
                if a == short or a == long:
                    if params:
                        try:
                            p = tuple(next(arg_iter) for _ in range(params))
                        except StopIteration:
                            raise ArgumentError("Expecting a parameter", a)
                    else:
                        p = ()
                    if not (
                        long == "--command"
                        or (long == "--set-env" and p[0] == "_RESTARTED")
                    ):
                        args.append(a)
                        args.extend(p)
                    break
            else:
                raise ArgumentError(f"Invalid option {a}")
        else:
            args.append(a)

    args.extend(more_args)

    r = Env.get("_RESTARTED", 0)
    r = int(r)
    r += 1
    args.extend(("--set-env", "_RESTARTED", f"{r}"))

    show("\n==================== RESTART ===================\n")
    os.execv(sys.executable, args)


if CHECK.frontend("ht3.gui"):
    import ht3.gui

    ht3.gui.do_on_start(ht3.gui.cmd_win_stay_on_top)

    if CHECK.frontend("ht3.hotkey"):
        HT_TO_FRONT_TIME = 0

        @cmd(attrs=dict(HotKey="F8"))
        def httofront():
            """Show the input and, if executed twice within short time, show log win."""
            global HT_TO_FRONT_TIME
            if time.monotonic() - HT_TO_FRONT_TIME > 0.25:
                Env.MoveHtWindow()
                ht3.gui.cmd_win_to_front()
                HT_TO_FRONT_TIME = time.monotonic()
            else:
                ht3.gui.log_win_to_front()


if CHECK.frontend("ht3.hotkey"):
    import ht3.hotkey

    def complete_hotkey(s):
        return sorted(hk.hotkey for hk in ht3.hotkey.HotKey.HOTKEYS.values())

    @cmd
    def disable_hotkey(hk: complete_hotkey = None):
        """Disable a hotkey."""
        if hk:
            hk = ht3.hotkey.get_hotkey(hk)
            hk.unregister()
        else:
            ht3.hotkey.disable_all_hotkeys()

    @cmd
    def enable_hotkey(hk: complete_hotkey = None):
        """Disable a hotkey."""
        if hk:
            hk = ht3.hotkey.get_hotkey(hk)
            hk.register()
        else:
            ht3.hotkey.enable_all_hotkeys()
