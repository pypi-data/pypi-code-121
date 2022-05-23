# coding=utf-8

from suanpan.app.modules.base import Module
from suanpan.node import node

module = Module()


@module.on("node.info.get")
def getFormulaItems(_):
    return node.json()
