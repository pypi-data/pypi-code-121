# -*- coding: utf-8 -*-
from docparser.core.text_virtual_block import TextVirtualBlock


class DefaultTextVirtualBlock(TextVirtualBlock):
    """
    默认文本虚拟区块实现
    """

    def __init__(self, sheet, block_config):
        self.virtual_table = None


