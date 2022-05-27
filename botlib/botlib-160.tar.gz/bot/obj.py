# This file is placed in the Public Domain.


"object"


import copy as copying
import datetime
import json
import os
import pathlib
import time
import uuid
import _thread


def __dir__():
    return (
        'Class',
        'Config',
        'Db',
        'Object',
        'ObjectDecoder',
        'ObjectEncoder',
        'allfns',
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


dblock = _thread.allocate_lock()


class ENOPATH(Exception):

    pass


class Class():

    cls = {}

    @staticmethod
    def add(clz):
        Class.cls["%s.%s" % (clz.__module__, clz.__name__)] =  clz

    @staticmethod
    def full(name):
        name = name.lower()
        res = []
        for cln in Class.cls:
            if cln.split(".")[-1].lower() == name:
                res.append(cln)
        return res

    @staticmethod
    def get(nm):
        return Class.cls.get(nm, None)


class Object:

    __slots__ = (
        "__dict__",
        "__otype__",
        "__stp__",
    )

    def __init__(self):
        object.__init__(self)
        self.__otype__ = str(type(self)).split()[-1][1:-2]
        self.__stp__ = os.path.join(
            self.__otype__,
            str(uuid.uuid4()),
            os.sep.join(str(datetime.datetime.now()).split()),
        )

    def __class_getitem__(cls):
        return cls.__dict__.__class_geitem__(cls)

    def __contains__(self, k):
        if k in self.__dict__.keys():
            return True
        return False

    def __delitem__(self, k):
        if k in self:
            del self.__dict__[k]

    def __eq__(self, o):
        return len(self.__dict__) == len(o.__dict__)

    def __getitem__(self, k):
        return self.__dict__[k]

    def __ior__(self, o):
        return self.__dict__.__ior__(o)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __le__(self, o):
        return len(self) <= len(o)

    def __lt__(self, o):
        return len(self) < len(o)

    def __ge__(self, o):
        return len(self) >= len(o)

    def __gt__(self, o):
        return len(self) > len(o)

    def __hash__(self):
        return id(self)

    def __ne__(self, o):
        return len(self.__dict__) != len(o.__dict__)

    def __reduce__(self):
        pass

    def __reduce_ex__(self, k):
        pass

    def __reversed__(self):
        return self.__dict__.__reversed__()

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __oqn__(self):
        return "<%s.%s object at %s>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self)),
        )

    def __ror__(self, o):
        return self.__dict__.__ror__(o)

    def __str__(self):
        return str(self.__dict__)


class Config(Object):

    debug = False
    name = "bot"
    verbose = False
    workdir = None


class ObjectDecoder(json.JSONDecoder):

    ""

    def decode(self, s, _w=None):
        ""
        v = json.loads(s)
        o = Object()
        update(o, v)
        return o


class ObjectEncoder(json.JSONEncoder):

    ""

    def default(self, o):
        ""
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        if isinstance(o,
                      (type(str), type(True), type(False),
                       type(int), type(float))):
            return o
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return str(o)


class Db(Object):

    names = Object()

    def all(self, otype, timed=None):
        nr = -1
        result = []
        for fn in fns(otype, timed):
            o = hook(fn)
            if "_deleted" in o and o._deleted:
                continue
            nr += 1
            result.append((fn, o))
        if not result:
            return []
        return result

    def find(self, otype, selector=None, index=None, timed=None):
        if selector is None:
            selector = {}
        nr = -1
        result = []
        for fn in fns(otype, timed):
            o = hook(fn)
            if selector and not search(o, selector):
                continue
            if "_deleted" in o and o._deleted:
                continue
            nr += 1
            if index is not None and nr != index:
                continue
            result.append((fn, o))
        if not result:
            return []
        return result

    def lastmatch(self, otype, selector=None, index=None, timed=None):
        db = Db()
        res = sorted(db.find(otype, selector, index, timed),
                     key=lambda x: fntime(x[0]))
        if res:
            return res[-1]
        return (None, None)

    def lasttype(self, otype):
        fnn = fns(otype)
        if fnn:
            return hook(fnn[-1])
        return None

    def lastfn(self, otype):
        fn = fns(otype)
        if fn:
            fnn = fn[-1]
            return (fnn, hook(fnn))
        return (None, None)

    def remove(self, otype, selector=None):
        has = []
        for _fn, o in self.find(otype, selector or {}):
            o._deleted = True
            has.append(o)
        for o in has:
            save(o)
        return has

    @staticmethod
    def types():
        assert Config.workdir
        path = os.path.join(Config.workdir, "store")
        if not os.path.exists(path):
            return []
        return sorted(os.listdir(path))


def allfns(timed=None):
    assert Config.workdir
    p = os.path.join(Config.workdir, "store")
    for name in os.listdir(p):
        for fn in fns(name):
            yield fn


def cdir(path):
    if os.path.exists(path):
        return
    if path.split(os.sep)[-1].count(":") == 2:
        path = os.path.dirname(path)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def locked(obj):

    def lockeddec(func, *args, **kwargs):
        def lockedfunc(*args, **kwargs):
            obj.acquire()
            res = None
            try:
                res = func(*args, **kwargs)
            finally:
                obj.release()
            return res

        lockedfunc.__wrapped__ = func
        return lockedfunc

    return lockeddec


def fntime(daystr):
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.split(".")[0]
    return time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))


