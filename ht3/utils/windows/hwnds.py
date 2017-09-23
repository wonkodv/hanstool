"""Functions that deal with Windows Windows."""
import ctypes
from ctypes.wintypes import RECT, POINT, HWND, LPARAM, DWORD
from ctypes import c_wchar, c_bool, byref

def EnumWindows(cb):
    exc = None

    @ctypes.WINFUNCTYPE(c_bool, HWND, LPARAM)
    def _cb(handle,_):
        try:
            r = cb(handle)
            return r is None or bool(r)
        except Exception as e:
            nonlocal exc
            exc = e
            return False
    r = ctypes.windll.user32.EnumWindows(_cb, 0)
    if exc:
        raise exc
    if not r:
        raise ctypes.WinError()

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
    if not ctypes.windll.user32.GetClassNameW(wnd, name, 100):
        raise ctypes.WinError()
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
    text = (c_wchar * 100)()
    ctypes.windll.user32.GetWindowTextW(wnd, text, 100)
    return text.value

def SetWindowText(wnd, text):
    if not ctypes.windll.user32.SetWindowTextW(wnd, text):
        raise ctypes.WinError()

def IsWindowVisible(wnd):
    return bool(ctypes.windll.user32.IsWindowVisible(wnd))

def IsWindow(hwnd):
    return bool(ctypes.windll.user32.IsWindow(hwnd))

_show_command = dict(
    FORCEMINIMIZE    =  11,
    HIDE             =   0,
    MAXIMIZE         =   3,
    MINIMIZE         =   6,
    RESTORE          =   9,
    SHOW             =   5,
    SHOWDEFAULT      =  10,
    SHOWMAXIMIZED    =   3,
    SHOWMINIMIZED    =   2,
    SHOWMINNOACTIVE  =   7,
    SHOWNA           =   8,
    SHOWNOACTIVATE   =   4,
    SHOWNORMAL       =   1,
)

def ShowWindow(wnd, cmd):
    cmd = _show_command.get(cmd, cmd)
    return ctypes.windll.user32.ShowWindow(wnd, cmd)

def SetForegroundWindow(wnd):
    return ctypes.windll.user32.SetForegroundWindow(wnd)

def SetParent(child, parent):
    if not ctypes.windll.user32.SetParent(child, parent):
        raise ctypes.WinError()

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


class Window:
    def __init__(self, hwnd):
        self.hwnd=hwnd

    def __bool__(self):
        """Is this a real window?"""
        return IsWindow(self.hwnd)

    @classmethod
    def find(cls, spec=..., *,parent=None, after=None, classname=None, title=None):
        return cls(FindWindow(spec=spec, parent=parent, after=after, cls=classname, title=title))

    @classmethod
    def foreground(cls):
        return cls(GetForegroundWindow())

    @classmethod
    def from_point(cls, p=None):
        return cls(WindowFromPoint(p))

    @classmethod
    def enumerate(cls, cb):
        def _cb(hwnd):
            return cb(cls(hwnd))
        EnumWindows(_cb)

    @property
    def class_name(self):
        return GetClassName(self.hwnd)

    @property
    def parent(self):
        return type(self)(GetParent(self.hwnd))

    @parent.setter
    def set_parent(self, parent):
        SetParent(self.hwnd, parent.hwnd)

    @property
    def rect(self):
        return GetWindowRect(self.hwnd)

    @property
    def text(self):
        return GetWindowText(self.hwnd)
    title=text

    @text.setter
    def _set_text(self, text):
        return SetWindowText(self.hwnd, text)

    @property
    def thread_id(self):
        t,p = GetWindowThreadProcessId(self.hwnd)
        return t

    @property
    def process_id(self):
        t,p = GetWindowThreadProcessId(self.hwnd)
        return p

    @property
    def visible(self):
        return IsWindowVisible(self.hwnd)

    @visible.setter
    def visible(self, v):
        if v:
            self.show()
        else:
            self.hide()

    def stay_on_top(self, b):
        if b:
            self.set_pos(after="TOPMOST")
        else:
            self.set_pos(after="NOTOPMOST")

    def to_front(self):
        SetForegroundWindow(self.hwnd)

    def set_pos(self, *,after=..., left=..., top=..., width=..., height=..., flags=0):
        SetWindowPos(self.hwnd, after=after, left=left, top=top, width=width, height=height, flags=flags)

    def show(self):
        ShowWindow(self.hwnd, "SHOW")

    def hide(self):
        ShowWindow(self.hwnd, "HIDE")

    def maximize(self):
        ShowWindow(self.hwnd, "MAXIMIZE")

    def minimize(self):
        ShowWindow(self.hwnd, "MINIMIZE")

    def restore(self):
        ShowWindow(self.hwnd, "MINIMIZE")
