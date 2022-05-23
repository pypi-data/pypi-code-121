#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP
from pg_metadata.DDL     import DDL
from pg_metadata.Owner   import Owner

class Publication(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = data.get("oid")
        assert (self.Oid or 0) > 0, \
            "Publication oid is null"

        self.Name = (data.get("name") or "").strip()
        assert len(self.Name) > 0, \
            "Publication name is null"

        self.IsViaRoot = bool(data.get("is_via_root") or False)
        self.IsAllTables = bool(data.get("is_all_tables") or False)

        self.Actions = (data.get("actions") or "").strip()
        assert len(self.Actions) > 0, \
            "Publication actions is null"

        self.Tables = (data.get("tables") or [])
        assert self.IsAllTables or len(self.Tables) > 0, \
            "Publication tables is null"

        self.Owner = Owner(
            self.GetObjectName(),
            {
                "instance_type" : self.GetTag(),
                "instance_name" : self.GetFullName(),
                "owner_name"    : data.get("owner")
            }
        )

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        return "publication"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return self.Name

    def GetTag(self):
        return "PUBLICATION"

    def DDL_Drop(self):
        return "DROP {0} IF EXISTS {1};".format(self.GetTag(), self.GetFullName())

    def DDL_Create(self):
        r = ""
        r += "-- Publication: {0}".format(self.GetFullName()) + SEP
        r += SEP
        r += "-- {0}".format(self.DDL_Drop()) + SEP
        r += SEP
        r += "CREATE {0} {1}".format(self.GetTag(), self.GetFullName())

        if self.IsAllTables:
            r += " FOR ALL TABLES"
        else:
            r += " FOR TABLE" + SEP
            r += ",{0}".format(SEP).join(["  {0}".format(t) for t in self.Tables])
        r += SEP

        r += "WITH (" + SEP
        r += "  publish = '{0}',".format(self.Actions) + SEP
        r += "  publish_via_partition_root = {0}".format(str(self.IsViaRoot).upper()) + SEP
        r += ");" + SEP

        r += SEP
        r += self.Owner.DDL_Create() + SEP

        return r.strip() + SEP

    def GetPath(self):
        return ["_logical"]

    def GetFileName(self):
        return "{0}.sql".format(self.Name)

    def Export(self):
        result = {}
        result[self.GetObjectName()] = self
        result[self.Owner.GetObjectName()] = self.Owner
        return result

    def Diff(self, another):
        result = []

        if self.IsViaRoot != another.IsViaRoot:
            result.append("ALTER {0} {1} SET(publish_via_partition_root = {2});".format(
                self.GetTag(), self.GetFullName(), str(self.IsViaRoot).upper()))

        if self.Actions != another.Actions:
            result.append("ALTER {0} {1} SET(publish = '{2}');".format(
                self.GetTag(), self.GetFullName(), self.Actions))

        if self.Tables != another.Tables:
            result.append("ALTER {0} {1} SET TABLE {2};".format(
                self.GetTag(), self.GetFullName(), ", ".join(self.Tables)))

        return result
