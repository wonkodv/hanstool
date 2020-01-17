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
            e = ctypes.WinError()
            e.filename = s
            raise e

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
        def MoveHtWindow():
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

        ht3.gui.cmd_win_hide_frame()


    @cmd(apply_default_param_anotations=True)
    def get_command_line_from_wnd(wnd:Window="_MOUSE_POS_MAIN"):
        show(command_line_from_wnd(wnd))

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
    def command_from_window(script:_complete_script_names, name=None, wnd:Window="_MOUSE_POS_MAIN"):
        cmdline = command_line_from_wnd(wnd)
        if name is None:
            name = wnd.title
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

    @cmd
    def device_manager():
        execute_disconnected('mmc devmgmt.msc')

    @cmd(attrs={'HotKey':'F7'})
    def private():
        """Hide a Window (Firefox-Private Browsing) while someone looks over your Shoulder"""

        w = Window.TOP.search_by_title(r"Firefox \(Private Browsing\)$")
        log(w)
        if w:
            if w.visible:
                if w == Window.get_foreground_window():
                    fake("ALT+TAB")
                w.hide()
            else:
                w.show()
                w.to_front()
#        else:
#            execute_disconnected("C:/Program Files/Mozilla Firefox/Firefox.exe", "-private")

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

    @Env
    def get_uptime():
        uptime = GetTickCount()
        boottime = format(datetime.datetime.now()-uptime, "%H:%M")
        uptime = str(uptime).partition('.')[0]
        return boottime, uptime


    @Env.updateable
    def tna_text():
        """Text to overwrite on the TNA.

        Multiline Text needs a thicker Taskbar to work.
        """
        boot_time, up_time = get_uptime()
        now = datetime.datetime.now()
        return (
            f"{now:%H:%M} KW{now:%V}\n"
            f"{now:%Y-%m-%d}\n"
            f"Boot {boot_time}"
        )

    @cmd
    def tna_text_updater():
        """ Overwrite the text in the Clock of the TNA with `tna_text()`.

        Wind the Clock Window on the TaskBar and draw over it every full minute
        """
        @threaded
        def tna_updater_thread():
            Env['tna_updater_thread'] = threading.current_thread()
            while Env['tna_updater_thread'] is threading.current_thread():
                w = Window.TOP.find(class_name='Shell_TrayWnd').find(class_name='TrayNotifyWnd').find(class_name='TrayClockWClass')
                dc = ctypes.windll.user32.GetDC(w.hwnd)

                text = tna_text()
                ctypes.windll.gdi32.SetBkColor(dc, 0xC8D0D4)
                y = 0

                for i in range(10):
                    for i,s in enumerate(text.split("\n")):
                        ctypes.windll.gdi32.TextOutW(dc, 3, 16*i,  s, len(s))
                    sleep(0.1) # Draw again in case the  Clock Window redraw happend late

                ctypes.windll.user32.ReleaseDC(w.hwnd, dc)

                now = datetime.datetime.now()
                sleep(60-now.second) # update on the full minute

    @cmd
    def tna_text_updater_stop():
            Env['tna_updater_thread'] = None
