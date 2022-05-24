#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System     import SEP, ParseACL
from pg_metadata.Grant      import Grant
from pg_metadata.Owner      import Owner
from pg_metadata.Comment    import Comment
from pg_metadata.DDL        import DDL
from pg_metadata.TableIndex import TableIndex

class View(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.IsMaterialized = data.get("is_materialized")
        self.IsMaterialized = self.IsMaterialized if self.IsMaterialized is not None else False

        self.Oid = data.get("oid")
        assert (self.Oid or 0) > 0, \
            "View oid is null"

        self.Schema = (data.get("schema") or "").strip().lower()
        assert len(self.Schema) > 0, \
            "View schema is null"

        self.Name = (data.get("name") or "").strip().lower()
        assert len(self.Name) > 0, \
            "View name is null"

        self.Definition = (data.get("definition") or "").strip()
        assert len(self.Definition) > 0, \
            "View definition is null"

        self.Owner = Owner(
            self.GetObjectName(),
            {
                "instance_type" : "TABLE",
                "instance_name" : self.GetFullName(),
                "owner_name"    : data.get("owner_name")
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
            grant["instance_type"] = "TABLE"
            grant["instance_name"] = self.GetFullName()
            self.Grants.append(Grant(self.GetObjectName(), grant))

        self.Indexes = []
        for idx in (data.get("indexes") or []):
            idx["schema"] = self.Schema
            idx["table"] = self.Name
            idx = TableIndex(self.GetObjectName(), idx)
            self.Indexes.append(idx)

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        if self.IsMaterialized:
            return "matview"
        else:
            return "view"

    def GetObjectName(self):
        return "{0}_{1}.{2}".format(self.GetObjectType(), self.Schema, self.Name)

    def GetFullName(self):
        return "{0}.{1}".format(self.Schema, self.Name)

    def GetTag(self):
        return "MATERIALIZED VIEW" if self.IsMaterialized else "VIEW"

    def DDL_Drop(self):
        if self.IsMaterialized:
            return "DROP MATRIALIZED VIEW IF EXISTS %s;" % (self.GetFullName())
        else:
            return "DROP VIEW IF EXISTS %s;" % (self.GetFullName())

    def DDL_Create(self):
        r = ""
        r += self.DDL_Drop()
        r += SEP + SEP
        if self.IsMaterialized:
            r += "CREATE MATERIALIZED VIEW %s AS" % (self.GetFullName())
        else:
            r += "CREATE OR REPLACE VIEW %s AS" % (self.GetFullName())
        r += SEP
        r += self.Definition
        r += SEP + SEP
        r += self.Owner.DDL_Create()
        r += SEP

        for grant in self.Grants:
            r += grant.DDL_Create()
            r += SEP
        r += SEP

        if self.Comment.IsExists:
            r += self.Comment.DDL_Create()
            r += SEP + SEP

        for ind in sorted(self.Indexes, key=lambda x: x.GetFullName()):
            r += ind.DDL_Create("%s  " % (SEP))
            r += SEP + SEP

        return r.strip() + SEP

    def GetPath(self):
        return [self.Schema, "view"]

    def GetFileName(self):
        return "{0}.sql".format(self.Name)

    def Export(self):
        result = {}
        result[self.GetObjectName()] = self
        result[self.Comment.GetObjectName()] = self.Comment
        result[self.Owner.GetObjectName()] = self.Owner
        for v in self.Grants:
            result[v.GetObjectName()] = v
        for v in self.Indexes:
            result[v.GetObjectName()] = v
        return result

    def Diff(self, another):
        if self.Definition != another.Definition:
            return [
                another.DDL_Drop(),
                self.DDL_Create()
            ]
