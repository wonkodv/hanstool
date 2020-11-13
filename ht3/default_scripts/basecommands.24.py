"""Useful commands"""

from Env import *

import re
import itertools
import threading
import time
import os


def _complete_fake(string):
    parts = re.split("[^A-Za-z0-9_]+", string)
    if len(parts) > 0:
        p = parts[-1]
    else:
        p = ""

    prefix = string[: len(string) - len(p)]
    values = filter_completions_i(p, ht3.utils.fake_input.KEY_CODES)
    values = sorted(values)
    values = (prefix + x for x in values)
    return values


@cmd(name=":")
def test_fake(s: _complete_fake):
    """Test a fake-sequence after 500 ms."""
    sleep(0.5)
    fake(s, restore_mouse_pos=True)
    global FAKE_TEXT
    FAKE_TEXT = s


@cmd
def record_fake_mouse():
    """Compile a Fake-script of mouse locations

    record mouse position every time you press F9,
    until you press F9 twice in a quarter second.
    """

    s = []
    with ht3.hotkey.EventHotKey("F9") as hk:
        for t in hk:
            if t < 0.25:
                break
            mp = get_mouse_pos()
            s.append("{}/{}".format(*mp))
    s = ": " + " ".join(s)
    show(s)


@cmd(attrs=dict(HotKey="F10"))
def repeat_fake():
    """Repeat the fake-sequence last tested."""
    global FAKE_TEXT
    fake(FAKE_TEXT)


Env["__"] = []
Env["_"] = None


# Some Eval Python functions
@cmd(name="=")
def _show_eval(s: args.Python = ""):
    """ Evaluate a python expression and show the result """
    r = evaluate_py_expression(s.lstrip())
    if inspect.isgenerator(r):
        r = list(itertools.islice(r, 1000))
    show(r)
    Env["__"].append(r)
    Env["_"] = r
    return r


@cmd(name=";")
def _execute_py_expression(s: args.Python):
    """Execute a python statement."""
    execute_py_expression(s.lstrip())


class PythonFallback(ht3.command.Command):
    def __init__(self, command_string):
        """Evaluate or executed as python."""

        super().__init__(command_string)
        try:
            self.c = compile(command_string, "<input>", "eval")
            self.show = True
        except SyntaxError:
            self.c = compile(command_string, "<input>", "exec")
            self.show = False

    def run(self):
        r = eval(self.c, {}, Env.dict)
        if self.show:
            show(r)
            Env["__"].append(r)
            Env["_"] = r

    @COMMAND_NOT_FOUND_HOOK.register
    def _hook(command_string):
        try:
            return PythonFallback(command_string)
        except SyntaxError:
            pass


@cmd
def cd(p: Path):
    os.chdir(p)
