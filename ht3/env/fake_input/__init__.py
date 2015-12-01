import re
import time

from ht3.lib import Check
from ht3.keycodes import KEY_CODES
from ht3.env import Env

__all__ = [
        'mouse_move',
        'mouse_down',
        'mouse_up',
        'mouse_wheel',
        'key_down',
        'key_up',
        'type_string',
        'KEY_CODES',
        'fake']

impl = object()

if Check.os.win:
    from . import windows as impl
elif Check.os.posix:
    try:
        from . import xserver as impl
    except NotImplementedError:
        pass



fake_types = (
    ("WHITESPACE",  r"\s+"),
    ("MOVE",        r"(?P<x>\d+)x(?P<y>\d+)"),
    ("MBTN",        r"(?P<mud>\+|-|)M(?P<btn>[1-3])"),
    ("KEY",         r"(?P<kud>\+|-|)(?P<key>[A-Za-z_0-9]+)"),
    ("STRING1",     r"'(?P<s1>[^']*)'"),
    ("STRING2",     r'"(?P<s2>[^"]*)"'),
    ("SLEEP",       r'\((?P<sleep>[0-9.]+)\)'),
    ("INVALID",     r"\S+")
    )

fake_re = re.compile("|".join("(?P<%s>%s)" % pair for pair in fake_types))

@Env
def fake(string,interval=10):
    """ Fake a sequence of Events, specified by a string in the
        following mini language:
        *   Whitespaces are ignored
        *   123X456 moves the mouse to x=123 and y=456, see mouse_move
        *   M1      Does a Mouse Click at the current mouse position
                    With the left button. 2=Middle, 3=right, 4, 5
        *   +M2     Press but do not release the middle mouse button
        *   -M3     Release the right mouse button
        *   'hans@fred.com'  Type hans' email address. No escaping any char
            except the closing quote is allowed in the string. You can use
            single or double quotes for text that contains the other quote.
        *   +Key    Press Key. valid Keys are A-Z 0-9 SHIFT, CoNTroL,... see KEY_CODES
        *   -A  Release A
        *   A   Press, then release A
        *   (10.3) sleep 10.3 ms
        if an interval (in ms) is given, wait this long before every event (thus
        twice when pressing and releasing keys/buttons). also before sleeps.
    """

    sequence = []
    def a(f, *a):
        sequence.append((f, a, m))
    for m in fake_re.finditer(string):
        if   m.group("WHITESPACE"):
            pass

        elif m.group("MOVE"):
            x = int(m.group('x'))
            y = int(m.group('y'))
            a(impl.mouse_move, x, y)

        elif m.group("MBTN"):
            ud = m.group('mud')
            btn= int(m.group('btn'))
            if ud != '-':
                a(impl.mouse_down, btn)
            if ud != '+':
                a(impl.mouse_up, btn)

        elif m.group("KEY"):
            ud = m.group('kud')
            key= m.group('key')
            key= impl.KEY_CODES[key.upper()]
            if ud != '-':
                a(impl.key_down, key)
            if ud != '+':
                a(impl.key_up, key)

        elif m.group("STRING1"):
            s = m.group('s1')
            a(impl.type_string, s, interval)

        elif m.group("STRING2"):
            s = m.group('s2')
            a(impl.type_string, s, interval)

        elif m.group("SLEEP"):
            t = float(m.group('sleep'))/1000
            a(time.sleep, t)

        elif m.group("INVALID"):
            raise ValueError("Invalid Token", m.group(0))
        else:
            assert False, m

    for c, a, m in sequence:
        if interval:
            time.sleep(float(interval)/1000)
        try:
            c(*a)
        except:
            raise Exception(m)

for k in __all__:
    if hasattr(impl, k):
        Env[k] = getattr(impl, k)
