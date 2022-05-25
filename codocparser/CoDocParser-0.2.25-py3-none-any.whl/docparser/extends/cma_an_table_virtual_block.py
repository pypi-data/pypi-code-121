# -*- coding: utf-8 -*-
from docparser.core.table_virtual_block import TableVirtualBlock


class CmaAnTableVirtualBlock(TableVirtualBlock):
    """
    CMA到港通知书表格扩展实现
    """

    def __init__(self, sheet, block_config):
        self.virtual_table = None

   
