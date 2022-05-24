#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System import SEP
from pg_metadata.DDL    import DDL

class TableTrigger(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Schema = (data.get("schema") or "").strip().lower()
        assert len(self.Schema) > 0, \
            "Trigger schema is null"

        self.Table = (data.get("table") or "").strip().lower()
        assert len(self.Table) > 0, \
            "Trigger table is null"

        self.Name = (data.get("name") or "").strip().lower()
        assert len(self.Name) > 0, \
            "Trigger name is null"

        self.IsDisabled = data.get("is_disabled") or False

        self.Definition = data.get("definition") or ""
        assert len(self.Definition) > 0, \
            "Trigger definition is null"

        self.Definition = self.Definition.replace(" BEFORE",  SEP+"  BEFORE")
        self.Definition = self.Definition.replace(" AFTER",   SEP+"  AFTER")
        self.Definition = self.Definition.replace(" ON",      SEP+"  ON")
        self.Definition = self.Definition.replace(" FOR",     SEP+"  FOR")
        self.Definition = self.Definition.replace(" EXECUTE", SEP+"  EXECUTE")

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        return "table_trigger"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return "%s.%s" % (self.Schema, self.Name)

    def DDL_Drop(self):
        return "DROP TRIGGER %s on %s.%s;" % (self.Name, self.Schema, self.Table)

    def DDL_Create(self):
        r = ""
        r += self.Definition + ";"
        if self.IsDisabled:
            r += SEP
            r += self.DDL_Enabled()
        return r

    def DDL_Enabled(self):
        if self.IsDisabled:
            return "ALTER TABLE %s.%s DISABLE TRIGGER %s;" % (self.Schema, self.Table, self.Name)
        else:
            return "ALTER TABLE %s.%s ENABLE TRIGGER %s;" % (self.Schema, self.Table, self.Name)

    def Diff(self, another):
        result = []

        if self.Definition != another.Definition:
            result.append(another.DDL_Drop())
            result.append(self.DDL_Create())

        if self.IsDisabled != another.IsDisabled:
            result.append(self.DDL_Enabled())

        return result
