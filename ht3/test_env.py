import unittest

from ht3.env import _Env_class

class EnvTest(unittest.TestCase):
    def test_is_empty(self):
        e = _Env_class()
        assert dict(e) == {}

    def test_asDict(self):
        e = _Env_class()
        e['key'] = 1
        e['key2']= 2
        self.assertEqual(e['key'],1)
        self.assertEqual(e['key2'],2)

    def test_iter(self):
        e = _Env_class()
        e['Key1'] = 1
        e['Key2'] = 2

        self.assertListEqual(list(sorted(e)), ['Key1', 'Key2'])

    def test_ObjToDict(self):
        e = _Env_class()
        e['Key1'] = 1
        e['Key2'] = 2
        self.assertDictEqual (e.dict, {'Key1':1, 'Key2':2})

    def test_attribute_not_write(self):
        """The Attributes of Env are not writable"""
        e = _Env_class()
        with self.assertRaises(AttributeError):
            e.Attr1 = 1

    def test_attribute_read(self):
        e = _Env_class()
        e.dict['Key3'] = 3

        self.assertEqual(e.Key3, 3)

    def test_reload(self):
        e = _Env_class()
        e['key'] = 1

        e._reload()

        assert 'key' not in e

    def test_persistent(self):
        e = _Env_class()
        e['key'] = 1
        e.put_persistent('pkey', 2)

        e._reload()

        assert 'key' not in e
        assert e['pkey'] == 2
