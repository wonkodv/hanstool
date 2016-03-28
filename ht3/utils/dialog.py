import tkinter as tk

__all__ = ('option_dialog', )

class OptionDialog(tk.Tk):
    def __init__(self, title, message, def_option, *more_options, timeout=0):
        super().__init__()
        self.title(title)
        self.result = None
        self.timeout = timeout

        tk.Label(self, text=message).pack()
        self.buttons = tk.Frame(self)

        self.bind("<Escape>", self.cancel)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.default = def_option
        b = self.default_button = self._option(def_option)
        b.default = tk.ACTIVE
        b.focus_force()
        for o in more_options:
            self._option(o)

        self.buttons.pack(padx=5, pady=5)

        if timeout > 0:
            self._timer()
        else:
            self._job = None


    def _option(self, o):
        b = tk.Button(self.buttons, text=str(o), width=10, command=lambda:self._select(o))
        b.pack(side=tk.LEFT, padx=5, pady=5)
        return b

    def _select(self, r):
        self.result = r
        self.cancel()

    def _timer(self):
        if self.timeout <= 0:
            self._select(self.default)
        else:
            self.timeout = self.timeout - 1
            self.default_button.config(
                text="{0:s} ({1:d})".format(
                    self.default, self.timeout))
            self._job = self.after(1000, self._timer)

    def cancel(self, evt=None):
        if self._job:
            self.after_cancel(self._job)
        self.destroy()

def option_dialog(title, message, *options, timeout=0):
    od = OptionDialog(title, message, *options, timeout=timeout)
    od.wait_window(od)
    return od.result


if __name__ == '__main__':
    print(
        option_dialog("Title", "Message", "Option 0", "Option 1", 42, timeout=4),
        option_dialog("Title", "Message", "Ok")
    )
