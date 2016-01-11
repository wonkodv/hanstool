import unittest

from ht3.env import _Env_class

class EnvTest(unittest.TestCase):
    def test_containsSelf(self):
        e = _Env_class()
        self.assertIs(e , e.Env)
        self.assertIs(e , e['Env'])

    def test_asDict(self):
        e = _Env_class()
        e['key'] = 1
        e['key2']= 2
        self.assertEqual(e['key'],1)
        self.assertEqual(e['key2'],2)

    def test_noSetAttr(self):
        e = _Env_class()
        with self.assertRaises(TypeError):
            e.Attr1 = 1
        with self.assertRaises(TypeError):
            setattr(e, 'Attr2', 2)

    def test_iter(self):
        e = _Env_class()
        e['Key1'] = 1
        e['Key2'] = 2

        self.assertListEqual(list(sorted(e)), ['Env', 'Key1', 'Key2'])

    def test_ObjToDict(self):
        e = _Env_class()
        e['Key1'] = 1
        e['Key2'] = 2
        self.assertDictEqual (e.dict, {'Key1':1, 'Env': e, 'Key2':2})

    def test_DictToObj(self):
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
