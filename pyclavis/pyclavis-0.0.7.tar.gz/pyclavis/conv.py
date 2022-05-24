import json

from .credit import Credential

TAB = "\t"


class Conv(object):
    def decode(self, s):
        raise NotImplementedError

    def encode(self, c):
        raise NotImplementedError


class ConvTabCsv(Conv):

    """converts to csv format, separator is TAB"""

    def decode(self, s):
        if s.find(TAB) < 0:
            raise Exception("invalid format")
        c = Credential(*s.split(TAB))
        if c.category != None:
            if len(c.category) == 0 or c.category.lower() == "none":
                c.category = None
        return c

    def encode(self, c):
        self._check(c)
        return TAB.join([c.name, c.user, c.passwd, str(c.category)])

    def _check(self, c):
        for n, v in c.__dict__.items():
            if v != None and v.find(TAB) >= 0:
                raise Exception("tab not allowed: " + n)


class ConvJson(Conv):

    """
    converts to json and back.
    each credential in a single row as json.
    no multiline json.
    """

    def decode(self, s):
        para = json.loads(s)
        c = Credential()
        c.__dict__.update(para)
        return c

    def encode(self, c):
        s = json.dumps(c.__dict__)
        return s
