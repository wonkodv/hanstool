import unittest
from unittest.mock import patch

from .fake_input import fake, KEY_CODES, fake_re

class Test_fake(unittest.TestCase):

    def test_re_combo(self):
        s = "CTRL+SHIFT+A"
        l = list(fake_re.finditer(s))
        assert len(l) == 1
        m = l[0]
        assert m.group('COMBO') == s
        assert m.group('mod1') == 'CTRL'
        assert m.group('mod2') == 'SHIFT'
        assert m.group('modkey') == 'A'

    def test_re_hexcode(self):
        s = "+0xEF"
        l = list(fake_re.finditer(s))
        assert len(l) == 1
        m = l[0]
        assert m.group('hkud') == '+'
        assert m.group('hkey') == 'EF'

    def runSequence(self, string, interval):
        s = []
        with patch("time.sleep") as mockSleep:
            mockSleep.side_effect=lambda t: s.append(['s', t])
            with patch(__package__ + ".fake_input.impl") as fake_in:
                fake_in.mouse_move =    lambda x,y  : s.append(["ma", x, y])
                fake_in.mouse_down =    lambda b    : s.append(["md", b])
                fake_in.mouse_up =      lambda b    : s.append(["mu", b])
                fake_in.key_down =      lambda k    : s.append(["kd", k])
                fake_in.key_up =        lambda k    : s.append(["ku", k])
                fake_in.type_string =   lambda t,i  : s.append(["t", t, i])
                fake_in.KEY_CODES =     KEY_CODES
                fake(string, interval)
        return s

    def test_all(self):
        k = KEY_CODES
        s = self.runSequence("""
            +Shift
            A
            (100)
            -Shift
            'A\SD"F'
            "GH'I"
            1000x2000
            01/250
            M1
            CTRL+A
            -0xDC
            """,0)
        exp = [
            ['kd',k['SHIFT']],
            ['kd',k['A']],
            ['ku',k['A']],
            ['s', 0.1],
            ['ku',k['SHIFT']],
            ['t', 'A\SD"F', 0],
            ['t', "GH'I", 0],
            ['ma', 1000, 2000],
            ['ma', 1, 250],
            ['md', 1],
            ['mu', 1],
            ['kd',k['CTRL']],
            ['kd',k['A']],
            ['ku',k['A']],
            ['ku',k['CTRL']],
            ['ku', 0xDC],
        ]
        self.assertListEqual(s, exp)
