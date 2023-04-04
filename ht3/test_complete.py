import pathlib
import unittest
from unittest.mock import Mock, patch

from ht3.complete import (
    complete_command_args,
    complete_commands,
    complete_path,
    complete_py,
    filter_completions,
    filter_completions_i,
)


class TestCompletion(unittest.TestCase):
    def test_command_completion(self):
        c1 = Mock()
        c1.arg_parser.complete = lambda s: ["arg1", "a2"]
        c1.name = "c1"
        c2 = Mock()
        c2.name = "c2"

        with patch("ht3.command.COMMANDS", {"c1": c1, "c2": c2}):
            self.assertListEqual(list(complete_commands("c")), ["c1", "c2"])
            self.assertListEqual(list(complete_commands("c1")), ["c1"])
            self.assertListEqual(
                list(complete_command_args("c1 ")), ["c1 arg1", "c1 a2"]
            )
            self.assertListEqual(
                list(complete_command_args("c1 a")), ["c1 arg1", "c1 a2"]
            )
            self.assertListEqual(list(complete_command_args("c1 ar")), ["c1 arg1"])

    def test_py_completion(self):
        with patch(
            "ht3.complete.SCOPE", {"one": 1, "two": 2, "three": 3, "text": "text"}
        ):

            def f(s):
                return list(complete_py(s))

            c = f("FO")
            self.assertListEqual(c, [])

            c = f("FO ")
            assert "FO one" in c

            c = f("FO BAR")
            self.assertListEqual(c, [])

            c = f("t")
            self.assertListEqual(c, ["text", "three", "two"])

            c = f("text")
            self.assertListEqual(c, ["text"])

            c = f("text ")
            # start new after spaces
            assert "text three" in c

            c = f("text o")
            # Is a command, not py, dont py complete
            self.assertListEqual(c, ["text one"])

            c = f("text.")
            self.assertIn("text.startswith", c)
            self.assertIn("text.capitalize", c)

            c = f("text.s")
            self.assertIn("text.startswith", c)
            self.assertIn("text.strip", c)

            c = f("one + tw")
            self.assertListEqual(c, ["one + two"])

            c = f('"".find(te')
            self.assertListEqual(c, ['"".find(text'])

            # should not raise a key error !
            c = f("text.foo.bar")
            assert c == []

    def test_command_complete_args_iter(self):
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
        c.arg_parser.complete = compl
        c.name = "c"

        with patch("ht3.command.COMMANDS", {"c": c}):
            completions = complete_command_args("c b")

        assert next(completions) == "c b"

    def test_complete_path_dir_slash(self):
        completions = list(complete_path("ht3"))
        assert "ht3/" in completions

    def test_complete_path_local(self):
        completions = list(complete_path("ht3/comple"))
        assert "ht3/complete.py" in completions

    def test_complete_path_absolute(self):
        a = str(pathlib.Path(__file__).parent.absolute()).replace("\\", "/")
        completions = list(complete_path(a + "/comple"))
        assert a + "/complete.py" in completions

    def test_filter_completions(self):
        def src0():
            yield "FOO"
            yield "bar"

        def src1():
            yield "FOO"
            yield "Foo"
            yield "foo"
            assert False, "The iterator was consumed without need"
            yield None

        g = filter_completions("F", src0(), src1())
        assert next(g) == "FOO"
        assert next(g) == "Foo", "should filter 'FOO'"

        g = filter_completions("f", src0(), src1())
        assert next(g) == "foo"

        g = filter_completions("b", src0(), src1())
        assert next(g) == "bar"

    def test_filter_completions_i(self):
        def src0():
            yield "FOO"
            yield "b:aR"

        def src1():
            yield "FOO"
            yield "Foo"
            yield "fuu"
            assert False, "The iterator was consumed without need"
            yield None

        g = filter_completions_i("F", src0(), src1())
        assert next(g) == "FOO"
        assert next(g) == "FUU", "should convert to upper"

        g = filter_completions_i("fo", src0(), src1())
        assert next(g) == "foo", "should convert to lower"

        g = filter_completions_i("B:", src0(), src1())
        assert next(g) == "B:aR", "Should not convert"
