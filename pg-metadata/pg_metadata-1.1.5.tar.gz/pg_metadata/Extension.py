#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP
from pg_metadata.DDL     import DDL

class Extension(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = data.get("oid")
        assert (self.Oid or 0) > 0, \
            "Extension oid is null"

        self.Schema = (data.get("schema") or "").strip()
        assert len(self.Schema) > 0, \
            "Extension schema is null"

        self.Name = (data.get("name") or "").strip()
        assert len(self.Name) > 0, \
            "Extension name is null"

        self.Version = (data.get("version") or "").strip()
        assert len(self.Version) > 0, \
            "Extension version is null"

        self.Owner = (data.get("owner") or "").strip()
        assert len(self.Owner) > 0, \
            "Extension owner is null"

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        return "extension"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return "{0}".format(self.Name)

    def GetTag(self):
        return "EXTENSION"

    def DDL_Drop(self):
        return "DROP {0} IF EXISTS {1};".format(self.GetTag(), self.GetFullName())

    def DDL_Create(self):
        r = ""
        r += "-- Extension: {0}".format(self.GetFullName()) + SEP
        r += SEP
        r += "-- {0}".format(self.DDL_Drop()) + SEP
        r += SEP
        r += "SET ROLE {0};".format(self.Owner) + SEP
        r += SEP
        r += "CREATE {0} {1}".format(self.GetTag(), self.GetFullName()) + SEP
        r += '  SCHEMA "{0}"'.format(self.Schema) + SEP
        r += '  VERSION "{0}"'.format(self.Version) + SEP
        r = r.strip() + ";"
        return r.strip() + SEP

    def GetPath(self):
        return ["_extension"]

    def GetFileName(self):
        return "{0}.sql".format(self.Name)

    def Export(self):
        return { self.GetObjectName() : self }

    def Diff(self, another):
        if self.DDL_Create() != another.DDL_Create():
            return [
                another.DDL_Drop(),
                self.DDL_Create()
            ]

        return []
