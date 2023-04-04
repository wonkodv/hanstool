import unittest
from unittest.mock import MagicMock, patch

from ht3.command import NoCommandError, cmd, get_registered_command, run_command
from ht3.lib import THREAD_LOCAL


class TestCmd(unittest.TestCase):
    COMMANDS = {}

    @patch("ht3.command.COMMANDS", COMMANDS)
    def test_decorator(self):
        @cmd
        def some_command():
            pass

        @cmd(name="some_other")
        def some_other_command():
            pass

        self.assertIn("some_command", self.COMMANDS)
        self.assertIn("some_other", self.COMMANDS)

    @patch("ht3.command.COMMANDS", COMMANDS)
    def test_command_called(self):
        x = 0

        @cmd
        def some_command(arg: int):
            nonlocal x
            x = arg

        run_command("some_command 1")
        assert x == 1
        run_command("some_command 2")
        assert x == 2

    @patch("ht3.command.COMMANDS", COMMANDS)
    def test_origin(self):
        @cmd
        def some_command():
            pass

        f, line_no = self.COMMANDS["some_command"].origin
        assert f == __file__
        assert line_no > 5

    @patch("ht3.command.COMMANDS", COMMANDS)
    def test_context(self):
        x = None

        @cmd
        def some_other_command():
            nonlocal x
            x = THREAD_LOCAL.command

        @cmd
        def some_command():
            run_command("some_other_command")

        run_command("some_command")
        assert x.name == "some_other_command"
        assert x.parent.name == "some_command"
        assert "result" in repr(x)


class TestGetCommand(unittest.TestCase):
    COMMANDS = {}

    @patch("ht3.command.COMMANDS", COMMANDS)
    def test_noarg(self):
        m = MagicMock()
        self.COMMANDS.clear()
        self.COMMANDS["cmd"] = m
        c = get_registered_command("cmd")
        m.assert_called_with("cmd", "")
        assert m() is c

    @patch("ht3.command.COMMANDS", COMMANDS)
    def test_empty_cmd(self):
        m = MagicMock()
        self.COMMANDS.clear()
        self.COMMANDS["cmd"] = m
        with self.assertRaises(NoCommandError):
            get_registered_command("cmd1")
        with self.assertRaises(NoCommandError):
            get_registered_command(" cmd")

    @patch("ht3.command.COMMANDS", COMMANDS)
    def test_arg(self):
        m = MagicMock()
        self.COMMANDS.clear()
        self.COMMANDS["cmd"] = m
        c = get_registered_command("cmd arg string")
        m.assert_called_with("cmd arg string", "arg string")
        assert m() is c
