from ctypes import windll
from ht3.keycodes import KEY_CODES
import time


__all__ = ['type_string', 'mouse_wheel', 'mouse_move', 'mouse_down', 'mouse_up', 'key_down', 'key_up']


mouse_event = windll.user32.mouse_event
keybd_event = windll.user32.keybd_event
keyscan = windll.user32.VkKeyScanW


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

def mouse_move(x, y):
    mouse_event(MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)

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
        d = x-2

    if up:
        f = f << 1

    return f, d

def key_down(vk):
    keybd_event(vk, 42, 0, 0)

def key_up(vk):
    keybd_event(vk, 42, KEYEVENTF_KEYUP, 0)

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


#   SendInput = ctypes.windll.user32.SendInput
#
#class KeybdInput(ctypes.Structure):
#    _fields_ = [("wVk", ctypes.c_ushort),
#                ("wScan", ctypes.c_ushort),
#                ("dwFlags", ctypes.c_ulong),
#                ("time", ctypes.c_ulong),
#                ("dwExtraInfo", ctypes.c_ulong)]
#
#class HardwareInput(ctypes.Structure):
#    _fields_ = [("uMsg", ctypes.c_ulong),
#                ("wParamL", ctypes.c_short),
#                ("wParamH", ctypes.c_ushort)]
#
#class MouseInput(ctypes.Structure):
#    _fields_ = [("dx", ctypes.c_long),
#                ("dy", ctypes.c_long),
#                ("mouseData", ctypes.c_ulong),
#                ("dwFlags", ctypes.c_ulong),
#                ("time",ctypes.c_ulong),
#                ("dwExtraInfo", ctypes.c_ulong)]
#
#class Input_Union(ctypes.Union):
#    _fields_ = [("ki", KeyBdInput),
#                 ("mi", MouseInput),
#                 ("hi", HardwareInput)]
#
#class Input(ctypes.Structure):
#    _fields_ = [("type", ctypes.c_ulong),
#                ("ii", Input_I)]
#
#
#
#
#def Unicode(char):
#    iu = Input_Union()
#    iu.ki = KeybdInput( 0, ord(char), KEYEVENTF_UNICODE, 0, 0)
#    i = Input(1 , iu)
#    return i
#
#def KeyUpDown(vk, up, scanCode=0):
#    if up:
#        flag = KEYEVENTF_KEYUP
#    else:
#        flag = 0
#
#    iu = Input_Union()
#    iu.ki = KeybdInput( vk, scanCode, flag, 0, 0)
#    i = Input(1 , iu)
#    return i
#
#def MouseUpDown(btn, up):
#    f = 0
#    d = 0
#    if b == 1:
#        f = MOUSEEVENTF_LEFTDOWN
#    elif b == 2:
#        f = MOUSEEVENTF_MIDDLEDOWN
#    elif b == 3:
#        f = MOUSEEVENTF_RIGHTDOWN
#    else:
#        f = MOUSEEVENTF_XDOWN
#        d = x-2
#
#    if up:
#        f = f << 1
#
#    iu = Input_Union()
#    iu.ki = MouseInput( 0, 0, d, f, 0, 0)
#    i = Input(0, iu)
#    return i
#
#def MouseMove(x, y):
#    iu = Input_Union()
#    iu.ki = MouseInput( x, y, 0, MOUSEEVENTF_ABSOLUTE, 0, 0)
#    i = Input(0, iu)
#    return i
#
#def MouseWheel(d, hwheel):
#    d = (d*120).round()
#    if hweheel:
#        f = MOUSEEVENTF_HWHEEL
#    else:
#        f = MOUSEEVENTF_WHEEL
#    iu = Input_Union()
#    iu.ki = MouseInput( 0, 0, d, f, 0, 0)
#    i = Input(0, iu)
#    r
