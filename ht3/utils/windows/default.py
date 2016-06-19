"""Various Windows Functions."""
import ctypes
import datetime

def GetTickCount():
    return datetime.timedelta(milliseconds=ctypes.windll.kernel32.GetTickCount())
