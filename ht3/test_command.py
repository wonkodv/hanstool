import unittest
from unittest.mock import patch, Mock
from ht3.command import cmd, get_command

class TestCmd(unittest.TestCase):
    COMMANDS = {}

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_decorator(self):
        @cmd
        def someCommand():
            pass

        @cmd(name="some_other_command")
        def someOtherCommand():
            pass

        self.assertIn('someCommand', self.COMMANDS)
        self.assertIn('some_other_command', self.COMMANDS)

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_command_called(self):
        x = 0
        @cmd(args=int)
        def someCommand(arg):
            nonlocal x
            x = arg

        self.COMMANDS['someCommand']("1")
        assert x==1
        self.COMMANDS['someCommand']("42")
        assert x==42

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_origin(self):
        @cmd
        def someCommand():
            pass

        f, l = self.COMMANDS['someCommand'].origin
        assert f == __file__
        assert l > 5

class Test_get_command(unittest.TestCase):
    comM = Mock()
    comM.name='com'

    preM = Mock()
    preM.name = '+'
    preM.Prefix = True
    pre2M = Mock()
    pre2M.name = '++'
    pre2M.Prefix = True
    COMMANDS = {'com': comM, '+': preM, '++':pre2M}

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_noarg(self):
        com, sep, args = get_command("com")
        assert com == self.comM
        assert sep == ''
        assert args == ''

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_empty_cmd(self):
        with self.assertRaises(KeyError):
            get_command("")
        with self.assertRaises(KeyError):
            get_command(" a")

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_arg(self):
        com, sep, args = get_command("com arg")
        assert com == self.comM
        assert sep == ' '
        assert args == 'arg'

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_tab_arg(self):
        com, sep, args = get_command("com\targuments")
        assert com == self.comM
        assert sep == '\t'
        assert args == 'arguments'

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_prefix_args(self):
        com, sep, args = get_command("+foo")
        assert com == self.preM
        assert sep == ''
        assert args == 'foo'

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_prefix_noarg(self):
        com, sep, args = get_command("+")
        assert com == self.preM
        assert sep == ''
        assert args == ''

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_prefix_ws_arg(self):
        com, sep, args = get_command("+ foo")
        assert com == self.preM
        assert sep == ' '
        assert args == 'foo'

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_prefix_order(self):
        com, sep, args = get_command("++foo")
        assert com == self.pre2M
        assert sep == ''
        assert args == 'foo'
