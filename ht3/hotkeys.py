import os
import threading
import warnings
import time

from . import lib
from ctypes import windll, pointer
from ctypes.wintypes import MSG


KEY_CODES = {'F8': 119} 
MODIFIERS = {}              # TODO

if os.name == 'nt':
    def register_hotkey(id, mod, vk):
        return windll.user32.RegisterHotKey(None, id, mod, vk)

    def unregister_hotkey(id):
        return windll.user32.UnregisterHotKey(0, i)

    def do_loop():
        msg = MSG()
        lpmsg = pointer(msg)

        while 1:
            while windll.user32.PeekMessageW(lpmsg, 0, 0, 0, 1):
                yield msg.wParam
            yield None  # give caller a change to close the generator
            time.sleep(0.05)

def translate_hotkey(s):
    parts = s.split('+')
    parts = [s.strip() for s in parts]
    vk = KEY_CODES[parts[-1]]
    mod = 0
    for m in parts[:-1]:
        mod |= MODIFIERS[m]

    return mod, vk


_message_loop_running = threading.Event()

def loop():
    _message_loop_running.clear()


    hotkeys = []

    for c in lib.COMMANDS.values():
        h = c.attrs.get('HotKey',None)
        if h:
            mod, vk = translate_hotkey(h)
            id = len(hotkeys)
            hotkeys.append([c, h])

            r = register_hotkey(id, mod, vk)

            if not r:
                warnings.warn("Can not register HotKey "+h)
            else:
                lib.Env.log("Register Hotkey %d, %s mod=%r vk=%r: %r" % (id, h, mod, vk, r))


    hotkey_iter = do_loop()

    while not _message_loop_running.is_set():
        id = next(hotkey_iter)
        if id is None: 
            continue
        if id < 0 or id >= len(hotkeys):
            warning.warn("Invalid Hotkey ID")
            continue
        c, h = hotkeys[id]
        try:
            r = c()
            lib.Env.log("Hotkey %s: %s => %r", h, c.name, r)
        except Exception as e:
            lib.Env.handle_exception(e)
    hotkey_iter.close()

    for i in range(len(hotkeys)):
        if not windll.user32.UnregisterHotKey(0, i):
            warnings.warn("Can not unregister HotKey "+str(hotkeys[i][1]))

def stop():
    _message_loop_running.set()
