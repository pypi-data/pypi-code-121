# -*- coding: utf-8 -*-
from docparser.core.rect import Rect


class VirtualBlock:
    """
    虚拟区块信息类
    """

    def __init__(self, sheet, block_config):
        # Excel表格
        self.sheet = sheet

        # 虚拟块配置信息
        self.block_config = block_config

        self.virtual_block_data = []

        self.rect = None
        # 初始化区块信息
        # self.__init_rect()

        # 初始化虚拟块数据
        # self.__init_virtual_block_data()

    def __init_rect(self):
        """
        初始化区域信息
        """
        self.rect = Rect(self.sheet, self.block_config)

    # def __init_virtual_block_data(self):
    #     """
    #     初始化虚拟块数据
    #     """
    #     self.virtual_block_data = []

    def _pre_build(self, rect):
        """
        数据前置处理
        """

        pass

    def _build(self):
        """
        输出结果
        """
        self.virtual_block_data = []
        return None

    def _post_build(self, data):
        """
        数据后置处理
        """
        return None

    def build(self):
        """
        输出结果
        """

        # 根据配置计算区域信息
        self.rect = Rect(self.sheet, self.block_config)

        # 预构建
        self._pre_build(self.rect)

        # 构建虚拟块规范数据
        self._build()

        # 构建后置处理
        self._post_build(self.virtual_block_data)

    def _pre_output(self, virtual_block_data):
        """
        输出前置处理
        """
        return virtual_block_data

    def _post_output(self, output_data):
        """
        输出后置处理
        """
        return output_data

    def _build_output(self, virtual_block_data):
        """
        构建输出结果
        """
        return virtual_block_data

    def output(self):
        """
        输出
        """

        # 前置处理虚拟块缓存数据
        pre_virtual_block_data = self._pre_output(self.virtual_block_data)

        # 构建输出数据
        output_data = self._build_output(pre_virtual_block_data)

        # 对输出数据进行后置处理
        result = self._post_output(output_data)

        return result
