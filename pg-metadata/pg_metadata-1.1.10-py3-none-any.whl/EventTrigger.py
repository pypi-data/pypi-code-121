#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System  import SEP
from pg_metadata.DDL     import DDL
from pg_metadata.Owner   import Owner

class EventTrigger(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = data.get("oid")
        assert (self.Oid or 0) > 0, \
            "Event trigger oid is null"

        self.Name = (data.get("name") or "").strip()
        assert len(self.Name) > 0, \
            "Event trigger name is null"

        self.Status = (data.get("status") or "").strip()
        assert len(self.Status) > 0, \
            "Event trigger status is null"

        self.Event = (data.get("event") or "").strip()
        assert len(self.Event) > 0, \
            "Event trigger event is null"

        self.Function = (data.get("fnc") or "").strip()
        assert len(self.Function) > 0, \
            "Event trigger function is null"

        self.Tags = (data.get("tags") or [])

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
        return "event_trigger"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return self.Name

    def GetTag(self):
        return "EVENT TRIGGER"

    def DDL_Drop(self):
        return "DROP {0} IF EXISTS {1};".format(self.GetTag(), self.GetFullName())

    def DDL_Create(self):
        r = ""
        r += "-- Event trigger: {0}".format(self.GetFullName()) + SEP
        r += SEP
        r += "-- {0}".format(self.DDL_Drop()) + SEP
        r += SEP
        r += "CREATE {0} {1}".format(self.GetTag(), self.GetFullName()) + SEP
        r += "  ON {0}".format(self.Event) + SEP

        if len(self.Tags) > 0:
            r += "  WHEN TAG IN ({0})".format(", ".join(["'{0}'".format(i) for i in sorted(self.Tags)])) + SEP

        r += "  EXECUTE PROCEDURE {0};".format(self.Function) + SEP
        r += SEP
        r += self.Owner.DDL_Create() + SEP
        r += SEP
        r += self.DDL_Status() + SEP
        return r.strip() + SEP

    def DDL_Status(self):
        return "ALTER {0} {1} {2};".format(self.GetTag(), self.GetFullName(), self.Status) + SEP

    def GetPath(self):
        return ["_event_trigger"]

    def GetFileName(self):
        return "{0}.sql".format(self.Name)

    def Export(self):
        result = {}
        result[self.GetObjectName()] = self
        result[self.Owner.GetObjectName()] = self.Owner
        return result

    def Diff(self, another):
        if (
            self.Event != another.Event or
            self.Function != another.Function or
            self.Tags != another.Tags
        ):
            return [self.DDL_Drop(), self.DDL_Create()]

        if self.Status != another.Status:
            return [self.DDL_Status()]
