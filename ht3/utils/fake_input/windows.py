"""Fake Input on windows"""

import ctypes
from ctypes.wintypes import POINT
from ht3.keycodes import KEY_CODES
import time


__all__ = (
    'type_string',
    'get_mouse_pos',
    'mouse_wheel',
    'mouse_move',
    'mouse_down',
    'mouse_up',
    'key_down',
    'key_up'
)


mouse_event = ctypes.windll.user32.mouse_event
keybd_event = ctypes.windll.user32.keybd_event
keyscan = ctypes.windll.user32.VkKeyScanW


EXTENDED_KEYS=set(KEY_CODES[k] for k in (
        'UP',
        'DOWN',
        'LEFT',
        'RIGHT',
        'HOME',
        'END',
        'PRIOR',
        'NEXT',
        'INSERT',
        'DELETE'
    )
)

KEYEVENTF_EXTENDEDKEY   = 0x0001
KEYEVENTF_KEYUP         = 0x0002

MOUSEEVENTF_ABSOLUTE    = 0x8000
MOUSEEVENTF_LEFTDOWN    = 0x0002
MOUSEEVENTF_LEFTUP      = 0x0004
MOUSEEVENTF_MIDDLEDOWN  = 0x0020
MOUSEEVENTF_MIDDLEUP    = 0x0040
MOUSEEVENTF_MOVE        = 0x0001
MOUSEEVENTF_RIGHTDOWN   = 0x0008
MOUSEEVENTF_RIGHTUP     = 0x0010
MOUSEEVENTF_WHEEL       = 0x0800
MOUSEEVENTF_XDOWN       = 0x0080
MOUSEEVENTF_XUP         = 0x0100
MOUSEEVENTF_WHEEL       = 0x0800
MOUSEEVENTF_HWHEEL      = 0x01000

def get_mouse_pos():
    p = POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(p)):
        raise ctypes.WinError()
    return p.x, p.y

def mouse_move(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)

def mouse_down(b):
    f, d = _btn(b, False)
    mouse_event(f, 0, 0, d, 0)

def mouse_up(b):
    f, d = _btn(b, True)
    mouse_event(f, 0, 0, d, 0)

def mouse_wheel(x, y=0):
    if x:
        d = (120 * x).round()
        mouse_event(MOUSEEVENTF_WHEEL, 0, 0, d, 0)
    if y:
        d = (120 * y).round()
        mouse_event(MOUSEEVENTF_HWHEEL, 0, 0, d, 0)


def _btn(b, up):
    f = 0
    d = 0
    if b == 1:
        f = MOUSEEVENTF_LEFTDOWN
    elif b == 2:
        f = MOUSEEVENTF_MIDDLEDOWN
    elif b == 3:
        f = MOUSEEVENTF_RIGHTDOWN
    else:
        f = MOUSEEVENTF_XDOWN
        d = b-2

    if up:
        f = f << 1

    return f, d

def key_down(vk):
    f = 0
    if vk in EXTENDED_KEYS:
        f |= KEYEVENTF_EXTENDEDKEY
    keybd_event(vk, 42, f, 0)

def key_up(vk, extended=False):
    f = KEYEVENTF_KEYUP
    if vk in EXTENDED_KEYS:
        f |= KEYEVENTF_EXTENDEDKEY
    keybd_event(vk, 42, f, 0)

def type_string(s, interval=0):
    if interval:
        def i():
            time.sleep(float(interval)/1000)
    else:
        def i():
            pass
    for c in s:
        x = keyscan(ord(c))
        if x < 0:
            raise OSError("Cannot get keycode")

        if x & 0x100:
            i()
            key_down(KEY_CODES['SHIFT'])
        if x & 0x200:
            i()
            key_down(KEY_CODES['CTRL'])
        if x & 0x400:
            i()
            key_down(KEY_CODES['ALT'])
        i()
        key_down(x&0xff)
        i()
        key_up(x&0xff)
        if x & 0x400:
            i()
            key_up(KEY_CODES['ALT'])
        if x & 0x200:
            i()
            key_up(KEY_CODES['CTRL'])
        if x & 0x100:
            i()
            key_up(KEY_CODES['SHIFT'])
