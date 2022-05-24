#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata.System             import SEP, ParseACL
from pg_metadata.Grant              import Grant
from pg_metadata.Owner              import Owner
from pg_metadata.Comment            import Comment
from pg_metadata.TableColumn        import TableColumn
from pg_metadata.TableConstraint    import TableConstraint
from pg_metadata.TableIndex         import TableIndex
from pg_metadata.TableSettings      import TableSettings
from pg_metadata.TableTrigger       import TableTrigger
from pg_metadata.DDL                import DDL

class Table(DDL):
    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.Oid = (data.get("oid") or 0)
        assert self.Oid > 0, \
            "Table oid is null"

        self.Schema = (data.get("schema") or "").strip()
        assert len(self.Schema) > 0, \
            "Table schema is null"

        self.Name = (data.get("name") or "").strip()
        assert len(self.Name) > 0, \
            "Table name is null"

        self.Settings = []
        for o in (data.get("reloptions") or []):
            self.Settings.append(TableSettings(self.GetObjectName(), {
                "schema"    : self.Schema,
                "table"     : self.Name,
                "setting"   : o
            }))

        self.HasOids = (data.get("has_oids") or "").strip()
        assert len(self.HasOids) > 0, \
            "Table has oids is null"

        self.HasOids = "OIDS=%s" % (str(self.HasOids).upper())
        self.Settings.append(TableSettings(self.GetObjectName(), {
            "schema"    : self.Schema,
            "table"     : self.Name,
            "setting"   : self.HasOids
        }))

        self.Inherits = (data.get("parent_table") or "").strip()

        self.Inherits = data.get("parent_table")
        if self.Inherits is not None and self.Inherits != "":
            self.Inherits = self.Inherits.strip()
        else:
            self.Inherits = None

        self.PartKey = data.get("part_key")
        if self.PartKey is not None and self.PartKey != "":
            self.PartKey = self.PartKey.strip()
        else:
            self.PartKey = None

        self.PartBorder = data.get("part_border")

        self.Owner = Owner(
            self.GetObjectName(),
            {
                "instance_type" : self.GetTag(),
                "instance_name" : self.GetFullName(),
                "owner_name"    : data.get("owner")
            }
        )

        self.Comment = Comment(
            self.GetObjectName(),
            {
                "instance_type" : self.GetTag(),
                "instance_name" : self.GetFullName(),
                "comment"       : data.get("comment")
            }
        )

        self.Grants = []
        for grant in ParseACL(data.get("acl"), self.Owner.Owner):
            grant["instance_type"] = self.GetTag()
            grant["instance_name"] = self.GetFullName()
            self.Grants.append(Grant(self.GetObjectName(), grant))

        self.Columns = []
        for column in (data.get("columns") or []):
            column["schema"] = self.Schema
            column["table"] = self.Name
            column = TableColumn(self.GetObjectName(), column)
            self.Columns.append(column)

        self.Constraints = []
        for cons in (data.get("constraints") or []):
            cons["schema"] = self.Schema
            cons["table"] = self.Name
            cons = TableConstraint(self.GetObjectName(), cons)
            self.Constraints.append(cons)

        self.Indexes = []
        for idx in (data.get("indexes") or []):
            idx["schema"] = self.Schema
            idx["table"] = self.Name
            idx = TableIndex(self.GetObjectName(), idx)
            self.Indexes.append(idx)

        self.Triggers = []
        for trg in (data.get("triggers") or []):
            trg["schema"] = self.Schema
            trg["table"] = self.Name
            trg = TableTrigger(self.GetObjectName(), trg)
            self.Triggers.append(trg)

    def __str__(self):
        return self.GetFullName()

    def GetObjectType(self):
        return "table"

    def GetObjectName(self):
        return "{0}_{1}".format(self.GetObjectType(), self.GetFullName())

    def GetFullName(self):
        return "{0}.{1}".format(self.Schema, self.Name)

    def GetTag(self):
        return "TABLE"

    def DDL_Drop(self):
        return "DROP TABLE IF EXISTS %s;" % (self.GetFullName())

    def DDL_Settings(self):
        r = []

        for sts in sorted(self.Settings, key=lambda x: x.GetFullName()):
            r.append(sts.DDL_Inner())

        return (",%s" % (SEP)).join(r)

    def DDL_Create(self):
        is_last_comma = len(self.Constraints) > 0

        r = ""
        r += self.DDL_Drop()
        r += SEP
        r += SEP

        r += "CREATE TABLE %s(" % (self.GetFullName())
        r += SEP

        for col in sorted(self.Columns, key=lambda x: x.OrderNum):
            r += col.DDL_Inner(add_comma=is_last_comma, add_comment=True)
            r += SEP


        self.Constraints = sorted(self.Constraints, key=lambda x: x.SortKey)
        if len(self.Constraints) > 0:
            cns = [c.DDL_Inner() for c in self.Constraints]
            cns_sep = ",%s" % (SEP)
            r += cns_sep.join(cns)
            r += SEP

        r += ")"
        r += SEP

        if self.PartKey is not None:
            r += "PARTITION BY %s" % (self.PartKey)
            r += SEP

        if self.Inherits is not None:
            if self.PartBorder is not None:
                r += "PARTITION OF %s" % (self.Inherits)
                r += SEP
            else:
                r += "INHERITS ( %s )" % (self.Inherits)
                r += SEP

        if self.PartBorder is not None:
            r += self.PartBorder
            r += SEP

        r += "WITH ("
        r += SEP
        r += self.DDL_Settings()
        r += SEP
        r += ");"
        r += SEP
        r += SEP
        r += self.Owner.DDL_Create()
        r += SEP

        for grant in self.Grants:
            r += grant.DDL_Create()
            r += SEP
        r += SEP

        if self.Comment.IsExists:
            r += self.Comment.DDL_Create()
            r += SEP
            r += SEP

        for col in self.Columns:
            cmt = col.DDL_Comment()
            if cmt is not None:
                r += col.DDL_Comment()
                r += SEP
        r += SEP

        for ind in sorted(self.Indexes, key=lambda x: x.GetFullName()):
            r += ind.DDL_Create("%s  " % (SEP))
            r += SEP
            r += SEP

        for trg in sorted(self.Triggers, key=lambda x: x.GetFullName()):
            r += trg.DDL_Create()
            r += SEP
            r += SEP

        return r.strip() + SEP

    def GetPath(self):
        return [self.Schema, "table"]

    def GetFileName(self):
        return "{0}.sql".format(self.Name)

    def Export(self):
        result = {}
        result[self.GetObjectName()] = self
        result[self.Comment.GetObjectName()] = self.Comment
        result[self.Owner.GetObjectName()] = self.Owner
        for v in self.Grants:
            result[v.GetObjectName()] = v
        for v in self.Columns:
            result[v.GetObjectName()] = v
        for v in self.Settings:
            result[v.GetObjectName()] = v
        for v in self.Constraints:
            result[v.GetObjectName()] = v
        for v in self.Indexes:
            result[v.GetObjectName()] = v
        for v in self.Triggers:
            result[v.GetObjectName()] = v
        return result
