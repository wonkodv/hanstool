import ctypes
from ht3.lib import Env
from functools import reduce
import operator

_MessageBoxFlags={
    # Buttons
    'ABORTRETRYIGNORE':     0x00000002,
    'CANCELTRYCONTINUE':    0x00000006,
    'HELP':                 0x00004000,
    'OK':                   0x00000000,
    'OKCANCEL':             0x00000001,
    'RETRYCANCEL':          0x00000005,
    'YESNO':                0x00000004,
    'YESNOCANCEL':          0x00000003,

    # Icon
    'ICONEXCLAMATION':      0x00000030,
    'ICONWARNING':          0x00000030,
    'ICONINFORMATION':      0x00000040,
    'ICONASTERISK':         0x00000040,
    'ICONQUESTION':         0x00000020,
    'ICONSTOP':             0x00000010,
    'ICONERROR':            0x00000010,
    'ICONHAND':             0x00000010,

    # Default Button
    'DEFBUTTON1':           0x00000000,
    'DEFBUTTON2':           0x00000100,
    'DEFBUTTON3':           0x00000200,
    'DEFBUTTON4':           0x00000300,

    # Modal
    'APPLMODAL':            0x00000000,
    'SYSTEMMODAL':          0x00001000,
    'TASKMODAL':            0x00002000,

    # Options
    'DEFAULT_DESKTOP_ONLY': 0x00020000,
    'RIGHT':                0x00080000,
    'RTLREADING':           0x00100000,
    'SETFOREGROUND':        0x00010000,
    'TOPMOST':              0x00040000,
    'SERVICE_NOTIFICATION': 0x00200000
}

_MessageBoxResults = [
    None,
    'OK',
    'CANCEL',
    'ABORT',
    'RETRY',
    'IGNORE',
    'YES',
    'NO',
    None,
    None,
    'TRYAGAIN',
    'CONTINUE'
]

@Env
def MessageBox(title, text, *flags):
    try:
        flags = int(flags[0])
    except:
        flags = reduce(operator.or_, (_MessageBoxFlags[x.upper()] for x in flags))
    x = ctypes.windll.user32.MessageBoxW(0, text, title, flags)
    return _MessageBoxResults[x]
