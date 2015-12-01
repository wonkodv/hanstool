import unittest
from ht3.command import cmd, COMMANDS, parse_command

class TestCmd(unittest.TestCase):
    def test_decorator(self):
        @cmd
        def someCommand():
            pass

        @cmd(name="some_other_command")
        def someOtherCommand():
            pass

        self.assertIn('someCommand', COMMANDS)
        self.assertIn('some_other_command', COMMANDS)

    def test_command_called(self):
        x = 0
        @cmd(args=int)
        def someCommand(arg):
            nonlocal x
            x = arg

        COMMANDS['someCommand']("1")
        assert x==1
        COMMANDS['someCommand']("42")
        assert x==42


class Test_parse_command(unittest.TestCase):

    def test_noarg(self):
        ca = parse_command("cmd")
        self.assertTupleEqual(ca, ('cmd',"", ''))

    def test_empty_cmd(self):
        ca = parse_command("")
        self.assertTupleEqual(ca, ('',"", ''))

    def test_empty_cmd_with_arg(self):
        ca = parse_command(" a")
        self.assertTupleEqual(ca, (''," ", 'a'))

    def test_arg(self):
        ca = parse_command("cmd arg")
        self.assertTupleEqual(ca, ('cmd', " ", 'arg'))

    def test_tab_arg(self):
        ca = parse_command("cmd\targ")
        self.assertTupleEqual(ca, ('cmd', '\t', 'arg'))

    def test_special_chars_cmd(self):
        ca = parse_command("$? !%")
        self.assertTupleEqual(ca, ('$?', ' ', '!%'))
