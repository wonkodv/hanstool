from ht3.filter import Filter
from .keycodes import KEY_CODES

__all__ = ['register_hotkey', 'unregister_hotkey', 'hotkey_loop', 'MODIFIERS', 'KEY_CODES']

if Filter.os.win:
    from .windows import *

