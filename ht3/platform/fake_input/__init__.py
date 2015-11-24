from ht3.lib import Check
from ..keycodes import KEY_CODES

__all__ = [
        'mouse_move',
        'mouse_down',
        'mouse_up',
        'mouse_scroll',
        'key_down',
        'key_up',
        'type_string',
        'KEY_CODES']

if Check.os.win:
    from .windows import *
elif Check.os.posix:
    try:
        from .xserver import *
    except NotImplementedError:
        pass
