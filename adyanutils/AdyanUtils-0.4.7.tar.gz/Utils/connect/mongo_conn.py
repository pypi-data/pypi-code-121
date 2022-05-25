#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/26 11:25
# @Author  : Adyan
# @File    : mongo_conn.py


from datetime import datetime

from pymongo import MongoClient


class MongoConn(object):
    def __init__(self, db_name, config):
        """
        :param db_name:
        :param config: {
        "host": "192.168.20.211",
        # "host": "47.107.86.234",
        "port": 27017
    }
        """
        self.client = MongoClient(**config, connect=True)
        self.db = self.client[db_name]


class DBBase(object):
    def __init__(self, collection, db_name, config):
        self.mg = MongoConn(db_name, config)
        self.collection = self.mg.db[collection]

    def exist_list(self, data, key, get_id: callable, _ignore):
        lst = [get_id(obj) for obj in data]
        set_list = set([
            i.get(key)
            for i in list(self.collection.find({key: {"$in": lst}}))
        ])
        set_li = set(lst) - set_list
        exist = list(set_li - set(_ignore))
        for obj in data:
            if get_id(obj) in exist:
                yield obj

    def exist(self, dic):
        """
        单条查询
        :param dic:
        :return:1,0
        """
        return self.collection.find(dic).count()

    def update_one(self, dic, item=None):
        result = self.exist(dic)
        if item and result == 1:
            item['updateTime'] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            self.collection.update(dic, {"$set": item})
        elif item:
            self.collection.update(dic, {"$set": item}, upsert=True)

    def insert_one(self, param):
        """
        :param param: 多条list 或者 单条dict
        :return:
        """
        self.collection.insert(param)

    def find_len(self, dic=None):
        if dic:
            return self.collection.find(dic).count()
        return self.collection.find().count()

    def find_one(self):
        return self.collection.find_one()

    def find_list(self, count=1000, dic=None, page=None, ):
        """
        查询数据
        :param count:查询量
        :param dic:{'city': ''} 条件查询
        :param page:分页查询
        :return:
        """
        index = page * count - count
        if page == 1:
            index = 0
        if dic:
            return list(self.collection.find(dic).skip(index).limit(count))
        if page:
            return list(self.collection.find().skip(index).limit(count))

    def daochu(self):
        return list(self.collection.find({'$and': [
            {'$or': [{"transaction_medal": "A"}, {"transaction_medal": "AA"}]},
            {"tpServiceYear": {'$lte': 2}},
            {"overdue": {'$ne': "店铺已过期"}},
            {"province": "广东"}
        ]}))

    def counts(self, dic=None):
        if dic:
            return self.collection.find(dic).count()
        return self.collection.count()


class MongoPerson(DBBase):
    def __init__(self, table, db_name, config):
        super(MongoPerson, self).__init__(table, db_name, config)

# mo = MongoPerson('config', 'settings', config={
#     # "host": "192.168.20.211",
#     # "host": "119.29.9.92",
#     "host": "47.107.86.234",
#     "port": 27017
# }).find_one()
# print(mo)
