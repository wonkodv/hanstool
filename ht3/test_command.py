import unittest
from unittest.mock import patch, MagicMock
from ht3.command import cmd, get_registered_command, NoCommandError, run_command
from ht3.lib import THREAD_LOCAL


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
        @cmd
        def someCommand(arg:int):
            nonlocal x
            x = arg

        run_command('someCommand 1')
        assert x==1
        run_command('someCommand 2')
        assert x==2

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_origin(self):
        @cmd
        def someCommand():
            pass

        f, l = self.COMMANDS['someCommand'].origin
        assert f == __file__
        assert l > 5


    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_origin(self):
        @cmd
        def someCommand():
            pass

        f, l = self.COMMANDS['someCommand'].origin
        assert f == __file__
        assert l > 5


    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_context(self):
        X = None
        @cmd
        def someOtherCommand():
            nonlocal X
            X = THREAD_LOCAL.command
        @cmd
        def someCommand():
            run_command('someOtherCommand')
        run_command('someCommand')
        assert X.name == 'someOtherCommand'
        assert X.parent.name == 'someCommand'
        assert 'Finished' in repr(X)


class Test_get_command(unittest.TestCase):
    COMMANDS = {}

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_noarg(self):
        m =  MagicMock()
        self.COMMANDS.clear()
        self.COMMANDS['cmd'] = m
        c = get_registered_command("cmd")
        m.assert_called_with("cmd","")
        assert m() is c

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_empty_cmd(self):
        m =  MagicMock()
        self.COMMANDS.clear()
        self.COMMANDS['cmd'] = m
        with self.assertRaises(NoCommandError):
            get_registered_command("cmd1")
        with self.assertRaises(NoCommandError):
            get_registered_command(" cmd")

    @patch('ht3.command.COMMANDS', COMMANDS)
    def test_arg(self):
        m =  MagicMock()
        self.COMMANDS.clear()
        self.COMMANDS['cmd'] = m
        c = get_registered_command("cmd arg string")
        m.assert_called_with("cmd arg string", "arg string")
        assert m() is c
