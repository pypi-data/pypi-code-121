# -*- coding: utf-8 -*-
from docparser.core.table_virtual_block import TableVirtualBlock


class MixedTableVirtualBlock(TableVirtualBlock):
    """
    混杂模式表格虚拟区块实现
    """

    def __init__(self, sheet, block_config):
        self.virtual_table = None

   
