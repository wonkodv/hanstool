"""Functions that deal with Windows Windows."""
import ctypes
from ctypes.wintypes import RECT, POINT, HWND, LPARAM, DWORD
from ctypes import c_wchar, c_bool, byref

def EnumWindows(cb):
    exc = None

    @ctypes.WINFUNCTYPE(c_bool, HWND, LPARAM)
    def _cb(handle,_):
        try:
            return cb(handle)
        except Exception as e:
            nonlocal exc
            exc = e
            return False
    r = ctypes.windll.user32.EnumWindows(_cb, 0)
    if exc:
        raise exc
    return r

def FindWindow(spec=..., *,parent=None, after=None, cls=None, title=None):
    if spec is ...:
        return ctypes.windll.user32.FindWindowExW(parent, after, cls, title)
    if parent or after or cls or title:
        raise TypeError()
    w = ctypes.windll.user32.FindWindowW(spec, None)
    if not w:
        w = ctypes.windll.user32.FindWindowW(None, spec)
    if not w:
        raise KeyError("No Window with title or class", spec)
    return w

def GetClassName(wnd):
    name = (c_wchar * 100)()
    ctypes.windll.user32.GetClassNameW(wnd, name, 100)
    return name.value

def GetCursorPos():
    p = POINT()
    if not ctypes.windll.user32.GetCursorPos(byref(p)):
        raise ctypes.WinError()
    return p

def GetForegroundWindow():
    return ctypes.windll.user32.GetForegroundWindow()

def GetParent(hWnd):
    return ctypes.windll.user32.GetParent(hWnd)

def GetWindowThreadProcessId(hwnd):
    procid = DWORD()
    threadid = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, byref(procid))
    return threadid, procid.value

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

def GetWindowRect(hwnd):
    r = RECT(0,0,0,0)
    p = byref(r)
    if not ctypes.windll.user32.GetWindowRect(hwnd, p):
        raise ctypes.WinError()
    return r.left, r.top, r.right - r.left, r.bottom - r.top

def GetWindowText(wnd):
    name = (c_wchar * 100)()
    ctypes.windll.user32.GetWindowTextW(wnd, name, 100)
    return name.value

def IsWindowVisible(wnd):
    return bool(ctypes.windll.user32.IsWindowVisible(wnd))

def SetForegroundWindow(wnd):
    return ctypes.windll.user32.SetForegroundWindow(wnd)

def SetParent(child, parent):
    return ctypes.windll.user32.SetParent(child, parent)

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

def WindowFromPoint(p=None):
    if p is None:
        p = GetCursorPos()
    elif not isinstance(p, POINT):
        p = POINT(*p)
    return ctypes.windll.user32.WindowFromPoint(p)
