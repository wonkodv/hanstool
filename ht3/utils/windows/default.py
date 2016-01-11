"""Various Windows Functions."""
import ctypes
from ctypes.wintypes import POINT

def GetCursorPos():
    p = POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(p)):
        raise ctypes.WinError()
    return p
