"""Fake Input for the X11."""

import functools
import time

import Xlib.display
import Xlib.ext.xtest
import Xlib.protocol.event
import Xlib.X
import Xlib.XK
from ht3.utils.keycodes.xserver import KEY_CODES

get_mouse_pos = None
mouse_move = None
mouse_down = None
mouse_up = None
mouse_wheel = None


@functools.lru_cache(1)
def display():
    return Xlib.display.Display()


def key_down(vk):
    if isinstance(vk, str):
        vk = KEY_CODES[vk.upper()]
    Xlib.ext.xtest.fake_input(display(), Xlib.X.KeyPress, vk)
    display().sync()


def key_up(vk):
    if isinstance(vk, str):
        vk = KEY_CODES[vk.upper()]
    Xlib.ext.xtest.fake_input(display(), Xlib.X.KeyRelease, vk)
    display().sync()


def type_string(s, interval=0):
    if interval:
        interval = float(interval) / 1000

        def i():
            time.sleep(interval)

    else:

        def i():
            pass

    for c in s:
        sym = Xlib.XK.string_to_keysym(c)
        if sym:
            shifted = c.isupper()
            kc = display().keysym_to_keycode(sym)
            if shifted:
                key_down("SHIFT")
            key_down(kc)
            key_up(kc)
            if shifted:
                key_up("SHIFT")
        else:
            key_down("CONTROL")
            key_down("SHIFT")
            key_down("U")
            key_up("U")
            key_up("SHIFT")
            key_up("CONTROL")

            u = ord(c)
            u = format(u, "04X")

            for d in u:
                key_down(d)
                key_up(d)

            key_down("SPACE")
            key_up("SPACE")
