"""Various Windows Functions."""
import ctypes
import datetime

from ht3.utils.keycodes.win32 import KEY_CODES


def GetTickCount():
    return datetime.timedelta(
        milliseconds=ctypes.windll.kernel32.GetTickCount())


def GetAsyncKeyState(k):
    if isinstance(k, str):
        k = KEY_CODES.get(k)
    else:
        assert isinstance(k, int)
    r = ctypes.windll.user32.GetAsyncKeyState(k)
    return bool(r & 0x8000)
