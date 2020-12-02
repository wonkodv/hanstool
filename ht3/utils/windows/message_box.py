"""Show the MessageBox."""
import ctypes
from functools import reduce

from .functions import MessageBoxW

_MessageBoxFlags = {
    # Buttons
    "ABORTRETRYIGNORE": 0x00000002,
    "CANCELTRYCONTINUE": 0x00000006,
    "HELP": 0x00004000,
    "OK": 0x00000000,
    "OKCANCEL": 0x00000001,
    "RETRYCANCEL": 0x00000005,
    "YESNO": 0x00000004,
    "YESNOCANCEL": 0x00000003,
    # Icon
    "ICONEXCLAMATION": 0x00000030,
    "ICONWARNING": 0x00000030,
    "ICONINFORMATION": 0x00000040,
    "ICONASTERISK": 0x00000040,
    "ICONQUESTION": 0x00000020,
    "ICONSTOP": 0x00000010,
    "ICONERROR": 0x00000010,
    "ICONHAND": 0x00000010,
    # Default Button
    "DEFBUTTON1": 0x00000000,
    "DEFBUTTON2": 0x00000100,
    "DEFBUTTON3": 0x00000200,
    "DEFBUTTON4": 0x00000300,
    # Modal
    "APPLMODAL": 0x00000000,
    "SYSTEMMODAL": 0x00001000,
    "TASKMODAL": 0x00002000,
    # Options
    "DEFAULT_DESKTOP_ONLY": 0x00020000,
    "RIGHT": 0x00080000,
    "RTLREADING": 0x00100000,
    "SETFOREGROUND": 0x00010000,
    "TOPMOST": 0x00040000,
    "SERVICE_NOTIFICATION": 0x00200000,
}

_MessageBoxResults = [
    None,
    "OK",
    "CANCEL",
    "ABORT",
    "RETRY",
    "IGNORE",
    "YES",
    "NO",
    None,
    None,
    "RETRY",
    "CONTINUE",
]


def MessageBox(title, text, flags):
    """Show the Message Box

    Shows a messagebox with ``title``, ``text`` and some buttons,
    defined by ``flags`` (either a whitespace seperated list of
    Constants, or an integer bit mask).
    """
    try:
        flags = int(flags)
    except ValueError:
        s = flags.split(" ")
        flags = reduce(
            lambda x, y: x | y, (_MessageBoxFlags[x.strip().upper()] for x in s)
        )
    x = MessageBoxW(0, text, title, flags)
    return _MessageBoxResults[x]
