if not Check.os.win:
    raise NotImplementedError()


@cmd(name='o', args=1)
def shellexecute(s):
    """ Shell Execute, windows's all purpose opening function for files and programms """
    from ctypes import windll
    windll.shell32.ShellExecuteW(0, "open", s, None, "", 1)

@cmd(args=COMMANDS, name="#")
def explore_command(cmd):
    """ Show the directory or file used in the target commands source in explorer"""
    from pathlib import Path
    for c in cmd.__wrapped__.__code__.consts:
        if isinstance(str, c):
            try:
                p = Path(c)
                if p.exists():
                    if not p.is_dir():
                        p = p.parent
                    execute("explorer","/select"+str(p))
            except:
                pass

if Check.frontend('ht3.gui'):
    @ht3.gui.do_on_start
    def _():
        h = GetTaskBarHandle()
        r = GetWindowRect(h)
        show(r)
        ht3.gui.cmd_win_set_rect(*r)



if Check.frontend('ht3.gui'):
    @Env
    def DockInTaskbar():
        c = ht3.gui.GUI.cmd_win.window.winfo_id()
        h = GetTaskBarHandle()
        left, top, width, height = GetWindowRect(h)
        ht3.gui.cmd_win_set_rect(0, 0, width, height)
        SetParent(c, h)
