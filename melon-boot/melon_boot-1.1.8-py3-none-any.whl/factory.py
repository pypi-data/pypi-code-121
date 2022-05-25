# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
import sys
import threading
import yaml
from melon.core import MelonElement, BasePage
from melon.loader import locate_file
from melon.loggers import logger

_lock = threading.RLock()
_pages = {}


class PageFactory:
    """页面对象工厂"""

    @staticmethod
    def __load_pages():
        """加载页面"""
        yaml_path = locate_file('./', 'pages.yaml')
        with open(yaml_path, encoding='UTF-8') as file:
            contents = yaml.load(file, Loader=yaml.FullLoader)
        try:
            pages = contents['melon']['pages']
        except KeyError as e:
            logger.error(f'pages not found [{e.args[0]}]')
            sys.exit(0)

        # 创建所有页面对象
        result = {}
        for page in pages:
            page_name = page['name']
            page_entity = BasePage()
            elements = page['elements']
            # 所有元素
            for element in elements:
                locator = element.get('locator')
                timeout = element.get('timeout')
                element_entity = MelonElement('label', locator[0], locator[1], timeout)
                setattr(page_entity, element.get('name'), element_entity)
            result[page_name] = page_entity
        return result

    @staticmethod
    def create_page(page_name) -> BasePage:
        """
        构建页面对象
        :param page_name: 页面名称
        :return: 页面对象
        """
        global _pages
        if not _pages or len(_pages) < 1:
            _lock.acquire()
            if not _pages or len(_pages) < 1:
                _pages = PageFactory.__load_pages()
        return _pages.get(page_name)