@locked(dblock)
def fns(name, timed=None):
    if not name:
        return []
    assert Config.workdir
    p = os.path.join(Config.workdir, "store", name) + os.sep
    if not os.path.exists(p):
        return []
    res = []
    d = ""
    for rootdir, dirs, _files in os.walk(p, topdown=False):
        if dirs:
            d = sorted(dirs)[-1]
            if d.count("-") == 2:
                dd = os.path.join(rootdir, d)
                fls = sorted(os.listdir(dd))
                if fls:
                    p = os.path.join(dd, fls[-1])
                    if (
                        timed
                        and "from" in timed
                        and timed["from"]
                        and fntime(p) < timed["from"]
                    ):
                        continue
                    if timed and timed.to and fntime(p) > timed.to:
                        continue
                    res.append(p)
    return sorted(res, key=fntime)


@locked(dblock)
def hook(hfn):
    if hfn.count(os.sep) > 3:
        oname = hfn.split(os.sep)[-4:]
    else:
        oname = hfn.split(os.sep)
    cname = oname[0]
    cls = Class.get(cname)
    if cls:
        o = cls()
    else:
        o = Object()
    fn = os.sep.join(oname)
    load(o, fn)
    return o


def listfiles(workdir):
    path = os.path.join(workdir, "store")
    if not os.path.exists(path):
        return []
    return sorted(os.listdir(path))


def spl(txt):
    return [x for x in txt.split(",") if x]


def clear(o):
    o.__dict__ = {}


def copy(o):
    return copying.copy(o)


def diff(o1, o2):
    d = Object()
    for k in keys(o2):
        if k in keys(o1) and o1[k] != o2[k]:
            d[k] = o2[k]
    return d



def dump(o, opath):
    cdir(opath)
    with open(opath, "w", encoding="utf-8") as ofile:
        json.dump(
            o.__dict__, ofile, cls=ObjectEncoder, indent=4, sort_keys=True
        )
    return o.__stp__


def dumps(o):
    return json.dumps(o, cls=ObjectEncoder)


def edit(o, setter):
    for key, v in items(setter):
        register(o, key, v)



def find(name, selector=None, index=None, timed=None, names=None):
    db = Db()
    if not names:
        names = Class.full(name)
    for n in names:
        for fn, o in db.find(n, selector, index, timed):
            yield fn, o


def format(o, args="", skip="_", empty=False, plain=False, **kwargs):
    res = []
    if args:
        ks = spl(args)
    else:
        ks = keys(o)
    for k in ks:
        if k in spl(skip) or k.startswith("_"):
            continue
        v = getattr(o, k, None)
        if not v and not empty:
            continue
        txt = ""
        if plain:
            txt = str(v)
        elif isinstance(v, str) and len(v.split()) >= 2:
            txt = '%s="%s"' % (k, v)
        else:
            txt = '%s=%s' % (k, v)
        res.append(txt)
    return " ".join(res)


def fromkeys(iterable, value=None):
    o = Object()
    for i in iterable:
        o[i] = value
    return o


def get(o, key, default=None):
    return o.__dict__.get(key, default)


def items(o):
    try:
        return o.__dict__.items()
    except AttributeError:
        return o.items()


def keys(o):
    try:
        return o.__dict__.keys()
    except (AttributeError, TypeError):
        return o.keys()


def last(o):
    db = Db()
    path, obj = db.lastfn(o.__otype__)
    if obj:
        update(o, obj)
    if path:
        splitted = path.split(os.sep)
        stp = os.sep.join(splitted[-4:])
        return stp
    return None


def load(o, opath):
    if opath.count(os.sep) != 3:
        raise ENOPATH(opath)
    assert Config.workdir
    splitted = opath.split(os.sep)
    stp = os.sep.join(splitted[-4:])
    lpath = os.path.join(Config.workdir, "store", stp)
    if os.path.exists(lpath):
        with open(lpath, "r", encoding="utf-8") as ofile:
            d = json.load(ofile, cls=ObjectDecoder)
            update(o, d)
    o.__stp__ = stp
    return o.__stp__


def loads(s):
    return json.loads(s, cls=ObjectDecoder)


def pop(o, k, d=None):
    try:
        return o[k]
    except KeyError as ex:
        if d:
            return d
        raise KeyError from ex


def popitem(o):
    k = keys(o)
    if k:
        v = o[k]
        del o[k]
        return (k, v)
    raise KeyError


def register(o, k, v):
    setattr(o, k, v)


def save(o):
    assert Config.workdir
    prv = os.sep.join(o.__stp__.split(os.sep)[:2])
    o.__stp__ = os.path.join(prv,
                             os.sep.join(str(datetime.datetime.now()).split()))
    opath = os.path.join(Config.workdir, "store", o.__stp__)
    dump(o, opath)
    os.chmod(opath, 0o444)
    return o.__stp__


def search(o, s):
    ok = False
    for k, v in items(s):
        vv = getattr(o, k, None)
        if v not in str(vv):
            ok = False
            break
        ok = True
    return ok


def setdefault(o, key, default=None):
    if key not in o:
        o[key] = default
    return o[key]


def update(o, data):
    try:
        o.__dict__.update(vars(data))
    except TypeError:
        o.__dict__.update(data)
    return o


def values(o):
    try:
        return o.__dict__.values()
    except TypeError:
        return o.values()
