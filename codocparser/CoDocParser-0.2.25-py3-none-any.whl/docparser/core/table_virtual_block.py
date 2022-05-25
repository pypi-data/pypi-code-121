# -*- coding: utf-8 -*-
from docparser.core.virtual_block import VirtualBlock


class TableVirtualBlock(VirtualBlock):
    """
    表格虚拟区块信息类
    """

    def __init__(self, sheet, block_config):
        VirtualBlock.__init__(self, sheet, block_config)
        self.original_table = OriginalTable(self.rect, block_config)
        self.virtual_table = None

    def _build(self):
        """
        构建虚拟块数据
        """
        return None

    def _build_output(self, virtual_block_data):
        """
        构建输出结果
        """
        return virtual_block_data

    # def _pre_output(self, data):
    #     """
    #     数据前置处理
    #     """
    #     VirtualBlock._pre_output(self, data)
    #
    #     self._to_virtual_table()


class OriginalTable:
    class Header:
        def __init__(self):
            self.rows = []

    class Body:
        def __init__(self):
            self.rows = []

    def __init__(self,rect, table_config):
        self.rect = rect
        self.table_config = table_config
        self.header = OriginalTable.Header()
        self.body = OriginalTable.Body()
        self._build()

    def _build_header(self):
        pass

    def _build_body(self):
        pass

    def _build(self):
        pass


class VirtualTable:
    class Header:
        def __init__(self):
            self.rows = []

    class Body:
        def __init__(self):
            self.rows = []

    class Cell:
        def __init__(self):
            self.Value = None

    def __init__(self, original_table):
        self.original_table = original_table
        self.header = VirtualTable.Header()
        self.body = VirtualTable.Body()
