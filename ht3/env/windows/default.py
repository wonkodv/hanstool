import ctypes
from ctypes.wintypes import POINT
from ht3.env import Env


@Env
def GetCursorPos():
    p = POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(p)):
        raise ctypes.WindowsError()
    return p
