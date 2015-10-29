import tkinter as t
import sys
import traceback
import os
import queue

from .env import Env
from . import lib

print ("HT GUI !!")

@Env
def show(s, *args):
    print (str(s) % args)


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
            try:
                lib.run_command(s)
                self.cmd.set("")
            except SystemExit:
                raise
            except Exception as e:
                self.on_exception(e)
        self.text['bg']="white"

    def on_exception(self, e):
        raise e

Env.COMMAND_WINDOW = CommandWindow()

def main(args):
    arg_iter = iter(args)
    Env.update(os.environ)
    lib.load_default_modules()
    for a in arg_iter:
        if a == '-s':
            s = next(arg_iter)
            lib.read_config(s)
        elif a == '-x':
            s = next(arg_iter)
            lib.run_command(s)
        else:
            raise ValueError(a)

    Env.COMMAND_WINDOW.mainloop()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
