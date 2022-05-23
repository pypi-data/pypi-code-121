#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP, ParseACL
from pg_metadata.Grant   import Grant
from pg_metadata.Owner   import Owner
from pg_metadata.Comment import Comment
from pg_metadata.DDL     import DDL

class ForeignTable(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Schema = (data.get("schema_name") or "").strip().lower()
        assert len(self.Schema) > 0, \
            "Foreign table schema is null"

        self.Name = (data.get("table_name") or "").strip().lower()
        assert len(self.Name) > 0, \
            "Foreign table name is null"

        self.Server = (data.get("server_name") or "").strip()
        assert len(self.Server) > 0, \
            "Foreign table server is null"

        self.Options = data.get("options")

        self.Columns = data.get("columns_list") or []
        assert len(self.Columns) > 0, \
            "Foreign table columns is null"

        self.Owner = Owner(
            self.GetObjectName(),
            {
                "instance_type" : self.GetTag(),
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

    def __str__(self):
        return self.Name

    def GetObjectType(self):
        return "foreign_server"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return "{0}.{1}".format(self.Schema, self.Name)

    def GetTag(self):
        return "FOREIGN TABLE"

    def DDL_Drop(self):
        return "DROP {0} IF EXISTS {1};".format(self.GetTag(), self.GetFullName())

    def DDL_Create(self):
        r = ""
        r += "-- Foreign Table: %s" % (self.GetFullName())
        r += SEP + SEP
        r += "-- %s" % (self.DDL_Drop())
        r += SEP + SEP
        r += "CREATE {0} {1}(".format(self.GetTag(), self.GetFullName())
        r += SEP
        r += self.DDL_Columns()
        r += SEP
        r += ")"
        r += SEP
        r += "SERVER %s" % (self.Server)
        r += SEP
        r += "OPTIONS("
        r += SEP
        r += self.DDL_Options()
        r += SEP
        r += ");"
        r += SEP + SEP

        if self.Owner.Owner is not None:
            r += self.Owner.DDL_Create()
            r += SEP

        for grant in self.Grants:
            r += grant.DDL_Create()
            r += SEP
        r += SEP

        if self.Comment.IsExists:
            r += SEP
            r += self.Comment.DDL_Create()
            r += SEP

        return r.strip() + SEP

    def DDL_Options(self):
        result = []

        for o in sorted(self.Options):
            o = o.split("=")
            if len(o) != 2:
                continue
            result.append("    %s '%s'" % (o[0], o[1]))

        separator = ",%s" % (SEP)
        return separator.join(result)

    def DDL_Columns(self):
        result = []
        for col in self.Columns:
            result.append("    %s" % (col))
        separator = ",%s" % (SEP)
        return separator.join(result)

    def GetPath(self):
        return [self.Schema, "foreign_table"]

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
