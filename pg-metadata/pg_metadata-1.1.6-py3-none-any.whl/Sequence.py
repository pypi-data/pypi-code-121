#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP, ParseACL
from pg_metadata.DDL     import DDL
from pg_metadata.Grant   import Grant
from pg_metadata.Owner   import Owner
from pg_metadata.Comment import Comment

class Sequence(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = data.get("oid")
        assert (self.Oid or 0) > 0, \
            "Sequence oid is null"

        self.Schema = (data.get("schema") or "").strip()
        assert len(self.Schema) > 0, \
            "Sequence schema is null"

        self.Name = (data.get("name") or "").strip()
        assert len(self.Name) > 0, \
            "Sequence name is null"

        self.Increment = int(data.get("increment") or 0)
        assert self.Increment != 0, \
            "Sequence increment is null"

        self.MinValue = int(data.get("minimum_value") or 0)
        self.MaxValue = int(data.get("maximum_value") or 0)

        self.IsCycle = "  CYCLE" if data.get("is_cycle") is True else "  NO CYCLE"

        self.Cache = (data.get("cache") or 0)
        assert self.Cache > 0, \
            "Sequence cache is null"

        self.Owner = Owner(
            self.GetObjectName(),
            {
                "instance_type" : "TABLE",
                "instance_name" : self.GetFullName(),
                "owner_name"    : data.get("owner")
            }
        )

        self.Comment = Comment(
            self.GetObjectName(),
            {
                "instance_type" : self.GetTag(),
                "instance_name" : self.GetFullName(),
                "comment"       : data.get("comment")
            }
        )

        self.Grants = []
        for grant in ParseACL(data.get("acl"), self.Owner.Owner):
            grant["instance_type"] = self.GetTag()
            grant["instance_name"] = self.GetFullName()
            self.Grants.append(Grant(self.GetObjectName(), grant))

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        return "sequence"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return "{0}.{1}".format(self.Schema, self.Name)

    def GetTag(self):
        return "SEQUENCE"

    def DDL_Drop(self):
        return "DROP SEQUENCE IF EXISTS %s;" % (self.GetFullName())

    def DDL_Create(self):
        r = ""
        r += "-- Sequence: %s" % (self.GetFullName())
        r += SEP
        r += SEP
        r += "-- %s" % (self.DDL_Drop())
        r += SEP
        r += SEP
        r += "CREATE SEQUENCE %s" % (self.GetFullName())
        r += SEP
        r += "  INCREMENT %s" % (self.Increment)
        r += SEP
        r += "  MINVALUE %s" % (self.MinValue)
        r += SEP
        r += "  MAXVALUE %s" % (self.MaxValue)
        r += SEP
        r += "  START %s" % (1)
        r += SEP
        r += "  CACHE %s" % (self.Cache)
        r += SEP
        r += self.IsCycle
        r = r.strip() + ";"
        r += SEP
        r += SEP
        r += self.Owner.DDL_Create()
        r += SEP

        for grant in self.Grants:
            r += grant.DDL_Create()
            r += SEP
        r += SEP

        if self.Comment.IsExists:
            r += self.Comment.DDL_Create()
            r += SEP

        return r.strip() + SEP

    def GetPath(self):
        return [self.Schema, "sequence"]

    def GetFileName(self):
        return "{0}.sql".format(self.Name)

    def Export(self):
        result = {}
        result[self.GetObjectName()] = self
        result[self.Comment.GetObjectName()] = self.Comment
        result[self.Owner.GetObjectName()] = self.Owner
        for v in self.Grants:
            result[v.GetObjectName()] = v
        return result

    def Diff(self, another):
        result = []

        if self.Cache != another.Cache:
            result.append("CACHE {0}".format(self.Cache))

        if self.Increment != another.Increment:
            result.append("INCREMENT BY {0}".format(self.Increment))

        if self.IsCycle != another.IsCycle:
            result.append(self.IsCycle)

        if self.MinValue != another.MinValue:
            result.append("MINVALUE {0}".format(self.MinValue))

        if self.MaxValue != another.MaxValue:
            result.append("MAXVALUE {0}".format(self.MaxValue))

        if len(result) > 0:
            return [
                "ALTER {0} {1} {2}".format(self.GetTag(), self.GetFullName(), " ".join(result))
            ]
        else:
            return []
