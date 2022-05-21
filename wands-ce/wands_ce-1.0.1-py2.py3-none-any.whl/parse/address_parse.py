# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/19 14:09
"""
from wands.data.load_data import load_address


class AddressParse:
    """解析到3级地址"""

    def __init__(self):
        self.map_list = None

    def _prepare(self):
        self.map_list = load_address()
        self.province_list = []
        self.city_list = []
        self.county_list = []
        for item in self.map_list:
            if item['class_code'] == '1':
                self.province_list.append(item)
            if item['class_code'] == '2':
                self.city_list.append(item)
            if item['class_code'] == '3':
                self.county_list.append(item)

    def get_candidates(self, address_text):
        """获取候选地址"""
        candidates = []
        for item in self.county_list:
            if item['name'] in address_text:
                candidates.append(item)

        if not candidates:
            for item in self.city_list:
                if item['name'] in address_text:
                    candidates.append(item)
        if not candidates:
            for item in self.province_list:
                if item['name'] in address_text:
                    candidates.append(item)
        return candidates

    def generate_tree(self, source, parent):
        data = dict()
        for item in source:
            if item["id"] == parent:
                data['id'] = item['id']
                data['name'] = item['name']
                data['class_code'] = item['class_code']
                self.result_list.append(data)
                self.generate_tree(source, item["parent"])

    def __call__(self, address_text):
        if self.map_list is None:
            self._prepare()
        result = {'province': None,
                  'city': None,
                  'county': None,
                  'province_id': None,
                  'city_id': None,
                  'county_id': None,
                  'detail': address_text
                  }

        candidates = self.get_candidates(address_text)
        if not candidates:
            return result
        candidate = candidates[0]
        self.result_list = []

        self.generate_tree(self.map_list, candidate['parent'])
        self.result_list.append(candidate)

        for item in self.result_list:
            if item['class_code'] == '3':
                result['county'] = item['name']
                result['county_id'] = item['id']
            if item['class_code'] == '2':
                result['city'] = item['name']
                result['city_id'] = item['id']
            if item['class_code'] == '1':
                result['province'] = item['name']
                result['province_id'] = item['id']

        return result
