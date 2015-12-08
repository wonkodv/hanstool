if not Check.os.win:
    raise NotImplementedError()

@cmd(name='o', args=1)
def shellexecute(s):
    """ Shell Execute, windows's all purpose opening function for files and programms """
    from ctypes import windll
    r = windll.shell32.ShellExecuteW(0, "open", s, None, "", 1)
    if r > 32:
        return None
    else:
        raise OSError("ShellExecute returned an error: %d" % r)

@cmd(args="1", complete=complete_command, name="#")
def explore_command(cmd):
    """ Show the directory or file used in the target commands source in explorer"""
    from pathlib import Path
    import functools

    w = COMMANDS[cmd].__wrapped__

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
                    execute("explorer",str(p))
                else:
                    shell('explorer /select,"'+str(p)+'"')
                return
    except:
        pass

if Check.frontend('ht3.gui'):
    @ht3.gui.do_on_start
    def _place_cmd_win_over_taskbar_toolbar():
        h = GetTaskBarHandle()
        r = GetWindowRect(h)
        ht3.gui.cmd_win_set_rect(*r)

    @Env
    def DockInTaskbar():
        c = ht3.gui.GUI.cmd_win.window.winfo_id()
        h = GetTaskBarHandle()
        left, top, width, height = GetWindowRect(h)
        ht3.gui.cmd_win_set_rect(0, 0, width, height)

        def to_front(*args):
            ht3.gui.cmd_win_to_front()

        # Hack because after Docking, The mouse click activation doesn't work
        ht3.gui.GUI.cmd_win.window.bind("<ButtonPress-3>", to_front)
        ht3.gui.GUI.cmd_win.window.bind("<ButtonPress-1>", to_front)
        ht3.gui.GUI.cmd_win.window.bind("<B1-Motion>", lambda *a:None)
        ht3.gui.GUI.cmd_win.window.bind("<B3-Motion>", lambda *a:None)

        SetParent(c, h)

