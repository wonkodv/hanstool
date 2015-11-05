import unittest

from ht3 import lib

class Test_parse_command(unittest.TestCase):

    def test_noarg(self):
        ca = lib.parse_command("cmd")
        self.assertTupleEqual(ca, ('cmd', ''))

    def test_empty_cmd(self):
        ca = lib.parse_command("")
        self.assertTupleEqual(ca, ('', ''))

    def test_empty_cmd_with_arg(self):
        ca = lib.parse_command(" a")
        self.assertTupleEqual(ca, ('', ' a'))

    def test_arg(self):
        ca = lib.parse_command("cmd arg")
        self.assertTupleEqual(ca, ('cmd', ' arg'))

    def test_tab_arg(self):
        ca = lib.parse_command("cmd\targ")
        self.assertTupleEqual(ca, ('cmd', '\targ'))

    def test_special_chars_cmd(self):
        ca = lib.parse_command("$? !%")
        self.assertTupleEqual(ca, ('$?', ' !%'))
