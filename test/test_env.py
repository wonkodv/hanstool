import unittest

from ht3.env import Env_class

class EnvTest(unittest.TestCase):
    def test_containsSelf(self):
        e = Env_class()
        self.assertIs(e , e.Env)
        self.assertIs(e , e['Env'])

    def test_asDict(self):
        e = Env_class()
        e['key'] = 1
        e['key2']= 2
        self.assertEqual(e['key'],1)
        self.assertEqual(e['key2'],2)

    def test_asNameSpace(self):
        e = Env_class()
        e.Attr1 = 1
        setattr(e, 'Attr2', 2)

        self.assertEqual(e.Attr1, 1)
        self.assertEqual(e.Attr2, 2)

    def test_iter(self):
        e = Env_class()
        e.Attr1 = 1
        e['Key2'] = 2

        self.assertListEqual(list(sorted(iter(e))), ['Attr1', 'Env', 'Key2'])

    def test_ObjToDict(self):
        e = Env_class()
        e.Attr1 = 1
        e['Key2'] = 2
        self.assertDictEqual (e.dict, {'Attr1':1, 'Env': e, 'Key2':2})

    def test_DictToObj(self):
        e = Env_class()
        e.dict['Key3'] = 3

        self.assertEqual(e.Key3, 3)
