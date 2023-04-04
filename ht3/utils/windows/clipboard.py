from ctypes import FormatError, c_size_t, c_void_p, c_wchar_p, cdll, memmove, windll
from ctypes.wintypes import BOOL, DWORD, UINT


def expect_nonzero(result, func, args):
    if not result:
        e = GetLastError()
        if e:
            s = FormatError(e)
            raise OSError(result, e, s, args)
    return args


CloseClipboard = windll.user32.CloseClipboard
CloseClipboard.argtypes = []
CloseClipboard.errcheck = expect_nonzero
CloseClipboard.restype = BOOL
EmptyClipboard = windll.user32.EmptyClipboard
EmptyClipboard.argtypes = []
EmptyClipboard.errcheck = expect_nonzero
EmptyClipboard.restype = BOOL
GetClipboardData = windll.user32.GetClipboardData
GetClipboardData.argtypes = [UINT]
GetClipboardData.restype = c_void_p
GetLastError = windll.kernel32.GetLastError
GetLastError.argtypes = []
GetLastError.restype = DWORD
GlobalAlloc = windll.kernel32.GlobalAlloc
GlobalAlloc.argtypes = [UINT, c_size_t]
GlobalAlloc.restype = c_void_p
GlobalLock = windll.kernel32.GlobalLock
GlobalLock.argtypes = [c_void_p]
GlobalLock.errcheck = expect_nonzero
GlobalLock.restype = c_void_p
GlobalSize = windll.kernel32.GlobalSize
GlobalSize.argtypes = [c_void_p]
GlobalSize.restype = c_size_t
GlobalUnlock = windll.kernel32.GlobalUnlock
GlobalUnlock.argtypes = [c_void_p]
GlobalUnlock.errcheck = expect_nonzero
GlobalUnlock.restype = BOOL
OpenClipboard = windll.user32.OpenClipboard
OpenClipboard.argtypes = [UINT]
OpenClipboard.errcheck = expect_nonzero
OpenClipboard.restype = BOOL
SetClipboardData = windll.user32.SetClipboardData
SetClipboardData.argtypes = [UINT, c_void_p]
SetClipboardData.errcheck = expect_nonzero
SetClipboardData.restype = c_void_p


def get_clipboard():
    OpenClipboard(0)
    try:
        data = GetClipboardData(13)
        if data:
            data_locked = GlobalLock(data)
            try:
                text = c_wchar_p(data_locked).value
            finally:
                GlobalUnlock(data_locked)
        else:
            text = None
    finally:
        CloseClipboard()
    return text


def set_clipboard(text):
    text = str(text)
    e = text.encode("utf-16-le")
    text_len = len(e)

    hCd = GlobalAlloc(0x2, text_len + 2)
    try:
        length = GlobalSize(hCd)
        if length <= len(e):
            raise OSError(
                f"Allocated MemBlock {hCd!r} smaller than requested: {length}"
            )
        pchData = GlobalLock(hCd)

        memmove(c_wchar_p(pchData), c_wchar_p(text), text_len)
        try:
            OpenClipboard(0)
            EmptyClipboard()
            SetClipboardData(13, hCd)
        finally:
            CloseClipboard()
    finally:
        GlobalUnlock(hCd)


__all__ = ("get_clipboard", "set_clipboard")

if __name__ == "__main__":
    import sys

    if sys.argv[1:] in ([], ["-o"]):
        print(get_clipboard())
    else:
        set_clipboard(" ".join(sys.argv[1:]))
