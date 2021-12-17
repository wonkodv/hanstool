import unittest

from ht3.env import Env, EnvClass


class EnvTest(unittest.TestCase):
    def test_as_dict(self):
        e = EnvClass()
        e["key"] = 1
        e["key2"] = 2
        self.assertEqual(e["key"], 1)
        self.assertEqual(e["key2"], 2)

    def test_iter(self):
        e = EnvClass()
        e["Key1"] = 1
        e["Key2"] = 2

        i = iter(e)

        assert "Key1" in set(i)

    def test_obj_to_dict(self):
        e = EnvClass()
        e["Key1"] = 1
        e["Key2"] = 2
        d = dict(e)
        assert d["Key1"] == 1
        assert d["Key2"] == 2

    def test_attribute_not_write(self):
        """The Attributes of Env are not writable"""
        e = EnvClass()
        with self.assertRaises(AttributeError):
            e.Attr1 = 1

    def test_attribute_read(self):
        e = EnvClass()
        e.dict["Key3"] = 3

        self.assertEqual(e.Key3, 3)

    def test_reload(self):
        e = EnvClass()
        e["key"] = 1

        e._reload()

        assert "key" not in e

    def test_persistent(self):
        e = EnvClass()
        e["key"] = 1
        e.put_static("pkey", 2)

        e._reload()

        assert "key" not in e
        assert e["pkey"] == 2

    def test_env_module(self):
        Env["X"] = 42
        Env["Y"] = 36

        def _():
            import Env

            assert Env.Y == 36
            from Env import X

            return X

        assert _() == 42

    def test_decorator(self):
        e = EnvClass()

        @e
        def a():
            return 1

        assert e["a"]() == 1

    def test_updateable(self):
        e = EnvClass()

        @e.updateable
        def a():
            return 1

        # this is not a but a wrapper that does e['a']() (without the
        # recursion)
        ref1 = e["a"]

        assert a is ref1
        assert ref1() == 1

        @e.updateable
        def a():
            return 2

        ref2 = e["a"]

        assert ref1() == 2  # looks up the newest func from e
        assert ref2() == 2  # looks up the newest func from e
        assert a() == 2
        assert ref1 is not ref2  # different wrappers with the same effect
