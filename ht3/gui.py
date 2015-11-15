import tkinter as tk
import sys
import traceback
import os
import queue
import threading

from . import lib
from .lib import Env

COMMAND_WINDOW = None

class CommandWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.cmd = tk.StringVar()
        self.text = tk.Entry(self, textvariable=self.cmd)
        self.text.pack()

        self.geometry("100x20")
        self.geometry("+100+20")
        self.text.bind("<KeyPress-Tab>",self.on_tab)
        self.text.bind("<Shift-KeyPress-Tab>",self.on_shift_tab)
        self.text.bind("<KeyPress-Return>",self.on_submit)
        self.text.bind("<Control-KeyPress-W>", self.delete_word) #TODO
        self.text.bind("<Control-KeyPress-U>", self.delete_text) #TODO
        self.text.bind("<KeyPress-Escape>", self.delete_text)

        self.cmd.trace("w",lambda *args: self.clear_completion())

        self.bind("<ButtonPress-3>",self.on_mousedown)
        self.bind("<ButtonPress-1>",self.on_mousedown)
        self.bind("<B1-Motion>",self.on_move)
        self.bind("<B3-Motion>",self.on_resize)

        self.closed_evt = threading.Event()
        self.after(100, self.check_closed)

    def on_mousedown(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        self.geometry("+%s+%s" % (deltax, deltay))

    def on_resize(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("%sx%s" % (x, y))
        self.text.pack()

    completion_cache = None
    completion_index = None
    uncompleted_string  = None

    def clear_completion(self):
        self.completion_cache = None


    def set_completion(self, i):
        if self.completion_cache is None:
            print ("Redo Completion")
            s = self.cmd.get()
            self.completion_cache = lib.get_all_completions(s)
            self.completion_index = 0
            self.uncompleted_string = s
        else:
            self.completion_index += i

        cc = self.completion_cache

        if 0 <= self.completion_index < len(self.completion_cache):
            s = self.cmd.get()
            ct = self.completion_cache[self.completion_index]
        else:
            self.completion_index = -1
            ct = self.uncompleted_string
        self.set_text(ct)

        self.completion_cache = cc # TODO: remove this HACK line by
            # TODO making clear_completion only trigger on user input that modifies text.


    def set_text(self, text):
        self.text.delete(0, tk.END)
        self.text.insert(0, text)
        def sel():
            self.text.selection_clear()
            self.text.xview(len(text)-1)
        self.after(0, sel)

    def delete_word(self, event):
        pass

    def delete_text(self, event):
        self.set_text("")

    def on_tab(self, event):
        self.set_completion(1)

    def on_shift_tab(self, event):
        self.set_completion(-1)

    def on_submit(self, event):
        self.text['bg']="red"
        s = self.cmd.get()
        if s:
            try:
                result = lib.run_command(s)
            except Exception as e:
                self.text['bg']="orange"
                e = traceback.format_exc()
                Env.log("Error %s: %s", s, e)
            else:
                if result is not None:
                    Env.log("Cmd %s: %r", s, result)
                else:
                    Env.log("Cmd %s", s)
                self.set_text("")
                self.text['bg']="white"

    def check_closed(self):
        if self.closed_evt.is_set():
            self.quit()
        else:
            self.after(100, self.check_closed)

    def close_soon(self):
        self.closed_evt.set()

    def to_front(self):
        self.text.focus_force()
        self.text.select_range(0, len(self.cmd.get()))

# Frontend API

def loop():
    global COMMAND_WINDOW
    try:
        COMMAND_WINDOW = CommandWindow()
        for c in _do_on_start:
            c()
        COMMAND_WINDOW.mainloop()
    finally:
        COMMAND_WINDOW = None

def stop():
    if not COMMAND_WINDOW is None:
        COMMAND_WINDOW.close_soon()


# Mandatory User API
# TODO: These all print on stdout. Make them use windows

@Env
def show(s, *args, **kwargs):
    print (str(s) % args)

@Env
def log(s, *args, **kwargs):
    print (str(s) % args)

Env.help = help

# Extended User API

_do_on_start = []
def do_on_start(f):
    assert callable(f)
    _do_on_start.append(f)
    return f

def show():
    COMMAND_WINDOW.to_front()

def stay_on_top():
    COMMAND_WINDOW.wm_attributes('-topmost', 1)

def set_rect(left, top, width, height):
    COMMAND_WINDOW.geometry("%dx%d+%d+%d" % (width, height, left, top))

if __name__ == '__main__':
    loop()
