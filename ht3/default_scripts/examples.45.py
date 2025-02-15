"""Soome example commands and configuration."""

import datetime
import random
import re
import string
import subprocess

from Env import *

if CHECK.frontend("ht3.cli"):
    import ht3.cli

    @ht3.cli.do_on_start
    def import_readline():
        try:
            import readline

            readline.parse_and_bind("set editing-mode vi")
        except ImportError:
            pass


@cmd
def txt():
    """Edit ~/txt."""
    edit_file(expanduser("~/txt"))


@cmd
def timer(t: args.Time, event: str = "Done"):
    """timer timer"""

    t2 = datetime.datetime.now() + datetime.timedelta(seconds=t)
    show(f"Reminding you of {event} at {t2}")

    @threaded(name=f"Timer {event} at {t2}")
    def timer_thread():
        sleep(t)
        option_dialog("Timer", f"Timer up: {event}", "OK")


@cmd
def measure_interval():
    @threaded
    def HotKeyTest():
        with ht3.hotkey.EventHotKey("F7") as hk:
            for t in hk:
                show(f"{hk} {t}")
                if t < 0.2:
                    break


def complete_virtualbox(s=None):
    """Helper function for the vb command, get the names of installed boxes."""
    vms = procio("VBoxManage list vms", shell=False, is_split=False)

    # "debian" {fbc948a5-7b8b-489c-88b0-7f5eaceb150e}
    for s in sorted(vms.split("\n")):
        if s:
            x = s.split('"')
            yield x[1]


@cmd
def vb(box: complete_virtualbox = None):
    """Open VirtualBox (the manager) or start a box with the approximate name."""
    if not box:
        return execute_disconnected("VirtualBox")
    else:
        return procio("VBoxManage", "startvm", box)


@cmd
def rand(low: int = 0, high: int = 0xFFFFFFFF):
    """Copy a random number to the Clipboard."""
    r = random.randint(low, high)
    set_clipboard("0x{:8X}".format(r))
    show(r)


@cmd
def password(
    length: int = 16,
    lower: bool = True,
    upper: bool = True,
    numbers: bool = True,
    common_symbols: bool = True,
    other: bool = False,
):
    ll = set(string.ascii_lowercase)
    ul = set(string.ascii_uppercase)
    no = set(string.digits)
    ss = set("+=-_@%")
    ot = set(string.printable) - ll - ul - no - ss

    pwchars = set()
    if lower:
        pwchars = pwchars | ll
    if upper:
        pwchars = pwchars | ul
    if numbers:
        pwchars = pwchars | no
    if common_symbols:
        pwchars = pwchars | ss
    if other:
        pwchars = pwchars | ot

    for i in range(100):
        pwd = random.sample(pwchars, length)
        if lower:
            if not any(c in ll for c in pwd):
                continue
        if upper:
            if not any(c in ul for c in pwd):
                continue
        if numbers:
            if not any(c in no for c in pwd):
                continue
        if other or common_symbols:
            if not any(c in (ot | ss) for c in pwd):
                continue
        set_clipboard("".join(pwd))
        return
    raise ValueError(
        "can not match all categories", "".join(sorted(pwd)), "".join(sorted(pwchars))
    )



_UNICODE_NAMES = None

def _unicode_names():
    import unicodedata

    global _UNICODE_NAMES
    if not _UNICODE_NAMES:
        l = []
        for c in range(0x20000):  # everything usefull except Chinese/Japanese/Korean
            try:
                l.append(unicodedata.name(chr(c)))
            except ValueError:
                pass
        _UNICODE_NAMES = sorted(l)
    return _UNICODE_NAMES

def _complete_unicode_names(s):
    return filter_completions_i(s, _unicode_names())


@cmd
def unicode(name: _complete_unicode_names):
    import unicodedata

    if len(name) == 1:
        s = name
        name = unicodedata.name(s)
        set_clipboard(name)
    else:
        name = name.upper()
        try:
            s = unicodedata.lookup(name)
        except KeyError as e:
            try:
                name += " SIGN"
                s = unicodedata.lookup(name)
            except KeyError:
                show("\n".join(f"{n} {unicodedata.lookup(n)} {ord(unicodedata.lookup(n))} \\u{ord(unicodedata.lookup(n)):04x}"  for n in _unicode_names() if all(s in n for s in name.split())))
                return
        set_clipboard(s)
    show(f"{name} {s} {ord(s)} \\u{ord(s):04x}")
