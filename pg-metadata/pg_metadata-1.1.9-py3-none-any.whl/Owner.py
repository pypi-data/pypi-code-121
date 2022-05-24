#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.DDL import DDL

class Owner(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Type = (data.get("instance_type") or "").strip().upper()
        assert len(self.Type) > 0, \
            "Owner instance type is null - {0}".format(parent)

        self.Instance = (data.get("instance_name") or "").strip()
        assert len(self.Instance) > 0, \
            "Owner instance name is null - {0}".format(parent)

        self.Owner = (data.get("owner_name") or "").strip()
        assert len(self.Owner) > 0, \
            "Owner name is null - {0}".format(parent)

    def __str__(self):
        return self.GetObjectName()

    def GetObjectType(self):
        return "owner"

    def GetObjectName(self):
        return "{0}_{1}_{2}".format(self.GetObjectType(), self.Type, self.Instance)

    def DDL_Create(self):
        return "ALTER %s %s OWNER TO %s;" % (self.Type, self.Instance, self.Owner)

    def DDL_Drop(self):
        return ""

    def Diff(self, another):
        if self.Owner != another.Owner:
            return [
                self.DDL_Create()
            ]
        else:
            return []
