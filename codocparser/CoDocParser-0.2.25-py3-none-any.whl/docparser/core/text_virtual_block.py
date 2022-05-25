# -*- coding: utf-8 -*-
from docparser.core.virtual_block import VirtualBlock


class TextVirtualBlock(VirtualBlock):
    """
    文本虚拟区块信息类
    """

    def __init__(self, sheet, block_config):
        VirtualBlock.__init__(self, sheet, block_config)
