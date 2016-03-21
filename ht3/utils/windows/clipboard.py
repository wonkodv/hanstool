import ctypes

def get_clipboard():
    ctypes.windll.user32.OpenClipboard(0)
    if ctypes.windll.user32.IsClipboardFormatAvailable(13):
        data = ctypes.windll.user32.GetClipboardData(13)
        data_locked = ctypes.windll.kernel32.GlobalLock(data)
        text = ctypes.c_wchar_p(data_locked).value
        ctypes.windll.kernel32.GlobalUnlock(data_locked)
    else:
        text = None
    ctypes.windll.user32.CloseClipboard()
    return text

def set_clipboard(text):
    text = str(text)
    ctypes.windll.user32.OpenClipboard(0)
    ctypes.windll.user32.EmptyClipboard()
    hCd = ctypes.windll.kernel32.GlobalAlloc(0x2000, len(text.encode('utf-16-le')) + 2)
    pchData = ctypes.windll.kernel32.GlobalLock(hCd)
    ctypes.cdll.msvcrt.wcscpy(ctypes.c_wchar_p(pchData), text)
    ctypes.windll.kernel32.GlobalUnlock(hCd)
    ctypes.windll.user32.SetClipboardData(13, hCd)

    ctypes.windll.user32.CloseClipboard()
