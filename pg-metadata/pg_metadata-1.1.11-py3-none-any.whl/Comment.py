#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.DDL import DDL

class Comment(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Type = (data.get("instance_type") or "").strip().upper()
        assert len(self.Type) > 0, \
            "Comment instance type is null - {0}".format(parent)

        self.Instance = (data.get("instance_name") or "").strip()
        assert len(self.Instance) > 0, \
            "Comment instance name is null - {0}".format(parent)

        self.Comment = (data.get("comment") or "").strip()

        self.IsExists = len(self.Comment) > 0

    def __str__(self):
        return self.GetObjectName()

    def GetObjectType(self):
        return "comment"

    def GetObjectName(self):
        return "{0}_{1}_{2}".format(self.GetObjectType(), self.Type, self.Instance)

    def DDL_Create(self):
        return "COMMENT ON %s %s IS '%s';" % (self.Type, self.Instance, self.Comment)

    def DDL_Drop(self):
        return "COMMENT ON %s %s IS '';" % (self.Type, self.Instance)

    def Diff(self, another):
        if self.Comment != another.Comment:
            return [
                self.DDL_Create()
            ]
        else:
            return []
