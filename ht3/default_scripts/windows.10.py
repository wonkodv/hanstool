"""Some default commands on Windows."""
if CHECK.os.win:

    @cmd(name='o', args=1)
    def shellexecute(s):
        """Shell Execute, windows's all purpose opening function for files and programms."""
        from ctypes import windll
        r = windll.shell32.ShellExecuteW(0, "open", s, None, "", 1)
        if r > 32:
            return None
        else:
            raise OSError("ShellExecute returned an error: %d" % r)

    @cmd(args="1", complete=complete_command, name="#")
    def explore_command(cmd):
        """Show the directory or file used in the target commands source in explorer."""
        from pathlib import Path
        import functools

        w = COMMANDS[cmd].function

        strings = []
        if isinstance(w, functools.partial):
            strings = w.args
        else:
            strings = [s for s in w.__code__.co_consts if isinstance(s, str)]
        try:
            for s in strings:
                p = Path(s)
                if p.exists():
                    if p.is_dir():
                        arg = str(p)
                    else:
                        arg = '/select,' + str(p)
                    execute(r'explorer', arg)
                    return
        except:
            pass

    if CHECK.frontend('ht3.gui'):
        @gui_do_on_start
        def _place_cmd_win_over_taskbar_toolbar():
            """Find a toolbar named ``hanstool`` and place the command window over it."""
            h = GetTaskBarHandle()
            if h:
                r = GetWindowRect(h)
                ht3.gui.cmd_win_set_rect(*r)

        @Env
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
    def analyze_windows():

        arr = []

        p = get_mouse_pos()
        w = WindowFromPoint(p)

        while(w):
            clas = GetClassName(w)
            title = GetWindowText(w)
            rect = GetWindowRect(w)

            arr.append("{0:X}\t{1:20s}\t'{2}'\n\t{3: 4} {4: 4} {5: 4} {6: 4})".format(w, clas, title, *rect))

            w = GetParent(w)
        show(str(p) + "\n" + "\n".join(arr))
