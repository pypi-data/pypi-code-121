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
            if item['area_level'] == '1':
                self.province_list.append(item)
            if item['area_level'] == '2':
                self.city_list.append(item)
            if item['area_level'] == '3':
                self.county_list.append(item)

    def get_candidates(self, address_text):
        """获取候选地址"""
        candidates = []
        for item in self.county_list:
            if item['name'] in address_text or item['alias'] in address_text:
                candidates.append(item)

        if not candidates:
            for item in self.city_list:
                if item['name'] in address_text or item['alias'] in address_text:
                    candidates.append(item)
        if not candidates:
            for item in self.province_list:
                if item['name'] in address_text or item['alias'] in address_text:
                    candidates.append(item)
        return candidates

    def generate_tree(self, source, parent):
        data = dict()
        for item in source:
            if item["id"] == parent:
                data['id'] = item['id']
                data['name'] = item['name']
                data['area_level'] = item['area_level']
                data['alias'] = item['alias']
                data['parent_id'] = item['parent_id']
                self.result_list.append(data)
                self.generate_tree(source, item["parent_id"])

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
        score_list = list()
        for item in candidates:
            self.result_list = []

            self.generate_tree(self.map_list, item['parent_id'])
            self.result_list.append(item)
            score = 0

            for data in self.result_list:
                if data['name'] in address_text or data['alias'] in address_text:
                    score += 1
            score_list.append(score)
        index_num = score_list.index(max(score_list))

        self.result_list = []
        self.generate_tree(self.map_list, candidates[index_num]['parent_id'])
        self.result_list.append(candidates[index_num])

        for item in self.result_list:
            if item['area_level'] == '3':
                result['county'] = item['name']
                result['county_id'] = item['id']
            if item['area_level'] == '2':
                result['city'] = item['name']
                result['city_id'] = item['id']
            if item['area_level'] == '1':
                result['province'] = item['name']
                result['province_id'] = item['id']

        return result
