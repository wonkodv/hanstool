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

    def _complete_windowhandle(s):
        @cache_for(5)
        def all_windows():
            l = []
            def cb(handle):
                if IsWindowVisible(handle):
                    l.append(GetClassName(handle))
                    l.append(GetWindowText(handle))
                return True
            EnumWindows(cb)
            yield from iter(sorted(l, key=lambda s:s.lower()))
        return filter_completions_i(s, ("_MOUSE_POS", "_WAIT_FOREGROUND", "_FOREGROUND"), all_windows())

    def _convert_windowhandle(s):
        if s == "_MOUSE_POS":
            handle = get_window_under_cursor(main=True)
        elif s == '_FOREGROUND':
            handle = GetForegroundWindow()
        elif s == '_WAIT_FOREGROUND':
            handle = org = GetForegroundWindow()
            while handle == org:
                sleep(0.1)
                handle = GetForegroundWindow()
        else:
            handle = FindWindow(s)

        if handle:
            return handle
        raise ValueError("No window",s)

    WindowHandle = Env['WindowHandle'] = args.Param(
        convert=_convert_windowhandle,
        complete=_complete_windowhandle,
        doc="Window Handle"
    )

    @Env
    @cmd(name='o')
    def shellexecute(s:args.Union(args.Path,args.Executable)):
        """Shell Execute, windows's all purpose opening function for files and programms."""
        s = str(s)
        r = windll.shell32.ShellExecuteW(0, "open", s, None, "", 1)
        if r > 32:
            return None
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
        @Env
        @cmd
        def PlaceOverTaskbar():
            """Find a toolbar named ``hanstool`` and place the command window over it."""

            @ht3.gui.interact(False)
            def doit(GUI):
                h = GetTaskBarHandle()
                if h:
                    r = GetWindowRect(h)
                    ht3.gui.cmd_win_set_rect(*r)
                    Env.log("Set window Rect" + repr(r))
            doit()

        @Env
        @cmd
        def DockInTaskbar():
            """Find a toolbar named ``hanstool`` and place the command window INSIDE it."""
            @ht3.gui.interact(False)
            def foo(GUI):
                h = GetTaskBarHandle()
                if not h:
                    return
                c = GUI.cmd_win.window.winfo_id()
                left, top, width, height = GetWindowRect(h)
                ht3.gui.cmd_win_set_rect(0, 0, width, height)

                def to_front(*args):
                    ht3.gui.cmd_win_to_front()

                # Hack so after docking, the windows isnt moved arround.
                GUI.cmd_win.window.bind("<ButtonPress-3>", to_front)
                GUI.cmd_win.window.bind("<ButtonPress-1>", to_front)
                GUI.cmd_win.window.bind("<B1-Motion>", lambda *a:None)
                GUI.cmd_win.window.bind("<B3-Motion>", lambda *a:None)

                SetParent(c, h)
            foo()

    @cmd
    def GetCommandLineFromHWND(hwnd:WindowHandle):
        _, procid = GetWindowThreadProcessId(hwnd)
        o = procio("WMIC path win32_process WHERE processid={:d} GET commandline".format(procid),
                errors="backslashreplace",
        )
        lines = [ l for l in o.split("\n") if l ]
        assert lines[0].strip() == 'CommandLine'
        assert len(lines) == 2
        return lines[1]

    def _complete_script_names(s):
        return Env._complete_script_names(s)

    @cmd(apply_default_param_anotations=True)
    def command_from_window(script:_complete_script_names, hwnd:WindowHandle="_MOUSE_POS"):
        cmdline = GetCommandLineFromHWND(hwnd)
        name = GetWindowText(hwnd)
        name = name.lower()
        Env.add_command(script, name=name, text="execute_disconnected(r'{}', is_split=False)".format(cmdline.replace("'", r"\'")))

    @cmd
    def analyze_windows(w:WindowHandle):
        arr = []
        while(w):
            clas = GetClassName(w)
            title = GetWindowText(w)
            rect = GetWindowRect(w)
            arr.append("{0:6X}\t{1:20s}\t'{2:20s}'\t{3: 4} {4: 4} {5: 4} {6: 4}".format(w, clas, title, *rect))
            arr.append("    hwnd=FindWindow(cls={}, title={})\n    SetWindowPos(hwnd, left={}, top={}, width={}, height={})".format(repr(clas), repr(title), *rect))

            w = GetParent(w)
        show("\n".join(arr))

    def get_window_under_cursor(main=False):
        p = get_mouse_pos()
        handle = WindowFromPoint(p)
        if main:
            p = handle
            while p:
                handle = p
                p = GetParent(p)
        return handle

    def device_manager():
        execute_disconnected('mmc devmgmt.msc')
