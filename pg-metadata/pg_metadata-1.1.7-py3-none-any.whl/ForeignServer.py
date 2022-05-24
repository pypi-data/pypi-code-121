#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP, ParseACL
from pg_metadata.Grant   import Grant
from pg_metadata.Owner   import Owner
from pg_metadata.Comment import Comment
from pg_metadata.DDL     import DDL

class ForeignServer(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Schema = "_foreign"

        self.Name = (data.get("server_name") or "").strip().lower()
        assert len(self.Name) > 0, \
            "Foreign server name is null"

        self.FDW = (data.get("fdw_name") or "").strip().lower()
        assert len(self.FDW) > 0, \
            "Foreign server FDW is null"

        self.Options = data.get("options")

        self.Owner = Owner(
            self.GetObjectName(),
            {
                "instance_type" : "SERVER",
                "instance_name" : self.Name,
                "owner_name"    : data.get("owner_name")
            }
        )

        self.Comment = Comment(
            self.GetObjectName(),
            {
                "instance_type" : self.GetTag(),
                "instance_name" : self.Name,
                "comment"       : data.get("comment")
            }
        )

        self.Grants = []
        for grant in ParseACL(data.get("acl"), self.Owner.Owner):
            grant["instance_type"] = self.GetTag()
            grant["instance_name"] = self.Name
            self.Grants.append(Grant(self.GetObjectName(), grant))

    def __str__(self):
        return self.Name

    def GetObjectType(self):
        return "foreign_server"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.Name)

    def GetTag(self):
        return "FOREIGN SERVER"

    def DDL_Drop(self):
        return "DROP SERVER IF EXISTS %s;" % (self.Name)

    def DDL_Create(self):
        r = ""
        r += "-- Server: {0}".format(self.Name)
        r += SEP + SEP
        r += "-- {0}".format(self.DDL_Drop())
        r += SEP + SEP
        r += "CREATE SERVER {0}".format(self.Name)
        r += SEP
        r += "FOREIGN DATA WRAPPER {0}".format(self.FDW)
        r += SEP
        r += "OPTIONS("
        r += SEP
        r += self.DDL_Options()
        r += SEP
        r += ");"
        r += SEP + SEP
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

    def DDL_Options(self):
        result = []

        for o in sorted(self.Options):
            o = o.split("=")
            if len(o) != 2:
                continue
            result.append("    %s = '%s'" % (o[0], o[1]))

        separator = ",%s" % (SEP)
        return separator.join(result)

    def GetPath(self):
        return [self.Schema]

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
