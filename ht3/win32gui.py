import os
import sys
import threading

from . import lib

from ctypes import *
from ctypes.wintypes import *


WNDPROCTYPE = WINFUNCTYPE(c_int, HWND, c_uint, WPARAM, LPARAM)

WS_EX_APPWINDOW = 0x40000
WS_EX_TOPMOST = 8
WS_OVERLAPPEDWINDOW = 0xcf0000
WS_CAPTION = 0xc00000
WS_BORDER   = 0x00800000
WS_CHILD    = 0x40000000
WS_VISIBLE  = 0x10000000
WS_POPUP    = 0x80000000


ES_LEFT        = 0x0
ES_CENTER      = 0x1
ES_RIGHT       = 0x2
ES_MULTILINE   = 0x4
ES_UPPERCASE   = 0x8
ES_LOWERCASE   = 0x10
ES_PASSWORD    = 0x20
ES_AUTOVSCROLL = 0x40
ES_AUTOHSCROLL = 0x80
ES_NOHIDESEL   = 0x100
ES_OEMCONVERT  = 0x400
ES_READONLY    = 0x800
ES_WANTRETURN  = 0x1000

SW_SHOWNORMAL = 1
SW_SHOW = 5

CS_HREDRAW = 2
CS_VREDRAW = 1

CW_USEDEFAULT = 0x80000000

WM_DESTROY = 2
WM_COMMAND = 0x0111

WHITE_BRUSH = 0


class WNDCLASSEX(Structure):
    _fields_ = [("cbSize", c_uint),
                ("style", c_uint),
                ("lpfnWndProc", WNDPROCTYPE),
                ("cbClsExtra", c_int),
                ("cbWndExtra", c_int),
                ("hInstance", HANDLE),
                ("hIcon", HANDLE),
                ("hCursor", HANDLE),
                ("hBrush", HANDLE),
                ("lpszMenuName", LPCWSTR),
                ("lpszClassName", LPCWSTR),
                ("hIconSm", HANDLE)]

class Window:
    def __init__(self, name, title, x, y, width, height):
        wndClass = WNDCLASSEX()
        wndClass.cbSize = sizeof(WNDCLASSEX)
        wndClass.style = CS_HREDRAW | CS_VREDRAW
        wndClass.lpfnWndProc = WNDPROCTYPE(self._proc_message)
        wndClass.cbClsExtra = 0
        wndClass.cbWndExtra = 0
        wndClass.hInstance = 0
        wndClass.hIcon = 0
        wndClass.hCursor = 0
        wndClass.hBrush = windll.gdi32.GetStockObject(WHITE_BRUSH)
        wndClass.lpszMenuName = 0
        wndClass.lpszClassName = name
        wndClass.hIconSm = 0

        regRes = windll.user32.RegisterClassExW(byref(wndClass))

        hWnd = windll.user32.CreateWindowExW(
                WS_EX_TOPMOST,
                name,
                title,
                #WS_OVERLAPPEDWINDOW | WS_CAPTION,
                WS_POPUP,
                x, y,
                width, height, 0, 0, 0, 0)

        if not hWnd:
            raise OSError("Window not created")

        self.handle = hWnd
        self._dontCarbageCollect = wndClass

    def show(self):
        windll.user32.ShowWindow(self.handle, SW_SHOW)
        windll.user32.UpdateWindow(self.handle)

    def _proc_message(self, hWnd, msg, wParam, lParam):
        try:
            if msg == WM_DESTROY:
                windll.user32.PostQuitMessage(0)
                return 0

            x = self.proc_message(hWnd, msg, wParam, lParam)
            if x == NotImplemented or x == None:
                return windll.user32.DefWindowProcW(hWnd, msg, wParam, lParam)
            else:
                return x
        except:
            stop()
            raise

    def proc_message(self, hWnd, msr, wParam, lParam):
        print("%4X, %4X, %4X" % (msg, wParam, lParam))

class HTWindow(Window):
    def __init__(self):
        super().__init__("HansTool3WndCls","Hanstool3", 100,100,100,100)
        self.edit = windll.user32.CreateWindowExW(
                0,
                "EDIT",
                "",
                WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL | ES_NOHIDESEL,
                0, 0,
                100, 21,
                self.handle,
                1, # EditID
                0, 0)

        if not self.edit:
            raise OSError("Can not create EDIT")

    def proc_message(self, hWnd, msg, wParam, lParam):
        if self.edit == hWnd:
            print("EDIT %4X, %4X, %4X" % (msg, wParam, lParam))
        else:
            print("%4X: %4X, %4X, %4X" % (hWnd, msg, wParam, lParam))

_message_loop_running = threading.Event()

def stop():
    _message_loop_running.set()

def loop():
    win = HTWindow()
    win.show()

    lib.Env.GUI_WINDOW = win

    _message_loop_running.clear()
    msg = MSG()
    lpmsg = pointer(msg)
    while 1:
        if _message_loop_running.is_set():
            return
        if windll.user32.GetMessageA(lpmsg, 0, 0, 0) == 0:
            return
        windll.user32.TranslateMessage(lpmsg)
        windll.user32.DispatchMessageA(lpmsg)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
