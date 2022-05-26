#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.DDL import DDL

class Grant(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Type = (data.get("instance_type") or "").strip().upper()
        assert len(self.Type) > 0, \
            "Grant instance type is null - {0}".format(parent)

        self.Instance = (data.get("instance_name") or "").strip()
        assert len(self.Instance) > 0, \
            "Grant instance name is null - {0}".format(parent)

        self.IsGrant = data.get("is_grant")
        assert self.IsGrant is not None, \
            "Grant type is null - {0}".format(parent)

        assert isinstance(self.IsGrant, bool), \
            "Grant type is not boolean - {0}".format(parent)

        self.Status = "GRANT" if self.IsGrant else "REVOKE"
        self.StatusDrop = "GRANT" if not self.IsGrant else "REVOKE"

        self.Prep = "TO" if self.IsGrant else "FROM"
        self.PrepDrop = "TO" if not self.IsGrant else "FROM"

        self.Permissions = data.get("perm")
        assert self.Permissions is not None, \
            "Grant permissions is null - {0}".format(parent)

        assert isinstance(self.Permissions, list), \
            "Grant permissions is not list - {0}".format(parent)

        assert len(self.Permissions) > 0, \
            "Grant permissions list is empty - {0}".format(parent)

        self.Permissions = ", ".join(sorted(self.Permissions))

        self.Role = (data.get("role") or "").strip()
        assert len(self.Role) > 0, \
            "Grant role is null"

    def __str__(self):
        return self.GetObjectName()

    def GetObjectType(self):
        return "grant"

    def GetObjectName(self):
        return "_".join([self.GetObjectType(), self.Type, self.Instance, self.Role])

    def DDL_Create(self):
        return "%s %s ON %s %s %s %s;" % (
            self.Status, self.Permissions, self.Type,
            self.Instance, self.Prep, self.Role
        )

    def DDL_Drop(self):
        return "%s %s ON %s %s %s %s;" % (
            self.StatusDrop, self.Permissions, self.Type,
            self.Instance, self.PrepDrop, self.Role
        )

    def Diff(self, another):
        if self.Permissions != another.Permissions:
            return [
                another.DDL_Drop(),
                self.DDL_Create()
            ]
        return []
