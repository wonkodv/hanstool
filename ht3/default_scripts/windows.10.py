"""Some default commands on Windows."""

from Env import *

from pathlib import Path
import functools
import re

if CHECK.os.win:
    from ctypes import windll

    # 32Bit binaries (python) can not acces System32 Folder, but Sysnative redirects there
    # lots of useful tools there.

    sysnative = Path(r"C:\Windows\Sysnative")
    if sysnative.exists():
        Env['PATH'].append(sysnative)

    @Env
    @cmd(name='o')
    def shellexecute(s:args.Union(args.Path,args.Executable)):
        """Shell Execute, windows's all purpose opening function for files and programms."""
        s = str(s)
        r = windll.shell32.ShellExecuteW(0, "open", s, None, "", 1)
        if r > 32:
            return
        else:
            raise OSError("ShellExecute returned an error: %d" % r)

    @cmd(name="%")
    def explore_command(cmd:args.Command):
        """Show the directory or file used in the target command's source in explorer."""

        w = COMMANDS[cmd].target

        strings = []
        if isinstance(w, functools.partial):
            strings = w.args
        else:
            strings = [s for s in w.__code__.co_consts if isinstance(s, str)]

        for s in strings:
            p = Path(s)
            if p.exists():
                if p.is_dir():
                    log("Directory: "+str(p))
                    arg = str(p)
                else:
                    log("File: "+str(p))
                    arg="/select," + shellescape(str(p))
                execute_disconnected('explorer ' + arg)
                return

    if CHECK.frontend('ht3.gui'):
        import ht3.gui

        def taskbar_window():
            w = Window.TOP.find(class_name='Shell_TrayWnd')
            w = w.find(class_name='ReBarWindow32')
            w = w.find(class_name='ToolbarWindow32', title='hanstool')
            return w

        @Env
        @cmd
        def PlaceOverTaskbar():
            """Find a toolbar named ``hanstool`` and place the command window over it."""
            w = taskbar_window()
            r = w.rect

            @ht3.gui.interact(False)
            def doit(GUI):
                ht3.gui.cmd_win_set_rect(*r)
                Env.log("Set window Rect" + repr(r))
            doit()

        @Env
        @cmd
        def DockInTaskbar():
            """Find a toolbar named ``hanstool`` and place the command window INSIDE it."""
            w = taskbar_window()
            r = w.rect

            @ht3.gui.interact(True)
            def foo(GUI):
                c = GUI.cmd_win.window.winfo_id()
                ht3.gui.cmd_win_set_rect(0, 0, r.width, r.height)

                def to_front(*args):
                    ht3.gui.cmd_win_to_front()

                # Hack so after docking, the windows isn't moved arround.
                GUI.cmd_win.window.bind("<ButtonPress-3>", to_front)
                GUI.cmd_win.window.bind("<ButtonPress-1>", to_front)
                GUI.cmd_win.window.bind("<B1-Motion>", lambda *a:None)
                GUI.cmd_win.window.bind("<B3-Motion>", lambda *a:None)

                return c

            c = foo()
            c = Window(c)
            c.parent = w

    @cmd
    def get_command_line_from_hwnd(w:Window):
        show(command_line_from_hwnd(w))

    def command_line_from_wnd(w):
        o = procio("WMIC path win32_process WHERE processid={:d} GET commandline".format( w.process_id),
                errors="backslashreplace",
        )
        lines = [ l for l in o.split("\n") if l ]
        assert lines[0].strip() == 'CommandLine'
        assert len(lines) == 2
        return lines[1]

    def _complete_script_names(s):
        return Env._complete_script_names(s)

    @cmd(apply_default_param_anotations=True)
    def command_from_window(script:_complete_script_names, wnd:Window="_MOUSE_POS_MAIN", name=None):
        cmdline = command_line_from_wnd(wnd)
        if name is None:
            name = hwnd.title
            name = name.lower()
            name = re.sub("[^a-z_0-9]","",name)
        Env.add_command(script, name=name, text="execute_disconnected(r'{}', is_split=False)".format(cmdline.replace("'", r"\'")))

    @cmd(apply_default_param_anotations=True)
    def analyze_windows(w:Window="_MOUSE_POS"):
        msg = []
        long = []
        short = []
        Env['w'] = w
        while(w):
            r = w.rect
            msg.append(f"{w:6X}\t{w.title:20s}\t'{w.class_name:20s}'\t{r.left: 4} {r.top: 4} {r.width: 4} {r.height: 4}")
            if w.parent:
                p = 'w'
            else:
                p = 'Window.TOP'
            long.append(    f"    w={p}.find(class_name={w.class_name!r}, title={w.title!r})\n"
                            f"    w.set_pos(left={r.left}, top={r.top}, width={r.width}, height={r.height})")
            short.append(f".find(class_name={w.class_name!r}, title={w.title!r})")
            w = w.parent
        show("\n".join(msg))
        show("\n".join(reversed(long)))
        show("\n    w = Window.TOP"+"".join(reversed(short)))

    def device_manager():
        execute_disconnected('mmc devmgmt.msc')

    @cmd(attrs={"HotKey":"SCROLL"})
    def private():
        """Hide a Window (Firefox-Private Browsing) while someone looks over your Shoulder"""
        w = Window.TOP.search_by_title("Firefox \(Private Browsing\)$")

        if w.visible:
            w.hide()
        else:
            w.show()
            w.to_front()

    @cmd
    def tmp(name=None):
        p = Path("~/tmp").expanduser()
        if name:
            p = p/"{:%y%m}-{}".format(datetime.datetime.now(), name)
            try:
                p.mkdir(parents=True)
            except FileExistsError:
                pass
        execute_disconnected('explorer {}'.format(shellescape(str(p))))
