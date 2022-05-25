# -*- coding: utf-8 -*-
import importlib


class DocParserFactory:
    """
    文档解析器创建工厂
    """

    @staticmethod
    def create(doc_type, file, config):
        """
        根据类型创建对应类型的文档解析器

        """
        try:

            module_name = 'docparser.implements.%s_document_parser' % doc_type

            class_name = '%sDocumentParser' % doc_type.capitalize()
            virtual_block_module = importlib.import_module(module_name)
            cls = getattr(virtual_block_module, class_name)

            return cls(file, config)
        except ModuleNotFoundError:
            raise

