# -*- coding: utf-8 -*-
from docparser.core.text_virtual_block import TextVirtualBlock


class StandardTableVirtualBlock(TextVirtualBlock):
    """
    标准表格虚拟区块实现
    """

    def __init__(self, sheet, block_config):
        self.virtual_table = None

   
