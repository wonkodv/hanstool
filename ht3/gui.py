import tkinter as tk
import sys
import traceback
import os
import queue
import threading

from . import lib
from .env import Env
from .command import run_command
from .complete import complete_all

GUI = None


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
            self.cmd_win._set_state("Working")
            try:
                result = run_command(string)
            except Exception as e:
                self.cmd_win._set_state("Error")
                log_error(e)
                return string
            else:
                self.cmd_win._set_state("Waiting")
                return ""
        else:
            self.cmd_win._set_state("Waiting")
            return string

    class CommandWindow():
        def __init__(self, ui):
            self.ui = ui
            self.window = ui.root
            self.master = ui.root
            #self.window=tk.Toplevel(self.master)
            self.window.title("Command Window")
            self.window.overrideredirect(True)
            self.window.geometry("100x20+100+20")

            self.cmd = tk.StringVar()
            self.text = tk.Entry(self.window, textvariable=self.cmd)
            self.text.pack(fill='both', expand=1)

            self.text.bind("<KeyPress-Tab>",lambda e: self._set_completion(1))
            self.text.bind("<Shift-KeyPress-Tab>",lambda e: self._set_completion(-1))
            self.text.bind("<KeyPress-Return>",self._submit)
            self.text.bind("<Control-KeyPress-W>", self._delete_word) #TODO
            self.text.bind("<Control-KeyPress-U>", self._delete_text) #TODO
            self.text.bind("<KeyPress-Escape>", self._delete_text)
            self.cmd.trace("w",lambda *args: self._clear_completion())

            self.window.bind("<ButtonPress-3>",self._start_resize_move)
            self.window.bind("<ButtonPress-1>",self._start_resize_move)
            self.window.bind("<B1-Motion>",self._move)
            self.window.bind("<B3-Motion>",self._resize)

            self.window.bind("<Double-Button-1>", self._toggle_log)

            self.window.bind("<FocusIn>", lambda e:self._set_focus(True))
            self.window.bind("<FocusOut>", lambda e:self._set_focus(False))

            self._completion_cache = None
            self._completion_index = None
            self._uncompleted_string  = None
            self._completion_update = False

            self._state = "Waiting"
            self._has_focus = False
            self._update_color()

        def _set_focus(self, f):
            self._has_focus = f
            self._update_color()

        def _set_state(self, state):
            self._state = state
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


        def _set_completion(self, i):
            if self._completion_cache is None:
                s = self.cmd.get()
                self._completion_cache = complete_all(s)
                self._completion_index = 0
                self._uncompleted_string = s
            else:
                self._completion_index += i

            cc = self._completion_cache

            if 0 <= self._completion_index < len(self._completion_cache):
                s = self.cmd.get()
                ct = self._completion_cache[self._completion_index]
            else:
                self._completion_index = -1
                ct = self._uncompleted_string

            self._completion_update = True
            self._set_text(ct)
            self._completion_update = False

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
            s = self.ui.run_command(s)
            self._set_text(s)


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

        def log(self, msg):
            assert isinstance(msg, str)
            self.text.insert('end', msg+'\n')
            self.text.yview('end')

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


        def log_show(self, o):
            self.log(str(o))
            self.to_front()

        def log_command(self, cmd):
            i, c, p = lib.THREAD_LOCAL.command
            f = lib.THREAD_LOCAL.frontend
            self.log("Command %d from %s: %s" % (i, f, cmd))

        def log_command_finished(self, result):
            if result is None:
                if not Env.get('DEBUG', False):
                    return
            i, c, p = lib.THREAD_LOCAL.command
            self.log("Result %d: %r" % (i, result))

        def log_error(self, e):
            self.log(traceback.format_exc())
            self.to_front()

        def log_subprocess(self, p):
            self.log("Spawned process %d: %r" % (p.pid, p.args))

        def log_thread(self, t):
            self.log("Spawned thread %d: %s" % (t.ident, t.name))

        def log_thread_finished(self, result):
            i, c, p = lib.THREAD_LOCAL.command
            self.log("ThreadResult %d: %r" % (i, result))

# Frontend API

_stored_log=[]

def loop():
    global GUI
    try:
        GUI = UserInterface()

        for m, a in _stored_log:
            _do_log(m, *a)
        _stored_log.clear()

        for c in _do_on_start:
            c()

        GUI.loop()
    finally:
        GUI = None

def stop():
    if not GUI is None:
        GUI.close_soon()

#logging

def _do_log(m, *args):
    if GUI:
        getattr(GUI.log_win, m)(*args)
    else:
        _stored_log.append([m, args])

@Env
def show(o):
    _do_log('log_show', o)

@Env
def log_command(cmd):
    _do_log('log_command', cmd)

@Env
def log_command_finished(result):
    _do_log('log_command_finished', result)

@Env
def log_error(e):
    if GUI:
        _do_log('log_error', e)
    else:
        raise e
    print(traceback.format_exc())

@Env
def log(s):
    _do_log('log', s)


@Env
def log_subprocess(p):
    _do_log('log_subprocess', p)

@Env
def log_thread(t):
    _do_log('log_thread', t)

@Env
def log_thread_finished(result):
    _do_log('log_thread_finished', result)

@Env
def help(obj):
    show(obj.__doc__)


# Extended User API

_do_on_start = []
def do_on_start(f):
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
