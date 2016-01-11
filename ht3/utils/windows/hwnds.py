"""Functions that deal with Windows Windows."""
import ctypes
from ctypes.wintypes import RECT, POINT
from ctypes import c_wchar

def FindWindow(spec=..., *,parent=None, after=None, cls=None, title=None):
    if spec is ...:
        return ctypes.windll.user32.FindWindowExW(parent, after, cls, title)
    if parent or after or cls or title:
        raise ValueError()
    w = ctypes.windll.user32.FindWindowW(spec, None)
    if not w:
        w = ctypes.windll.user32.FindWindowW(None, spec)
    return w

def GetWindowRect(hwnd):
    r = RECT(0,0,0,0)
    p = ctypes.byref(r)
    if not ctypes.windll.user32.GetWindowRect(hwnd, p):
        raise ctypes.WinError()
    return r.left, r.top, r.right - r.left, r.bottom - r.top

def SetParent(child, parent):
    return ctypes.windll.user32.SetParent(child, parent)

def SetForegroundWindow(wnd):
    return ctypes.windll.user32.SetForegroundWindow(wnd)

def GetCursorPos():
    p = POINT()
    if not ctypes.windll.user32.GetCursorPos(ctypes.byref(p)):
        raise ctypes.WinError()
    return p

def WindowFromPoint(p=None):
    if p is None:
        p = GetCursorPos()
    elif not isinstance(p, POINT):
        p = POINT(*p)
    return ctypes.windll.user32.WindowFromPoint(p)

def GetClassName(wnd):
    name = (c_wchar * 100)()
    ctypes.windll.user32.GetClassNameW(wnd, name, 100)
    return name.value


def SetWindowPos(hwnd, *,after=..., left=..., top=..., width=..., height=..., flags=0):
    after = dict(BOTTOM=1,TOP=0,TOPMOST=-1,NOTOPMOST=-2).get(after,after)
    flags = dict(SHOW=0x40,HIDE=0x80,NOACTIVATE=0x10,).get(flags,flags)

    if left is ... or top is ...:
        flags |= 2
        left = 0
        top = 0

    if width is ... or height is ...:
        flags |= 1
        width = 0
        height = 0

    if after is ...:
        flags |= 4
        after = 0
    if not ctypes.windll.user32.SetWindowPos(hwnd, after, left, top, width, height, flags):
        ctypes.WinError()
def GetTaskBarHandle():
    h = FindWindow(cls='Shell_TrayWnd')
    if not h:
        raise ctypes.WinError()
    h = FindWindow(parent=h, cls='ReBarWindow32')
    if not h:
        raise ctypes.WinError()
    h = FindWindow(parent=h, cls='ToolbarWindow32', title='hanstool')
    if not h:
        raise ctypes.WinError()
    return h

def GetForegroundWindow():
    return ctypes.windll.user32.GetForegroundWindow()
