#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from pg_metadata.System import SEP
from pg_metadata.DDL    import DDL

class TableColumn(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Schema = (data.get("schema") or "").strip().lower()
        assert len(self.Schema) > 0, \
            "Column schema is null"

        self.Table = (data.get("table") or "").strip().lower()
        assert len(self.Table) > 0, \
            "Column table is null"

        self.Name = (data.get("name") or "").strip().lower()
        assert len(self.Name) > 0, \
            "Column name is null"

        self.Type = (data.get("type") or "").strip()
        assert len(self.Type) > 0, \
            "Column type is null"

        self.NotNull = data.get("not_null") or False

        self.DefaultValue = (data.get("default_value") or "").strip()

        self.OrderNum = data.get("order_num") or 0
        assert self.OrderNum > 0, \
            "Column order num is null"

        self.OrderNumLast = data.get("max_order_num") or 0
        assert self.OrderNumLast > 0, \
            "Column max order num is null"

        self.IsLast = (self.OrderNum == self.OrderNumLast)

        self.Comment = data.get("comment")
        if self.Comment is not None:
            self.Comment = re.sub("[\n\r]{1,}", SEP, self.Comment, re.MULTILINE | re.IGNORECASE)

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        return "table_column"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return "{0}.{1}.{2}".format(self.Schema, self.Table, self.Name)

    def DDL_Create(self):
        result = "ALTER TABLE %s.%s ADD COLUMN %s %s%s%s;" % (
            self.Schema,
            self.Table,
            self.Name,
            self.Type,
            "" if not self.NotNull else " NOT NULL",
            "" if len(self.DefaultValue) <= 0 else " DEFAULT " + self.DefaultValue
        )

        if self.Comment is not None and self.Comment.strip() != "":
            result = result + '\nCOMMENT ON COLUMN %s.%s.%s IS "%s";' % (
                self.Schema, self.Table, self.Name, self.Comment)

        return result

    def DDL_NotNull(self):
        if self.NotNull:
            return "ALTER TABLE %s.%s ALTER COLUMN %s SET NOT NULL;" % (self.Schema, self.Table, self.Name)
        else:
            return "ALTER TABLE %s.%s ALTER COLUMN %s DROP NOT NULL;" % (self.Schema, self.Table, self.Name)

    def DDL_Default(self):
        if self.DefaultValue is None or self.DefaultValue.strip() == "":
            return "ALTER TABLE %s.%s ALTER COLUMN %s DROP DEFAULT;" % (self.Schema, self.Table, self.Name)
        else:
            return "ALTER TABLE %s.%s ALTER COLUMN %s SET DEFAULT %s;" % (self.Schema, self.Table, self.Name, self.DefaultValue)

    def DDL_Drop(self):
        return "ALTER TABLE %s.%s DROP COLUMN IF EXISTS %s;" % (self.Schema, self.Table, self.Name)

    def DDL_Comment(self):
        if self.Comment is not None and self.Comment.strip() != "":
            return "COMMENT ON COLUMN %s.%s.%s IS '%s';" % (self.Schema, self.Table, self.Name, self.Comment)
        return None

    def DDL_Type(self):
        return "ALTER TABLE %s.%s ALTER COLUMN %s TYPE %s;" % (self.Schema, self.Table, self.Name, self.Type)

    def DDL_Inner(self, add_comma=False, add_comment=False):
        if not add_comma:
            add_comma = not self.IsLast

        return "  %s %s%s%s%s%s" % (
            self.Name,
            self.Type,
            "" if not self.NotNull else " NOT NULL",
            "" if len(self.DefaultValue) <= 0 else " DEFAULT " + self.DefaultValue,
            "" if not add_comma else ",",
            "" if not add_comment or self.Comment is None else " -- %s" % (self.Comment.replace(SEP, " "))
        )

    def Diff(self, another):
        result = []

        if self.Comment != another.Comment:
            result.append(self.DDL_Comment())

        if self.DefaultValue != another.DefaultValue:
            result.append(self.DDL_Default())

        if self.NotNull != another.NotNull:
            result.append(self.DDL_NotNull())

        if self.Type != another.Type:
            result.append(self.DDL_Type())

        return result
