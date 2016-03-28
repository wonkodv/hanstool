"""The Graphical user interface.

Has a small window where you enter Text
and a larger one that will be mostly hidden wher log messages appear.
"""

import inspect
import itertools
import os.path
import pathlib
import pprint
import threading
import tkinter as tk
import traceback

from . import lib
from .env import Env
from .command import run_command
from .check import CHECK

GUI = None


__all__ = (
    'cmd_win_set_rect',
    'cmd_win_stay_on_top',
    'cmd_win_to_front',
    'gui_do_on_start',
    'help',
    'log',
    'log_command',
    'log_command_finished',
    'log_error',
    'log_subprocess',
    'log_subprocess_finished',
    'log_thread',
    'log_thread_finished',
    'log_win_to_front',
    'show',
)

class UserInterface():
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.title("root")
        self.log_win = self.MessageWindow(self)
        self.cmd_win = self.CommandWindow(self)
        self.root.after(100, self.cmd_win.to_front)

    def loop(self):
        self.closed_evt = threading.Event()
        self.root.after(100, self.check_closed)
        self.root.mainloop()

    def check_closed(self):
        if self.closed_evt.is_set():
            self.root.quit()
        else:
            self.root.after(100, self.check_closed)

    def close_soon(self):
        self.closed_evt.set()

    def run_command(self, string):
        if string:
            self.cmd_win.set_state("Working")
            try:
                run_command(string)
            except Exception as e:
                self.cmd_win.set_state("Error")
                log_error(e)
                return False
            else:
                self.cmd_win.set_state("Waiting")
                return True
        else:
            self.cmd_win.set_state("Waiting")
            return False

    class CommandWindow():
        def __init__(self, ui):
            self.ui = ui
            self.window = ui.root
            self.master = ui.root
            #self.window=tk.Toplevel(self.master)
            self.window.title("Command Window")
            self.window.overrideredirect(True)
            self.window.geometry("100x20+100+20")

            self.window.bind("<ButtonPress-3>",self._start_resize_move)
            self.window.bind("<ButtonPress-1>",self._start_resize_move)
            self.window.bind("<B1-Motion>",self._move)
            self.window.bind("<B3-Motion>",self._resize)

            self.window.bind("<Double-Button-1>", self._toggle_log)

            self.cmd = tk.StringVar()
            self.text = tk.Entry(self.window, textvariable=self.cmd)
            self.text.pack(fill='both', expand=1)
            self.text.bind("<KeyPress-Return>",self._submit)
            self.text.bind("<Control-KeyPress-W>", self._delete_word) #TODO
            self.text.bind("<Control-KeyPress-U>", self._delete_text) #TODO
            self.text.bind("<KeyPress-Escape>", self._delete_text)

            self._completion_cache = None
            self._completion_iter = None
            self._completion_index = None
            self._uncompleted_string  = None
            self._completion_update = False
            self.cmd.trace("w",lambda *args: (self._clear_completion(),self._clear_history()))
            self.text.bind("<KeyPress-Tab>",lambda e: self._set_completion(1))
            self.text.bind("<Shift-KeyPress-Tab>",lambda e: self._set_completion(-1))

            self._load_history()
            self._history_update = False
            self.text.bind("<KeyPress-Up>",lambda e: self._set_history(1))
            self.text.bind("<KeyPress-Down>",lambda e: self._set_history(-1))

            self._state = "Waiting"
            self._has_focus = False
            self._update_color()
            self.window.bind("<FocusIn>", lambda e:self._set_focus(True))
            self.window.bind("<FocusOut>", lambda e:self._set_focus(False))

        def _set_focus(self, f):
            self._has_focus = f
            self._update_color()

        def _update_color(self):
            if self._state == 'Waiting':
                if self._has_focus:
                    self.text['bg'] = 'white'
                else:
                    self.text['bg'] = '#D4D0C8'
            elif self._state == 'Working':
                self.text['bg'] = 'red'
            elif self._state == 'Error':
                self.text['bg'] = 'orange'
            else:
                assert False
            self.master.update_idletasks()

        def set_state(self, state):
            self._state = state
            self._update_color()

        def to_front(self):
            self.window.deiconify()
            self.text.focus_force()
            self.text.select_range(0, 'end')

        def stay_on_top(self):
            self.window.wm_attributes('-topmost', 1)

        def set_rect(self, left, top, width, height):
            self.window.geometry("%dx%d+%d+%d" % (width, height, left, top))

        def _toggle_log(self, event):
            self.ui.log_win.toggle()

        def _start_resize_move(self, event):
            self.x = event.x
            self.y = event.y

        def _move(self, event):
            x = self.window.winfo_x() + event.x - self.x
            y = self.window.winfo_y() + event.y - self.y
            self.window.geometry("+%s+%s" % (x, y))

        def _resize(self, event):
            x = self.window.winfo_width() + event.x - self.x
            y = self.window.winfo_height() + event.y - self.y
            self.x = event.x
            self.y = event.y
            if x>10 and y>10:
                self.window.geometry("%sx%s" % (x, y))

        def _clear_completion(self):
            if not self._completion_update:
                self._completion_cache = None
                self._completion_iter = None


        def _set_completion(self, i):
            # index 0: original
            # index < 0 is wrapped in line 198
            # index > 0: used to access cache[index-1]
            if self._completion_cache is None:
                s = self.cmd.get()
                self._completion_cache = []
                c = Env.general_completion(s)
                self._completion_iter = iter(c)
                self._completion_index = i
                self._uncompleted_string = s
            else:
                self._completion_index += i

            if self._completion_index < 0:
                self._completion_cache.extend(self._completion_iter)
                try:
                    self._completion_index = self._completion_index % (
                         len(self._completion_cache) + 1)
                except ZeroDivisionError:
                    self._completion_index = 0
            else:
                try:
                    while self._completion_index > len(self._completion_cache):
                        nc = next(self._completion_iter)
                        self._completion_cache.append(nc)
                except StopIteration:
                    self._completion_index = 0

            if self._completion_index == 0:
                ct = self._uncompleted_string
            else:
                assert self._completion_index >= 1
                ct = self._completion_cache[self._completion_index-1]

            self._completion_update = True
            self._set_text(ct)
            self._completion_update = False

        def _load_history(self):
            h = os.path.expanduser(Env.get('GUI_HISTORY', '~/.config/guihistory'))
            self._history_file = h
            if os.path.exists(h):
                with open(h, 'rt') as f:
                    self._history = [s.strip() for s in f]
            else:
                self._history = []
            self._history_index = -1

        def _set_history(self, i):
            h = self._history_index + i
            if self._history_index == -1:
                self._history_active = self.cmd.get()
            if  h >= len(self._history):
                return
            if h < 0:
                s = self._history_active
                self._history_index = -1
            else:
                self._history_index = h

                s = self._history[-1-h]

            self._history_update = True
            self._set_text(s)
            self._history_update = False

        def _clear_history(self):
            if not self._history_update:
                self._history_index = -1

        def _set_text(self, text):
            self.text.delete(0, tk.END)
            self.text.insert(0, text)
            def sel():
                self.text.selection_clear()
                self.text.xview(len(text)-1)
            self.window.after(0, sel)

        def _delete_word(self, event):
            pass

        def _delete_text(self, event):
            self._set_text("")

        def _submit(self, event):
            s = self.cmd.get()
            if self.ui.run_command(s):
                self._set_text('')
            self._history.append(s)
            self._history_index = -1
            with open(self._history_file, 'at') as f:
                f.write(s+"\n")


    class MessageWindow():
        def __init__(self, ui):
            self.ui = ui
            self.master = ui.root
            self.window = tk.Toplevel(self.master)
            self.window.title("Log")
            self.text=tk.Text(self.window)
            self.scrollbar = tk.Scrollbar(self.window)
            self.scrollbar.pack(side='right',fill='y')
            self.text.pack(fill='both', expand=1)
            self.text.config(yscrollcommand=self.scrollbar.set)
            self.scrollbar.config(command=self.text.yview)

            self.window.protocol('WM_DELETE_WINDOW', self.hide)
            self.visible = False
            self.window.withdraw()

            self.window.bind('<KeyPress-Escape>', lambda e: self.hide())

        def toggle(self):
            if not self.visible:
                self.to_front()
            else:
                self.hide()

        def to_front(self):
            self.visible = True
            self.window.deiconify()
            self.window.focus_set()

        def hide(self):
            self.visible = False
            self.window.withdraw()
            self.ui.cmd_win.to_front()

        def log(self, msg, current_command=None, frontend=None):
            assert isinstance(msg, str)
            self.text.insert('end', msg+'\n')
            self.text.yview('end')


        def log_show(self, o, current_command=None, frontend=None):
            if isinstance(o, str):
                pass
            elif isinstance(o, bool):
                o = str(o)
            elif isinstance(o, int):
                o = "0b{0:b}\t0x{0:X}\t{0:d}".format(o)
            elif inspect.isfunction(o):
                s, l = inspect.getsourcelines(o)
                o = "".join("{0:>6d} {1}".format(n,s) for (n,s) in zip(itertools.count(l),s))
            else:
                o = pprint.pformat(o)
            self.log(o)
            self.to_front()

        def log_command(self, cmd, current_command=None, frontend=None):
            i, c, p = current_command
            self.log("Command %d from %s: %s" % (i, frontend, cmd))

        def log_command_finished(self, result, current_command=None, frontend=None):
            if result is None:
                if not Env.get('DEBUG', False):
                    return
            i, c, p = current_command
            self.log("Result %d: %s" % (i, pprint.pformat(result)))

        def log_error(self, e, current_command=None, frontend=None):
            t = type(e)
            tb = e.__traceback__
            self.log("".join(traceback.format_exception(t, e, tb)))
            self.to_front()

        def log_subprocess(self, p, current_command=None, frontend=None):
            self.log("Spawned process %d: %r" % (p.pid, p.args))

        def log_subprocess_finished(self, p, current_command=None, frontend=None):
            a = p.args
            if not isinstance(a, str):
                a = a[0]
            a = pathlib.Path(a)
            a = a.with_suffix('')
            a = a.name
            self.log("Process finished %d (%s): %r" % (p.pid, a, p.returncode))
            if p.returncode > 0:
                if CHECK.os.win:
                    if not getattr(p, 'shell', False): # shell is set explicitly by the shell function
                        # Dont raise log for non-shell
                        return
                self.to_front()

        def log_thread(self, t, current_command=None, frontend=None):
            self.log("Spawned thread %d: %s" % (t.ident, t.name))

        def log_thread_finished(self, result, current_command=None, frontend=None):
            i, c, p = current_command
            self.log("ThreadResult %d: %r" % (i, result))


