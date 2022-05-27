# This file is placed in the Public Domain.


"object tests"


import os
import unittest


from bot.obj import Config, Db, fns, hook, load, last, save
from bot.obj import cdir, edit, format, register
from bot.obj import Object, get, items, keys, update, values


import bot.obj


Config.workdir = ".test"


attrs1 = (
        'Class',
        'Config',
        'Db',
        'Object',
        'ObjectDecoder',
        'ObjectEncoder',
        'all',
        'clear',
        'copy',
        'diff',
        'dump',
        'dumps',
        'edit',
        'find',
        'format',
        'fromkeys',
        'get',
        'items',
        'keys',
        'last',
        'load',
        'loads',
        'pop',
        'popitem',
        'read',
        "register",
        'save',
        'search',
        'setdefault',
        'update',
        'values'
)


attrs2 = (
    '__class__',
    '__class_getitem__',
    '__contains__',
    '__delattr__',
    '__delitem__',
    '__dict__',
    '__dir__',
    '__doc__',
    '__eq__',
    '__format__',
    '__ge__',
    '__getattribute__',
    '__getitem__',
    '__gt__',
    '__hash__',
    '__init__',
    '__init_subclass__',
    '__ior__',
    '__iter__',
    '__le__',
    '__len__',
    '__lt__',
    '__module__',
    '__ne__',
    '__new__',
    '__oqn__',
    '__otype__',
    '__reduce__',
    '__reduce_ex__',
    '__repr__',
    '__reversed__',
    '__ror__',
    '__setattr__',
    '__setitem__',
    '__sizeof__',
    '__slots__',
    '__stp__',
    '__str__',
    '__subclasshook__'
)


