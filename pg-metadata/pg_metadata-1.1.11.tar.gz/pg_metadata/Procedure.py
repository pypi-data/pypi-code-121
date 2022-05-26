#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP, ParseACL
from pg_metadata.Grant   import Grant
from pg_metadata.Owner   import Owner
from pg_metadata.Comment import Comment
from pg_metadata.DDL     import DDL

class Procedure(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = (data.get("oid") or 0)
        assert self.Oid > 0, \
            "Procedure oid is null"

        self.Schema = (data.get("schema") or "").strip()
        assert len(self.Schema) > 0, \
            "Procedure schema is null"

        self.Name = (data.get("proc") or "").strip()
        assert len(self.Name) > 0, \
            "Procedure name is null"

        self.ArgsInTypes = (data.get("args_in_types") or "").strip()

        self.NameWithParams = "{0}.{1}({2})".format(self.Schema, self.Name, self.ArgsInTypes)

        self.ArgsIn = (data.get("args_in") or "").strip()

        self.Language = (data.get("lang") or "").strip()
        assert len(self.Language) > 0, \
            "Procedure language is null"

        self.HasDuplicate = data.get("has_duplicate") or False

        self.Code = (data.get("code") or "").strip()
        assert len(self.Code) > 0, \
            "Procedure code is null"

        self.Owner = Owner(
            self.GetObjectName(),
            {
                "instance_type" : self.GetTag(),
                "instance_name" : self.NameWithParams,
                "owner_name"    : data.get("owner")
            }
        )

        self.Comment = Comment(
            self.GetObjectName(),
            {
                "instance_type" : self.GetTag(),
                "instance_name" : self.NameWithParams,
                "comment"       : data.get("comment")
            }
        )

        self.Grants = []
        for grant in ParseACL(data.get("acl"), self.Owner.Owner):
            grant["instance_type"] = self.GetTag()
            grant["instance_name"] = self.NameWithParams
            self.Grants.append(Grant(self.GetObjectName(), grant))

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        return "procedure"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        if self.HasDuplicate:
            return "{0}.{1}({2}).sql".format(self.Schema, self.Name, self.ArgsInTypes)
        else:
            return "{0}.{1}".format(self.Schema, self.Name)

    def GetTag(self):
        return "PROCEDURE"

    def DDL_Drop(self):
        return "DROP {0} {1}.{2}({3});".format(self.GetTag(), self.Schema, self.Name, self.ArgsInTypes)

    def DDL_ArgsIn(self):
        if len(self.ArgsIn or "") == 0:
            return "()" + SEP
        else:
            r = "(" + SEP
            r += "    %s" % (self.ArgsIn.replace(",", ",%s   " % (SEP))) + SEP
            r += ") "
            return r

    def DDL_Create(self):
        r = ""
        r += "-- Procedure: {0}.{1}({2})".format(self.Schema, self.Name, self.ArgsInTypes) + SEP
        r += SEP
        r += "-- {0}".format(self.DDL_Drop()) + SEP
        r += SEP
        r += "CREATE OR REPLACE {0} {1}.{2}".format(self.GetTag(), self.Schema, self.Name)
        r += self.DDL_ArgsIn()
        r += 'LANGUAGE "{0}" AS'.format(self.Language) + SEP
        r += "$BODY$" + SEP
        r += self.Code + SEP
        r += "$BODY$;" + SEP
        r += SEP
        r += self.Owner.DDL_Create() + SEP

        for grant in self.Grants:
            r += grant.DDL_Create() + SEP
        r += SEP

        if self.Comment.IsExists:
            r += self.Comment.DDL_Create() + SEP

        return r.strip() + SEP

    def GetPath(self):
        return [self.Schema, "procedure"]

    def GetFileName(self):
        if self.HasDuplicate:
            return "{0}({1}).sql".format(self.Name, self.ArgsInTypes)
        else:
            return "{0}.sql".format(self.Name)

    def Export(self):
        result = {}
        result[self.GetObjectName()] = self
        result[self.Comment.GetObjectName()] = self.Comment
        result[self.Owner.GetObjectName()] = self.Owner
        for g in self.Grants:
            result[g.GetObjectName()] = g
        return result

    def Diff(self, another):
        if (
            self.ArgsIn     != another.ArgsIn     or
            self.ArgsOut    != another.ArgsOut    or
            self.Code       != another.Code       or
            self.Cost       != another.Cost       or
            self.Language   != another.Language   or
            self.Rows       != another.Rows       or
            self.Volatility != another.Volatility
        ):
            return [
                another.DDL_Drop(),
                self.DDL_Create()
            ]
        else:
            return []