# Frontend API

_stored_log=[]

def start():
    pass

def loop():
    global GUI
    try:
        GUI = UserInterface()

        for m, a, k in _stored_log:
            l = getattr(GUI.log_win, m)
            l(*a, **k)
        _stored_log.clear()

        for c in _do_on_start:
            c()

        GUI.loop()
    finally:
        GUI = None

def stop():
    if GUI is not None:
        GUI.close_soon()

def _reptor_tk_ex(self, typ, val, tb):
    log_error(val)

tk.Tk.report_callback_exception = _reptor_tk_ex

#logging

def _do_log(m, *args):
    tls = lib.THREAD_LOCAL
    cc = getattr(tls,'command',None)
    cf = getattr(tls,'frontend',None)
    if GUI:
        l = getattr(GUI.log_win, m)
        l(*args, current_command=cc, frontend=cf)
    else:
        _stored_log.append( [ m, args, { 'current_command': cc, 'frontend': cf } ])

def show(o):
    _do_log('log_show', o)

def log_command(cmd):
    _do_log('log_command', cmd)

def log_command_finished(result):
    _do_log('log_command_finished', result)

def log_error(e):
    _do_log('log_error', e)
    if  not GUI:
        from ht3.utils.log import log_error
        log_error(e)

def log(s):
    _do_log('log', s)


def log_subprocess(p):
    _do_log('log_subprocess', p)

def log_subprocess_finished(p):
    _do_log('log_subprocess_finished', p)

def log_thread(t):
    _do_log('log_thread', t)

def log_thread_finished(result):
    _do_log('log_thread_finished', result)

def help(obj):
    import pydoc
    show(pydoc.plain(pydoc.render_doc(obj, title='Help on %s')))


# Extended User API

_do_on_start = []
def gui_do_on_start(f):
    assert callable(f)
    _do_on_start.append(f)
    return f

def cmd_win_stay_on_top():
    GUI.cmd_win.stay_on_top()

def cmd_win_to_front():
    GUI.cmd_win.to_front()

def log_win_to_front():
    GUI.log_win.to_front()

def cmd_win_set_rect(left, top, width, height):
    GUI.cmd_win.set_rect(left, top, width, height)

if __name__ == '__main__':
    loop()