class Test_Object(unittest.TestCase):

    def test_import(self):
        self.assertEqual(tuple(dir(bot.obj)), attrs1)

    def test_attributes(self):
        o = Object()
        self.assertEqual(tuple(dir(o)), attrs2)

    def test_Object(self):
        o = Object()
        self.assertTrue(type(o), Object)

    def test_Object__class__(self):
        o = Object()
        o.__class__
        oo = o.__class__()
        self.assertTrue("Object" in str(type(oo)))

    def test_Object__contains__(self):
        o = Object()
        o.key = "value"
        self.assertTrue("key" in o)

    def test_Object__delattr__(self):
        o = Object()
        o.key = "value"
        o.__delattr__("key")
        self.assertTrue("key" not in o)

    def test_Object__delitem__(self):
        o = Object()
        o["key"] = "value"
        o.__delitem__("key")
        self.assertTrue("key" not in o)

    def test_Object__dict__(self):
        o = Object()
        self.assertEqual(o.__dict__, {})

    def test_Object__dir__(self):
        o = Object()
        self.assertEqual(
            dir(o), list(attrs2)
        )

    def test_Object__doc__(self):
        o = Object()
        self.assertEqual(o.__doc__, None)

    def test_Object__eq__(self):
        o = Object()
        oo = Object()
        self.assertTrue(o == oo)

    def test_Object__format__(self):
        o = Object()
        self.assertEqual(o.__format__(""), "{}")

    def test_Object__ge__(self):
        o = Object()
        oo = Object()
        oo.key = "value"
        self.assertTrue(oo >= o)

    def test_Object__getattribute__(self):
        o = Object()
        o.key = "value"
        self.assertEqual(o.__getattribute__("key"), "value")

    def test_Object__getitem__(self):
        o = update(Object(), {"key": "value"})
        self.assertEqual(o.__getitem__("key"), "value")

    def test_Object___gt__(self):
        o = Object()
        oo = Object()
        oo.key = "value"
        self.assertTrue(oo > o)

    def test_Object__hash__(self):
        o = Object()
        h = hash(o)
        self.assertTrue(isinstance(h, int))

    def test_Object__init__(self):
        o = Object()
        self.assertTrue(type(Object.__init__(o)), Object)

    def test_Object__init_subclass__(self):
        o = Object()
        scls = o.__init_subclass__()
        self.assertEqual(scls, None)

    def test_Object__iter__(self):
        o = Object()
        o.key = "value"
        self.assertTrue(
            list(o.__iter__()),
            [
                "key",
            ],
        )

    def test_Object__le__(self):
        o = Object()
        oo = Object()
        oo.key = "value"
        self.assertTrue(o <= oo)

    def test_Object__len__(self):
        o = Object()
        self.assertEqual(len(o), 0)

    def test_Object__lt__(self):
        o = Object()
        oo = Object()
        oo.key = "value"
        self.assertTrue(o < oo)

    def test_Object__module__(self):
        self.assertTrue(Object().__module__, "bot.obj")

    def test_Object__ne__(self):
        o = Object()
        oo = Object()
        oo.key = "value"
        self.assertTrue(o != oo)

    def test_Object__new__(self):
        o = Object()
        oo = o.__new__(Object)
        self.assertEqual(o, oo)

    def test_Object__otype__(self):
        self.assertEqual(Object().__otype__, "bot.obj.Object")

    def test_Object__reduce__(self):
        o = Object()
        o.__reduce__()
        
    def test_Object__reduce_ex__(self):
        o = Object()
        o.__reduce__()

    def test_Object__repr__(self):
        self.assertTrue(update(Object(),
                               {"key": "value"}).__repr__(), {"key": "value"})

    def test_Object__setattr__(self):
        o = Object()
        o.__setattr__("key", "value")
        self.assertTrue(o.key, "value")

    def test_Object__setitem__(self):
        o = Object()
        o.__setitem__("key", "value")
        self.assertTrue(o["key"], "value")

    def test_Object__sizeof__(self):
        self.assertEqual(Object().__sizeof__(), 40)

    def test_Object__slots__(self):
        self.assertEqual(Object().__slots__, ("__dict__",
                                              "__otype__",
                                              "__stp__"))

    def test_Object__stp__(self):
        o = Object()
        self.assertTrue("bot.obj.Object" in o.__stp__)

    def test_Object__str__(self):
        o = Object()
        self.assertEqual(str(o), "{}")

    def test_Object__subclasshook__(self):
        o = Object()
        b = o.__subclasshook__()
        self.assertEqual(b, NotImplemented)

    def test_Db(self):
        db = Db()
        self.assertTrue(type(db), Db)

    def test_cdir(self):
        cdir(".test")
        self.assertTrue(os.path.exists(".test"))

    def test_edit(self):
        o = Object()
        d = {"key": "value"}
        edit(o, d)
        self.assertEqual(o.key, "value")

    def test_format(self):
        o = Object()
        self.assertEqual(format(o), "")

    def test_fns(self):
        from bot.obj import Config, Object, save
        Config.workdir = ".test"
        o = Object()
        save(o)
        self.assertTrue("Object" in fns("bot.obj.Object")[0])

    def test_get(self):
        o = Object()
        o.key = "value"
        self.assertEqual(get(o, "key"), "value")

    def test_hook(self):
        o = Object()
        o.key = "value"
        p = save(o)
        oo = hook(p)
        self.assertEqual(oo.key, "value")

    def test_keys(self):
        o = Object()
        o.key = "value"
        self.assertEqual(
            list(keys(o)),
            [
                "key",
            ],
        )

    def test_items(self):
        o = Object()
        o.key = "value"
        self.assertEqual(
            list(items(o)),
            [
                ("key", "value"),
            ],
        )

    def test_last(self):
        o = Object()
        o.key = "value"
        save(o)
        last(o)
        self.assertEqual(o.key, "value")

    def test_load(self):
        o = Object()
        o.key = "value"
        p = save(o)
        oo = Object()
        load(oo, p)
        self.assertEqual(oo.key, "value")

    def test_register(self):
        o = Object()
        register(o, "key", "value")
        self.assertEqual(o.key, "value")

    def test_save(self):
        Config.workdir = ".test"
        o = Object()
        p = save(o)
        self.assertTrue(os.path.exists(os.path.join(Config.workdir, "store", p)))

    def test_update(self):
        o = Object()
        o.key = "value"
        oo = Object()
        update(oo, o)
        self.assertTrue(oo.key, "value")
        pass

    def test_values(self):
        o = Object()
        o.key = "value"
        self.assertEqual(
            list(values(o)),
            [
                "value",
            ],
        )
