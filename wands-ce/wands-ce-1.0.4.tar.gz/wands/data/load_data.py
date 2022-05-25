# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/19 14:44
"""
import os
import csv

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
ADDRESS_PATH = os.path.join(DIR_PATH, 'area_base.csv')


def load_address():
    result = []
    csv_reader = csv.reader(open(ADDRESS_PATH, encoding='utf8'))
    for line in csv_reader:
        address_map = dict()
        address_map['id'] = line[0]
        address_map['name'] = line[1]
        address_map['area_level'] = line[2]
        address_map['alias'] = line[3]
        address_map['parent_id'] = line[4]
        result.append(address_map)
    return result
