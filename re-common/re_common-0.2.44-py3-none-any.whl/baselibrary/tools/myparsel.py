# -*- coding: utf-8 -*-
# @Time    : 2020/9/16 13:18
# @Author  : suhong
# @File    : mcss.py
# @Software: PyCharm
import jsonpath as jsonpath
from parsel import Selector


class MParsel(object):
    def __init__(self, html="", logger=None):
        if logger is None:
            from re_common.baselibrary import MLogger
            logger = MLogger().streamlogger
        self.logger = logger
        self.html = html
        if self.html:
            self.set_sel(self.html)

    def set_sel(self, html):
        self.html = html
        self.sel = Selector(html)

    def css_parsel(self, sel, css_selector={}):
        assert self.html, '解析html时html不能为空'
        dicts = {}
        parent = None
        if css_selector:
            # 保证 parent 存在时优先解析
            if "parent" in css_selector.keys():
                parent = sel.css(css_selector["parent"])
            for key, value in css_selector.items():
                if isinstance(value, dict):
                    if key == "children":
                        # assert parent, "parent 不存在"
                        list_c = []
                        for p_item in parent:
                            list_c.append(self.css_parsel(p_item, value))
                        dicts[key] = list_c
                    else:
                        dicts[key] = self.css_parsel(sel, value)
                    continue
                if key == "parent":
                    continue
                dicts[key] = sel.css(value).getall()
        return dicts

    def css_parsel_html(self, css_selector={}):
        if self.html != "" and css_selector:
            dict_ = dict()
            for key, value in css_selector.items():
                dict_[key] = self.sel.css(value).getall()
            return True, dict_
        else:
            return False, ""

    def xpath_parsel(self, sel, xpath_selector={}):
        assert self.html, '解析html时html不能为空'
        dicts = {}
        parent = None
        if xpath_selector:
            # 保证 parent 存在时优先解析
            if "parent" in xpath_selector.keys():
                parent = sel.xpath(xpath_selector["parent"])
            for key, value in xpath_selector.items():
                if isinstance(value, dict):
                    if key == "children":
                        # assert parent, "parent 不存在"
                        list_c = []
                        for p_item in parent:
                            list_c.append(self.xpath_parsel(p_item, value))
                        dicts[key] = list_c
                    else:
                        dicts[key] = self.xpath_parsel(sel, value)
                    continue
                if key == "parent":
                    continue
                dicts[key] = sel.xpath(value).getall()
        return dicts

    def xpath_parsel_html(self, html="", xpath_selector={}):
        if html != "" and xpath_selector:
            sel = Selector(html)
            dict_ = dict()
            for key, value in xpath_selector.items():
                dict_[key] = sel.xpath(value).getall()
            return True, dict_
        else:
            return False, ""

    def json_parsel(self, sel_json, json_selector={}):
        assert self.html, '解析html时html不能为空'
        re_dict = {}
        if json_selector:
            for key, value in json_selector.items():
                re_dict[key] = jsonpath(sel_json, value)
        dicts = {
            "json_raw":sel_json,
            "data":re_dict
        }
        return dicts

    def asd(self):
        pass
