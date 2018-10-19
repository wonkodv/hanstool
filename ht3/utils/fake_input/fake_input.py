"""
Fake Input

Provides a set of functions that simulate User
input (mouse moves, Key Strokes, etc).
``fake(s)`` parses the string s and generates fake input from that.
"""

import re
import time

from ht3.check import CHECK;

if CHECK.os.win:
    from . import windows as impl
elif CHECK.os.posix:
    try:
        from . import xserver as impl
    except NotImplementedError:
        impl = None

__all__ = (
    'KEY_CODES',
    'fake',
    'type_string',
    'get_mouse_pos',
    'mouse_wheel',
    'mouse_move',
    'mouse_down',
    'mouse_up',
    'key_down',
    'key_up'
)

class Error(Exception):
    pass

fake_types = (
    ("WHITESPACE",  r"\s+"),
    ("COUNT",       r"(?P<count>\d+)\*"),
    ("MOVEABS",     r"(-?[\d]+)[/:,](-?[\d]+)"),
    ("COMBO",       r"((?P<mod1>\w+)\+)"
                    r"((?P<mod2>\w+)\+)?"
                    r"((?P<mod3>\w+)\+)?"
                    r"((?P<mod4>\w+)\+)?"
                    r"(?P<modkey>[0-9a-zA-Z_]+)"),
    ("MBTN",        r"(?P<mud>\+|-|)M(?P<btn>[1-3])"),
    ("HKEY",        r"(?P<hkud>\+|-|)0x(?P<hkey>[0-9a-fA-F]{2})"),
    ("KEY",         r"(?P<kud>\+|-|)(?P<key>[A-Za-z_0-9]+)"),
    ("STRING1",     r"'([^']*)'"),
    ("STRING2",     r'"([^"]*)"'),
    ("SLEEP",       r'\(([0-9.]+)\)'),
    ("INVALID",     r"\S+")
    )

fake_re = re.compile("|".join("(?P<%s>%s)" % pair for pair in fake_types))

def fake(string, interval=10, restore_mouse_pos=False):
    """
    Fake a sequence of Events, specified by a string.

    Parses the following mini language:
    *   Whitespaces are ignored
    *   ``123/456`` moves the mouse to x=123 and y=456, see mouse_move
    *   ``M1``      Does a Mouse Click at the current mouse position
                    With the left button. 2=Middle, 3=right, 4, 5
    *   ``+M2``     Press but do not release the middle mouse button
    *   ``-M3``     Release the right mouse button
    *   ``'hans@fred.com'``  Type hans' email address. No escaping any char
                    except the closing quote is allowed in the string. You can use
                    single or double quotes for text that contains the other quote.
    *   ``+Key``    Press Key. valid Keys are A-Z 0-9 SHIFT, CoNTroL, ...
                    see ht3.utils.keycodes.*.KEY_CODES or the hexadecimal key code
                    for example 0x42 ( for B on windows )
    *   ``-A``      Release A
    *   ``A``       Press, then release A
    *   ``Mod1+Mod2+Key``
                    Press Mod1 and Mod2, then press and releasae key,
                    then release mod2 and mod1
    *   ``(10.3)``  Sleep 10.3 ms
    *   ``"Text"`` and ``'Text'``
                    Type text, by querying the current keybord layout for the
                    correct sequence of keystrokes to produce a character.
    *   ``42*``     Do the next thing 42 times
    Waits for ``interval`` milliseconds between every event. (thus
    twice when pressing and releasing keys/buttons). also before sleeps.
    Example that activates the first window, clicks in it, waits and
    then types HANSTool:
        fake("WINDOWS+1 300/45 M1 (100) +Shift H A N S -Shift 'Tool'")

    """

    sequence = []
    count = 1
    def a(f, *a):
        nonlocal count
        for _ in range(count):
            sequence.append((f, a, m))
        count = 1

    logs=[]
    def log(s, *args):
        pass
        #logs.append(s%args)

    for m in fake_re.finditer(string):
        groups = [ x for x in m.groups() if x is not None][1:]
        try:
            if   m.group("WHITESPACE"):
                pass
            elif m.group("COUNT"):
                count = int(m.group("count"))
            elif m.group("MOVEABS"):
                x,y = groups
                x = int(x)
                y = int(y)
                a(impl.mouse_move, x, y)
                log("MouseMove to x=%.1f y=%.1f", x, y)
            elif m.group("MBTN"):
                ud = m.group('mud')
                btn= int(m.group('btn'))
                if ud != '-':
                    a(impl.mouse_down, btn)
                    log("MouseDown b=%d", btn)
                if ud != '+':
                    a(impl.mouse_up, btn)
                    log("MouseUp b=%d", btn)
            elif m.group("COMBO"):
                keys = ['mod1','mod2','mod3','mod4','modkey']
                keys = [m.group(k) for k in keys]
                keys = [impl.KEY_CODES[k.upper()] for k in keys if k is not None]
                for key in keys:
                    a(impl.key_down, key)
                    log("KeyDown vk=%d", key)
                for key in reversed(keys):
                    a(impl.key_up, key)
                    log("KeyUp vk=%d", key)
            elif m.group("KEY"):
                ud = m.group('kud')
                key= m.group('key')
                key= impl.KEY_CODES[key.upper()]
                if ud != '-':
                    a(impl.key_down, key)
                    log("KeyDown vk=%d", key)
                if ud != '+':
                    a(impl.key_up, key)
                    log("KeyUp vk=%d", key)
            elif m.group("HKEY"):
                ud = m.group('hkud')
                key= m.group('hkey')
                key= int(key,16)
                if ud != '-':
                    a(impl.key_down, key)
                    log("KeyDown vk=%d", key)
                if ud != '+':
                    a(impl.key_up, key)
                    log("KeyUp vk=%d", key)
            elif m.group("STRING1") or m.group("STRING2"):
                s = groups[0]
                a(impl.type_string, s, interval)
                log("String Input: %s", s)
            elif m.group("SLEEP"):
                t = int(groups[0])
                a(time.sleep, t/1000)
                log("Sleep for %dms", t)
            else:
                assert m.group("INVALID")
                raise ValueError("Invalid Token", m.group(0))
        except KeyError:
            raise Error("Invalid fake-sequence", m)

    if restore_mouse_pos:
        mp = get_mouse_pos()
    for c, a, m in sequence:
        if interval:
            time.sleep(float(interval)/1000)
        c(*a)
    if restore_mouse_pos:
        if interval:
            time.sleep(float(interval)/1000)
        mouse_move(*mp)

for e in __all__:
    g = globals()
    if hasattr(impl,e):
        g[e]=getattr(impl,e)
