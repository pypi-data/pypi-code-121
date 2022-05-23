# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.arguments import Arg, String
from suanpan.dw import dw


class DWArg(Arg):
    def getOutputTmpValue(self, *args):
        return "_".join(args)


class Table(DWArg):
    def __init__(self, key, table, partition, **kwargs):
        kwargs.setdefault("required", False)
        super().__init__(key)
        self.table = String(key=table, required=kwargs["required"])
        self.partition = String(key=partition)

    @property
    def isSet(self):
        return True

    def load(self, args):
        self.table.load(args)
        self.partition.load(args)
        if self.table.value:
            self.value = {"table": self.table.value, "partition": self.partition.value}
        return self

    def transform(self, value):
        if not value:
            return None
        return dw.readTable(self.table.value, self.partition.value)

    def save(self, result):
        data = result.value
        dw.writeTable(self.table.value, data)
        self.logSaved(self.table.value)
        return self.value

    def getOutputTmpArg(self, *args):
        value = self.getOutputTmpValue(  # pylint: disable=assignment-from-no-return
            *args
        )
        return (f"--{self.table.key}", value) if value is not None else tuple()
