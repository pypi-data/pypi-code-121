#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP
from pg_metadata.DDL     import DDL

class Cast(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = data.get("oid")
        assert (self.Oid or 0) > 0, \
            "Cast oid is null"

        self.TypeFrom = (data.get("type_from") or "").strip()
        assert len(self.TypeFrom) > 0, \
            "Cast type_from is null"

        self.TypeTo = (data.get("type_to") or "").strip()
        assert len(self.TypeTo) > 0, \
            "Cast type_to is null"

        self.Context = (data.get("context") or "").strip()
        assert len(self.Context) > 0, \
            "Cast context is null"

        self.Func = (data.get("func") or "").strip()

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        return "cast"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return "{0} AS {1}".format(self.TypeFrom, self.TypeTo)

    def GetTag(self):
        return "CAST"

    def DDL_Drop(self):
        return "DROP {0} IF EXISTS {1};".format(self.GetTag(), self.GetFullName())

    def DDL_Create(self):
        r = ""
        r += "-- Cast: {0}".format(self.GetFullName()) + SEP
        r += SEP
        r += "-- {0}".format(self.DDL_Drop()) + SEP
        r += SEP
        r += "CREATE {0} ({1})".format(self.GetTag(), self.GetFullName()) + SEP

        if len(self.Func) > 0:
            r += '  WITH FUNCTION {0}'.format(self.Func) + SEP
        else:
            r += '  WITHOUT FUNCTION' + SEP

        r += '  AS {0}'.format(self.Context) + SEP
        r = r.strip() + ";"
        return r.strip() + SEP

    def GetPath(self):
        return ["_cast"]

    def GetFileName(self):
        return "{0}.sql".format(self.GetFullName())

    def Export(self):
        return { self.GetObjectName() : self }

    def Diff(self, another):
        if self.DDL_Create() != another.DDL_Create():
            return [
                another.DDL_Drop(),
                self.DDL_Create()
            ]

        return []
