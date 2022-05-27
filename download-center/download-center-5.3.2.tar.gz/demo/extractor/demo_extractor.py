# -*- coding: utf-8 -*-
from lxml.html import fromstring
from lxml import etree
import sys


class DemoExtractor(object):
    """

    """

    def __init__(self):
        super(DemoExtractor, self).__init__()

    def extractor(self, text):
        """
        将一个页面文本解析为结构化信息的字典
        Args:
            text: 需要解析的文本
        Returns:
            数组: 每条为一个完整记录，记录由字典格式保存
        """
        results = list()
        try:
            tree = fromstring(text.decode("utf-8", "ignore"))  # 这种方式 可使用cssselect  不然linux 不能使用
            # soup = BeautifulSoup(text.decode('utf-8', 'ignore'), 'lxml')
            # navs_div = soup.find('div', id='navs')
            # if navs_div:
            #     depart_divs = navs_div.find_all('h2', recursive=True)
            #     if len(depart_divs) > 0:
            #         for depart in depart_divs:
            #             url = depart.find('a', recursive=True)['href']
            #             department_id = url.split('_')[2]
            #             results.append(
            #                 {
            #                     'name': str(depart.get_text()),
            #                     'department_id':department_id
            #                 })
        except Exception:
            pass
        return results
