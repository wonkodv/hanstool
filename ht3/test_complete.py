import unittest
import pathlib
from unittest.mock import patch, Mock

from ht3.complete import complete_py, complete_command, complete_path


class Test_Completion(unittest.TestCase):

    def test_command_completion(self):
        c1 = Mock()
        c1.complete = lambda s: ["arg1", "a2"]
        c1.name='c1'
        c2 = Mock()
        c2.name='c2'

        with patch("ht3.command.COMMANDS", {'c1':c1, 'c2': c2}):
            self.assertListEqual(list(complete_command('c')), ['c1', 'c2'])
            self.assertListEqual(list(complete_command('c1')), ['c1'])
            self.assertListEqual(list(complete_command('c1 ')), ['c1 arg1', 'c1 a2'])
            self.assertListEqual(list(complete_command('c1 a')), ['c1 arg1', 'c1 a2'])
            # complete_command should filter out a2
            self.assertListEqual(list(complete_command('c1 ar')), ['c1 arg1'])

    def test_py_completion(self):
        with patch("ht3.complete.SCOPE", {'one': 1, 'two': 2, 'three': 3, 'text': 'text'}):
            def f(s):
                return list(complete_py(s))

            c = f('FO')
            self.assertListEqual(c, [])

            c = f('FO ')
            assert 'FO one' in c

            c = f('FO BAR')
            self.assertListEqual(c, [])

            c = f('t')
            self.assertListEqual(c, ['text', 'three', 'two'])

            c = f('text')
            self.assertListEqual(c, ['text'])

            c = f('text ')
            # start new after spaces
            assert 'text three' in c

            c = f('text o')
            self.assertListEqual(c, ['text one']) # Is a command, not py, dont py complete

            c = f('text.')
            self.assertIn('text.startswith', c)
            self.assertIn('text.capitalize', c)

            c = f('text.s')
            self.assertIn('text.startswith', c)
            self.assertIn('text.strip', c)

            c = f('one + tw')
            self.assertListEqual(c, ['one + two'])

            c = f('"".find(te')
            self.assertListEqual(c, ['"".find(text'])

            # should not raise a key error !
            c = f('text.foo.bar')
            assert c == []

    def test_command_complete_iter(self):
        """Complete of commands should not be consumed if iterator

        If a completion function yields some values and has to compute the
        rest with an expensive function, that computation should only happen
        if the user does not like the first offered values
        """
        def compl(x):
            yield "a"
            yield "b"
            assert False, "The iterator was consumed without need"
            yield "c"
        c = Mock()
        c.complete = compl
        c.name = 'c'

        with patch("ht3.command.COMMANDS", {'c':c}):
            l = complete_command('c b')

        assert next(l) == 'c b'


    def test_complete_path_dir_slash(self):
        l = list(complete_path('ht'))
        assert 'ht3/' in l

    def test_complete_path_local(self):
        l = list(complete_path('ht3/comple'))
        assert 'ht3/complete.py' in l

    def test_complete_path_dir_slash(self):
        a = str(pathlib.Path(__file__).parent.absolute()).replace('\\','/')
        l = list(complete_path(a+'/comple'))
        assert a+'/complete.py' in l
