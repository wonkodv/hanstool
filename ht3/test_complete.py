import unittest
from unittest.mock import patch, Mock

from ht3.complete import complete_py, complete_command


class Test_Completion(unittest.TestCase):

    def test_command_completion(self):
        c1 = Mock()
        c1.complete = lambda s: ["arg1", "a2"]
        c2 = Mock()

        with patch("ht3.command.COMMANDS", {'c1':c1, 'c2': c2, 'asdfg':None}):
            self.assertListEqual(complete_command('c'), ['c1', 'c2'])
            self.assertListEqual(complete_command('c1'), ['c1'])
            self.assertListEqual(complete_command('c1 '), ['c1 arg1', 'c1 a2'])
            self.assertListEqual(complete_command('c1 a'), ['c1 arg1', 'c1 a2'])
            self.assertListEqual(complete_command('c1 ar'), ['c1 arg1'])

    def test_py_completion(self):
        with patch("ht3.complete.SCOPE", {'one': 1, 'two': 2, 'three': 3, 'text': 'text'}):
            c = complete_py('FO')
            self.assertListEqual(c, [])

            c = complete_py('FO ')
            self.assertListEqual(c, [])

            c = complete_py('FO BAR')
            self.assertListEqual(c, [])

            c = complete_py('t')
            self.assertListEqual(c, ['text', 'three', 'two'])

            c = complete_py('text')
            self.assertListEqual(c, ['text'])

            c = complete_py('text ')
            self.assertListEqual(c, []) # Is a command, not py, dont py complete

            c = complete_py('text foo')
            self.assertListEqual(c, []) # Is a command, not py, dont py complete

            c = complete_py('text.')
            self.assertIn('text.startswith', c)
            self.assertIn('text.capitalize', c)

            c = complete_py('text.s')
            self.assertIn('text.startswith', c)
            self.assertIn('text.strip', c)

