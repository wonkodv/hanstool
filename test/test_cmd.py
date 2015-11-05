import unittest

import ht3.cmd

class TestCmd(unittest.TestCase):
    def test_decorator(self):
        @ht3.cmd.cmd
        def someCommand():
            pass

        @ht3.cmd.cmd(name="some_other_command")
        def someOtherCommand():
            pass

        self.assertIn('someCommand',ht3.cmd.COMMANDS)
        self.assertIn('some_other_command',ht3.cmd.COMMANDS)
