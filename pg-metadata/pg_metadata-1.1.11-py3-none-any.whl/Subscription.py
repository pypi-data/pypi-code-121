#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from pg_metadata.System  import SEP
from pg_metadata.DDL     import DDL
from pg_metadata.Owner   import Owner

class Subscription(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = data.get("oid")
        assert (self.Oid or 0) > 0, \
            "Subscription oid is null"

        self.Name = (data.get("name") or "").strip()
        assert len(self.Name) > 0, \
            "Subscription name is null"

        self.IsEnabled = bool(data.get("is_enabled") or False)

        self.Connect = (data.get("connect") or "").strip()
        assert len(self.Connect) > 0, \
            "Subscription connect is null"

        self.Slot = (data.get("slot") or "").strip()
        assert len(self.Slot) > 0, \
            "Subscription slot is null"

        self.SyncCommit = (data.get("sync_commit") or "").strip()
        assert len(self.SyncCommit) > 0, \
            "Subscription sync_commit is null"

        self.Publications = (data.get("publications") or [])
        assert len(self.Publications) > 0, \
            "Subscription publications is null"

        self.Tables = (data.get("tables") or [])

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
        return "subscription"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return self.Name

    def GetTag(self):
        return "SUBSCRIPTION"

    def DDL_Drop(self):
        return "DROP {0} IF EXISTS {1};".format(self.GetTag(), self.GetFullName())

    def DDL_Create(self):
        r = ""
        r += "-- Subscription: {0}".format(self.GetFullName()) + SEP
        r += SEP
        r += "-- {0}".format(self.DDL_Drop()) + SEP
        r += SEP
        r += "CREATE {0} {1}".format(self.GetTag(), self.GetFullName()) + SEP
        r += "CONNECTION '{0}'".format(self.Connect) + SEP
        r += "PUBLICATION {0}".format(", ".join(self.Publications)) + SEP
        r += "WITH (" + SEP
        r += "  enabled = {0},".format(str(self.IsEnabled).upper()) + SEP
        r += '  slot_name = "{0}",'.format(self.Slot) + SEP
        r += "  synchronous_commit = '{0}'".format(self.SyncCommit) + SEP
        r += ");" + SEP

        r += SEP
        r += self.Owner.DDL_Create() + SEP

        if len(self.Tables) > 0:
            r += SEP
            r += '-- Tables:' + SEP
            for t in self.Tables:
                r += '--   {0}'.format(t) + SEP

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

        if self.IsEnabled != another.IsEnabled:
            if self.IsEnabled:
                result.append("ALTER {0} {1} ENABLE;".format(self.GetTag(), self.GetFullName()))
            else:
                result.append("ALTER {0} {1} DISABLE;".format(self.GetTag(), self.GetFullName()))

        if self.Connect != another.Connect:
            result.append("ALTER {0} {1} CONNECTION '{2}';".format(
                self.GetTag(), self.GetFullName(), self.Connect))

        if self.Publications != another.Publications:
            result.append("ALTER {0} {1} SET PUBLICATION {2};".format(
                self.GetTag(), self.GetFullName(), ", ".join(self.Publications)))

        if self.Slot != another.Slot:
            result.append('ALTER {0} {1} SET(slot_name = "{2}");'.format(
                self.GetTag(), self.GetFullName(), self.Slot))

        if self.Slot != another.Slot:
            result.append("ALTER {0} {1} SET(synchronous_commit = '{2}');".format(
                self.GetTag(), self.GetFullName(), self.SyncCommit))

        if len(result) > 0:
            result.append("ALTER {0} {1} REFRESH PUBLICATION;".format(self.GetTag(), self.GetFullName()))

        return result
