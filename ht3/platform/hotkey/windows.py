from ctypes import windll, byref
from ctypes.wintypes import MSG

MODIFIERS = {
    'ALT': 1,
    'MENU': 1,
    'CTRL': 2,
    'SHIFT': 4,
    'MOD4': 8,
    'WIN': 8
}

def register_hotkey(id, mod, vk):
    return windll.user32.RegisterHotKey(None, id, mod, vk)

def unregister_hotkey(id):
    return windll.user32.UnregisterHotKey(0, id)

def hotkey_loop():
    msg = MSG()
    lpmsg = byref(msg)

    while 1:
        while windll.user32.PeekMessageW(lpmsg, 0, 0, 0, 1):
            yield msg.wParam
        yield None  # give caller a chance to sleep or close the generator
