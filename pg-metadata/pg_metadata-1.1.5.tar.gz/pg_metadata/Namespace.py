#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP, ParseACL
from pg_metadata.Owner   import Owner
from pg_metadata.Comment import Comment
from pg_metadata.Grant   import Grant
from pg_metadata.DDL     import DDL

class Namespace(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = data.get("oid")
        assert (self.Oid or 0) > 0, \
            "Namespace oid is null"

        self.Name = (data.get("name") or "").strip()
        assert len(self.Name) > 0, \
            "Namespace name is null"

        self.Owner = Owner(
            self.GetObjectName(),
            {
                "instance_type" : self.GetTag(),
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
        return "schema"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return self.Name

    def GetTag(self):
        return "SCHEMA"

    def DDL_Drop(self):
        return "DROP SCHEMA IF EXISTS %s;" % (self.GetFullName())

    def DDL_Create(self):
        r = ""
        r += "-- Schema: %s" % (self.GetFullName())
        r += SEP + SEP
        r += "-- %s" % (self.DDL_Drop())
        r += SEP + SEP
        r += "CREATE SCHEMA %s;" % (self.GetFullName())
        r += SEP + SEP
        r += self.Owner.DDL_Create()
        r += SEP + SEP

        for grant in self.Grants:
            r += grant.DDL_Create()
            r += SEP
        r += SEP

        if self.Comment.IsExists:
            r += self.Comment.DDL_Create()
            r += SEP

        return r.strip() + SEP

    def GetPath(self):
        return [self.GetFullName()]

    def GetFileName(self):
        return "{0}.sql".format(self.GetFullName())

    def Export(self):
        result = {}
        result[self.GetObjectName()] = self
        result[self.Comment.GetObjectName()] = self.Comment
        result[self.Owner.GetObjectName()] = self.Owner
        for g in self.Grants:
            result[g.GetObjectName()] = g
        return result
