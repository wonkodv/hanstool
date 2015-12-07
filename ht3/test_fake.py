import unittest
import time
from unittest.mock import patch, Mock, MagicMock

from ht3.env.fake_input import fake, KEY_CODES

class Test_fake(unittest.TestCase):
    def runSequence(self, string, interval):
        s = []
        with patch("time.sleep") as mockSleep:
            mockSleep.side_effect=lambda t: s.append(['s', t])
            with patch("ht3.env.fake_input.impl") as fake_in:
                fake_in.mouse_move =    lambda x,y  : s.append(["m", x, y])
                fake_in.mouse_down =    lambda b    : s.append(["md", b])
                fake_in.mouse_up =      lambda b    : s.append(["mu", b])
                fake_in.key_down =      lambda k    : s.append(["kd", k])
                fake_in.key_up =        lambda k    : s.append(["ku", k])
                fake_in.type_string =   lambda t,i  : s.append(["t", t, i])
                fake_in.KEY_CODES =     KEY_CODES
                with patch('ht3.env.fake_input.Env'): # Env.log
                    fake(string, interval)
        return s

    def test_all(self):
        k = KEY_CODES
        s = self.runSequence("""+Shift A (100) -Shift 'A\SD"F' "GH'I" 37.2x42.67 50/50 M1 """,0)
        exp = [
            ['kd',k['SHIFT']],
            ['kd',k['A']],
            ['ku',k['A']],
            ['s', 0.1],
            ['ku',k['SHIFT']],
            ['t', 'A\SD"F', 0],
            ['t', "GH'I", 0],
            ['m', 37.2, 42.67],
            ['m', 50, 50],
            ['md', 1],
            ['mu', 1],
        ]
        self.assertListEqual(s, exp)
