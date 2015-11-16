from ht3.lib import Check
from .keycodes import KEY_CODES

__all__ = ['register_hotkey', 'unregister_hotkey', 'hotkey_loop', 'MODIFIERS', 'KEY_CODES']

if Check.os.win:
    from .windows import *

