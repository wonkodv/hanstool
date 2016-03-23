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
    c1 = Mock()
    c1.name='c1'

    c2 = Mock()
    c2.name = 'c2'

    COMMANDS = {'c1': c1, 'c2': c2}

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_noarg(self):
        com, sep, args = get_command("c1")
        assert com == self.c1
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
        com, sep, args = get_command("c1 arg")
        assert com == self.c1
        assert sep == ' '
        assert args == 'arg'
