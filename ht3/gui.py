import tkinter as t
import sys
import traceback
import os
import queue
import threading

from . import lib
from .lib import Env

class CommandWindow(t.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.cmd = t.StringVar()
        self.text = t.Entry(self, textvariable=self.cmd)
        self.text.pack()

        self.geometry("100x20")
        self.geometry("+100+20")
        self.text.bind("<KeyPress-Tab>",self.on_tab)
        self.text.bind("<KeyPress-Return>",self.on_enter)

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

    def on_tab(self, event):
        pass

    def on_enter(self, event):
        self.text['bg']="red"
        s = self.cmd.get()
        if s:
            lib.run_command(s)
            self.cmd.set("")
        self.text['bg']="white"

    def check_closed(self):
        if self.closed_evt.is_set():
            self.quit()
        else:
            self.after(100, self.check_closed)

    def to_front(self):
        self.text.focus_force()
        self.text.select_range(0, len(self.cmd.get()))

# Frontend API

def loop():
    try:
        lib.Env.COMMAND_WINDOW = CommandWindow()
        lib.Env.COMMAND_WINDOW.mainloop()
    finally:
        lib.Env.COMMAND_WINDOW = None

def stop():
    if not lib.Env.COMMAND_WINDOW is None:
        lib.Env.COMMAND_WINDOW.closed_evt.set()


# Mandatory User API
# TODO: These all print on stdout. Make them use windows

@Env
def show(s, *args, **kwargs):
    print (str(s) % args)

@Env
def log(s, *args, **kwargs):
    print (str(s) % args)

@Env
def edit_file(path, line):
    execute(EDITOR, f)

Env.help = help

# Extended User API

@Env
def show_input_window():
    Env.COMMAND_WINDOW.to_front()

if __name__ == '__main__':
    loop()
