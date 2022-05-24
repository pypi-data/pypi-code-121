#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System import SEP
from pg_metadata.DDL    import DDL

class TableConstraint(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Schema = (data.get("schema") or "").strip().lower()
        assert len(self.Schema) > 0, \
            "Constraint schema is null"

        self.Table = (data.get("table") or "").strip().lower()
        assert len(self.Table) > 0, \
            "Constraint table is null"

        self.Name = (data.get("name") or "").strip().lower()
        assert len(self.Name) > 0, \
            "Constraint name is null"

        self.Type = (data.get("type") or "").strip().lower()
        assert len(self.Type) > 0, \
            "Constraint type is null"

        self.IsForeignKey = (self.Type == "f")

        self.OrderNum = data.get("order_num") or 6

        self.SortKey = "%s_%s" % (self.OrderNum, self.GetFullName())

        self.Definition = (data.get("definition") or "")
        assert len(self.Definition) > 0, \
            "Constraint definition is null"

        self.UpdateAction = (data.get("update_action") or "").strip().upper()

        self.DeleteAction = (data.get("delete_action") or "").strip().upper()

        self.MatchAction = (data.get("match_action") or "").strip().upper()

        self.DeferrableType = (data.get("deferrable_type") or "").strip().upper()

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        return "table_constraint"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return "%s.%s.%s" % (self.Schema, self.Table, self.Name)

    def GetDefinition(self, separator=" "):
        if not self.IsForeignKey:
            return "CONSTRAINT %s %s" % (self.Name, self.Definition)

        definition = self.Definition
        if definition.find(" ON") > -1:
            definition = definition[0:definition.find(") ON") + 1]

        #definition = definition.replace("REFERENCES", separator+"REFERENCES")

        return separator.join([
            "CONSTRAINT %s" % (self.Name),
            definition,
            self.MatchAction,
            self.UpdateAction,
            self.DeleteAction,
            self.DeferrableType
        ])

    def DDL_Inner(self):
        separator = "%s    " % (SEP)
        return "  " + self.GetDefinition(separator)

    def DDL_Create(self):
        return "ALTER TABLE %s.%s ADD %s;" % (self.Schema, self.Table, self.GetDefinition(" "))

    def DDL_Drop(self):
        return "ALTER TABLE %s.%s DROP CONSTRAINT %s;" % (self.Schema, self.Table, self.Name)

    def Diff(self, another):
        if (
            self.DeferrableType != another.DeferrableType   or
            self.Definition     != another.Definition       or
            self.UpdateAction   != another.UpdateAction     or
            self.DeleteAction   != another.DeleteAction     or
            self.MatchAction    != another.MatchAction
        ):
            return [
                another.DDL_Drop(),
                self.DDL_Create()
            ]
        else:
            return []
