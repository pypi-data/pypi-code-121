#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP, ParseACL
from pg_metadata.Grant   import Grant
from pg_metadata.Owner   import Owner
from pg_metadata.Comment import Comment
from pg_metadata.DDL     import DDL

class Function(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = (data.get("oid") or 0)
        assert self.Oid > 0, \
            "Function oid is null"

        self.Schema = (data.get("schema") or "").strip()
        assert len(self.Schema) > 0, \
            "Function schema is null"

        self.Name = (data.get("proc") or "").strip()
        assert len(self.Name) > 0, \
            "Function name is null"

        self.ArgsInTypes = (data.get("args_in_types") or "").strip()

        self.NameWithParams = "{0}.{1}({2})".format(self.Schema, self.Name, self.ArgsInTypes)

        self.ArgsIn = (data.get("args_in") or "").strip()

        self.ArgsOut = (data.get("args_out") or "").strip()

        self.Cost = data.get("cost") or 0

        self.Rows = data.get("rows") or 0

        self.Language = (data.get("lang") or "").strip()
        assert len(self.Language) > 0, \
            "Function language is null"

        self.Volatility = (data.get("volatility") or "").strip()
        assert len(self.Volatility) > 0, \
            "Function volatility"

        self.HasDuplicate = data.get("has_duplicate") or False
        self.IsTrigger = data.get("is_trigger") or False

        self.Code = (data.get("code") or "").strip()
        assert len(self.Code) > 0, \
            "Function code is null"

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
        return "function"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        if self.HasDuplicate:
            return "{0}.{1}({2}).sql".format(self.Schema, self.Name, self.ArgsInTypes)
        else:
            return "{0}.{1}".format(self.Schema, self.Name)

    def GetTag(self):
        return "FUNCTION"

    def DDL_Drop(self):
        return "DROP FUNCTION {0}.{1}({2});".format(self.Schema, self.Name, self.ArgsInTypes)

    def DDL_ArgsIn(self):
        if len(self.ArgsIn or "") == 0:
            return "()" + SEP
        else:
            r = ""
            r += "("
            r += SEP
            r += "    %s" % (self.ArgsIn.replace(",", ",%s   " % (SEP)))
            r += SEP
            r += ")"
            r += SEP
            return r

    def DDL_Create(self):
        r = ""
        r += "-- Function: {0}.{1}({2})".format(self.Schema, self.Name, self.ArgsInTypes)
        r += SEP
        r += SEP
        r += "-- %s" % (self.DDL_Drop())
        r += SEP
        r += SEP
        r += "CREATE OR REPLACE FUNCTION %s.%s" % (self.Schema, self.Name)
        r += self.DDL_ArgsIn()
        r += "RETURNS %s AS" % (self.ArgsOut)
        r += SEP
        r += "$BODY$"
        r += SEP
        r += self.Code
        r += SEP
        r += "$BODY$"
        r += SEP
        r += "  LANGUAGE %s %s" % (self.Language, self.Volatility)

        if self.Cost > 0:
            r += SEP
            r += "  COST %s" % (int(self.Cost))

        if self.Rows > 0:
            r += SEP
            r += "  ROWS %s" % (int(self.Rows))

        r += ";"
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
        return [self.Schema, "triggers" if self.IsTrigger else "functions"]

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
