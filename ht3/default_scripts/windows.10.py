"""Some default commands on Windows."""

from Env import *

from pathlib import Path
import functools

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
            handle = windows.get_window_under_cursor(main=True)
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

    Env['WindowHandle'] = WindowHandle = args.Param(
        convert=_convert_windowhandle,
        complete=_complete_windowhandle,
        doc="Window Handle"
    )

    @Env
    @cmd(name='o')
    def shellexecute(s):
        """Shell Execute, windows's all purpose opening function for files and programms."""
        r = windll.shell32.ShellExecuteW(0, "open", s, None, "", 1)
        if r > 32:
            return None
        else:
            raise OSError("ShellExecute returned an error: %d" % r)

    @cmd(name="%")
    def explore_command(cmd:args.Command):
        """Show the directory or file used in the target commands source in explorer."""

        w = COMMANDS[cmd].function

        strings = []
        if isinstance(w, functools.partial):
            strings = w.args
        else:
            strings = [s for s in w.__code__.co_consts if isinstance(s, str)]

        for s in strings:
            p = Path(s)
            if p.exists():
                if p.is_dir():
                    arg = str(p)
                else:
                    arg = '/select,' + str(p)
                execute_disconnected('explorer', arg)
                return

    if CHECK.frontend('ht3.gui'):
        import ht3.gui
        @ht3.gui.do_on_start
        @Env
        @cmd
        def PlaceOverTaskbar():
            """Find a toolbar named ``hanstool`` and place the command window over it."""
            h = GetTaskBarHandle()
            if h:
                r = GetWindowRect(h)
                ht3.gui.cmd_win_set_rect(*r)
                Env.log("Set window Rect" + repr(r))

        @Env
        @cmd
        def DockInTaskbar():
            """Find a toolbar named ``hanstool`` and place the command window INSIDE it."""
            h = GetTaskBarHandle()
            if not h:
                return
            c = ht3.gui.GUI.cmd_win.window.winfo_id()
            left, top, width, height = GetWindowRect(h)
            ht3.gui.cmd_win_set_rect(0, 0, width, height)

            def to_front(*args):
                ht3.gui.cmd_win_to_front()

            # Hack so after docking, the windows isnt moved arround.
            ht3.gui.GUI.cmd_win.window.bind("<ButtonPress-3>", to_front)
            ht3.gui.GUI.cmd_win.window.bind("<ButtonPress-1>", to_front)
            ht3.gui.GUI.cmd_win.window.bind("<B1-Motion>", lambda *a:None)
            ht3.gui.GUI.cmd_win.window.bind("<B3-Motion>", lambda *a:None)

            SetParent(c, h)

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
