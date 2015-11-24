import unittest
import unittest.mock
import time
import os
from unittest.mock import patch, Mock, MagicMock

from ht3 import lib
import ht3.platform.fake_input

class Test_parse_command(unittest.TestCase):

    def test_noarg(self):
        ca = lib.parse_command("cmd")
        self.assertTupleEqual(ca, ('cmd',"", ''))

    def test_empty_cmd(self):
        ca = lib.parse_command("")
        self.assertTupleEqual(ca, ('',"", ''))

    def test_empty_cmd_with_arg(self):
        ca = lib.parse_command(" a")
        self.assertTupleEqual(ca, (''," ", 'a'))

    def test_arg(self):
        ca = lib.parse_command("cmd arg")
        self.assertTupleEqual(ca, ('cmd', " ", 'arg'))

    def test_tab_arg(self):
        ca = lib.parse_command("cmd\targ")
        self.assertTupleEqual(ca, ('cmd', '\t', 'arg'))

    def test_special_chars_cmd(self):
        ca = lib.parse_command("$? !%")
        self.assertTupleEqual(ca, ('$?', ' ', '!%'))


class Test_frontends(unittest.TestCase):
    def test_import_recursive(self):
        m = lib.import_recursive('unittest.mock')
        self.assertIs(m, unittest.mock)


    def get_fe(self, n):
        m = Mock()
        m.i = 0
        m.running = True
        def start():
            while m.running:
                m.i += 1

        def stop():
            m.running = False

        m.__name__ = n
        m.loop = start
        m.stop = stop
        return m

    @patch('ht3.lib.import_recursive')
    def test_full_run(self, importMock):

        fe1 = self.get_fe('fe1')
        fe2 = self.get_fe('fe2')

        fe3 = Mock()
        fe3.stop = lambda:None
        fe3.loop = lambda:time.sleep(0.1)
        fe3.__name__ = 'fe3'

        importMock.side_effect = [fe1, fe2, fe3]

        lib.load_frontend('frontend1')
        lib.load_frontend('frontend2')
        lib.load_frontend('frontend3')

        lib.run_frontends()

        self.assertGreater(fe1.i, 100)
        self.assertGreater(fe2.i, 100)

class Test_check(unittest.TestCase):
    def test_basic_os(self):
        assert os.name in lib.Check.os
        assert lib.Check.os(os.name)

    def test_basic_os(self):
        if os.name == 'nt':
            assert lib.Check.os.win
            assert lib.Check.os.windows
            assert lib.Check.os.nt
        elif os.name == 'posix':
            assert lib.Check.os.posix
            #TODO: assert Check.os.linux

    def test_currnet_frontend(self):
        with self.assertRaises(AttributeError):
            lib.Check.current_frontend('ht3.cli')
        with patch('ht3.lib.FRONTEND_LOCAL') as fl:
            fl.frontend='testfe'
            assert lib.Check.current_frontend('testfe')



class Test_Completion(unittest.TestCase):

    def test_command_completion(self):
        c1 = Mock()
        c1.complete = lambda s: ["arg1", "a2"]
        c2 = Mock()

        with patch("ht3.lib.COMMANDS", {'c1':c1, 'c2': c2, 'asdfg':None}):
            self.assertListEqual(lib.complete_command('c'), ['c1', 'c2'])
            self.assertListEqual(lib.complete_command('c1'), ['c1'])
            self.assertListEqual(lib.complete_command('c1 '), ['c1 a2', 'c1 arg1'])
            self.assertListEqual(lib.complete_command('c1 a'), ['c1 a2', 'c1 arg1'])
            self.assertListEqual(lib.complete_command('c1 ar'), ['c1 arg1'])

    def test_py_completion(self):
        with patch("ht3.lib.Env") as mockEnv:
            mockEnv.dict = {'one': 1, 'two': 2, 'three': 3, 'text': 'text'}
            c = lib.complete_py('t')
            assert 'three' in c
            assert 'two' in c
            assert 'text' in c
            assert not 'one' in c

            c = lib.complete_py('text')
            assert c == ['text']

            c = lib.complete_py('text.')
            self.assertIn('text.startswith', c)
            self.assertIn('text.capitalize', c)

            c = lib.complete_py('text.s')
            self.assertIn('text.startswith', c)
            self.assertIn('text.strip', c)

class Test_fake(unittest.TestCase):
    def runSequence(self, string):
        s = []
        with patch("ht3.lib.fake_input") as fake_in:
            fake_in.mouse_move =    lambda x,y  : s.append(["m", x, y])
            fake_in.mouse_down =    lambda b    : s.append(["md", b])
            fake_in.mouse_up =      lambda b    : s.append(["mu", b])
            fake_in.key_down =      lambda k    : s.append(["kd", k])
            fake_in.key_up =        lambda k    : s.append(["ku", k])
            fake_in.type_string =   lambda t    : s.append(["t", t])
            fake_in.KEY_CODES =     ht3.platform.fake_input.KEY_CODES

            lib.fake(string)
        return s

    def test_all(self):
        k = ht3.platform.fake_input.KEY_CODES
        s = self.runSequence("""+Shift A -Shift 'A\SD"F' "GH'I" 37x42 M1 """)
        exp = [
            ['kd',k['SHIFT']],
            ['kd',k['A']],
            ['ku',k['A']],
            ['ku',k['SHIFT']],
            ['t', 'A\SD"F'],
            ['t', "GH'I"],
            ['m', 37, 42],
            ['md', 1],
            ['mu', 1],
        ]
        self.assertListEqual(s, exp)



