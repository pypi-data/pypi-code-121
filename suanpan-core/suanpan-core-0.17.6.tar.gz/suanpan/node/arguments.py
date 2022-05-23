# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import error
from suanpan.arguments.auto import ProxyArg
from suanpan.node import node


class DataFrame(ProxyArg):
    MAPPING = {
        "data": "suanpan.storage.arguments.Csv",
        "table": "suanpan.dw.arguments.Table",
    }

    def __init__(self, key, table, partition, *args, **kwargs):
        port = node.get(table) or node.get(key)
        if not port:
            argsString = f"key={key}, table={table}, partition={partition}"
            raise error.NodeError(f"No such {self.name}: {argsString}")
        kwargs.setdefault(self.TYPE_KEY, port.type)
        kwargs.update(key=key, table=table, partition=partition)
        super().__init__(*args, **kwargs)
