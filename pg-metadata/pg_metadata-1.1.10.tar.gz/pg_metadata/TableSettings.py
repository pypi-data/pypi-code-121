#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.DDL import DDL

class TableSettings(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Schema = (data.get("schema") or "").strip().lower()
        assert len(self.Schema) > 0, \
            "Table settings schema is null"

        self.Table = (data.get("table") or "").strip().lower()
        assert len(self.Table) > 0, \
            "Table settings table is null"

        setting = data.get("setting" or "").strip().lower()
        assert len(setting) > 0, \
            "Table settings value is null"
        assert setting.find('=') >= 0, \
            "Table settings value isn't contains '=' symbol"

        self.Field = setting.split('=')[0].strip().upper()
        self.Value = setting.split('=')[1].strip().upper()

    def __str__(self):
        return "%s=%s" % (self.Field, self.Value)

    def GetObjectType(self):
        return "table_setting"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return '{0}.{1}.{2}'.format(self.Schema, self.Table, self.Field)

    def DDL_Inner(self):
        return "  %s=%s" % (self.Field, self.Value)

    def DDL_Drop(self):
        return """ALTER TABLE {0}.{1} RESET ({2});""".format(
            self.Schema, self.Table, self.Field)

    def DDL_Create(self):
        return """ALTER TABLE {0}.{1} SET ({2} = {3});""".format(
            self.Schema, self.Table, self.Field, self.Value)

    def Diff(self, another):
        if self.Value != another.Value:
            return [
                self.DDL_Create()
            ]
        else:
            return []
