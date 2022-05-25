# -*- coding: utf-8 -*-
import importlib


class VirtualBlockBuilder:
    """
    虚拟区块构建者
    """

    @staticmethod
    def build(sheet, block_config):
        """
        根据类型构建虚拟区块
        """
        try:
            block_type = block_config['type']
            if block_type == 'text':
                parser = block_config['parser'] if 'parser' in block_config['parser'] else 'default'
            else:
                parser = block_config['parser'] if 'parser' in block_config['parser'] else 'standard'

            if parser in ['default', 'mixed', 'standard']:
                module_name = 'common.document.parsers.implements.%s_%s_virtual_block' % (parser, block_type)
            else:
                module_name = 'common.document.parsers.extends.%s_%s_virtual_block' % (parser, block_type)

            class_name = '%sVirtualBlock' % (parser.capitalize(), block_type.capitalize())
            virtual_block_module = importlib.import_module(module_name)
            cls = getattr(virtual_block_module, class_name)

            virtual_block = cls(sheet, block_config)
            virtual_block.build()

            return virtual_block

        except ModuleNotFoundError:
            raise
