#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from TDhelper.db.mongodb.base import mongodbclient
from TDhelper.db.mongodb.setting import db_cfg

class dbhelper(mongodbclient):
    def __init__(self):
        try:
            super(dbhelper, self).__init__()
            if db_cfg:
                self.loadCfg(**db_cfg)
            else:
                raise "mongodb配置没有找到."
        except Exception as e:
            raise e

    def setCollection(self, collectionName):
        try:
            if self.db:
                self.collection = self.db[collectionName]
        except Exception as e:
            raise e

    def save(self, args, flag="one"):
        '''
        Feature\r\n
            save(self,args,flag)\r\n
        Description\r\n
            保存\r\n
        Args\r\n
            args\r\n
                type:Model Class\r\n
                description:实体\r\n
            flag\r\n
                type:string,[one|many]\r\n
                description:one->insert one record,many->insert some records\r\n
                example:save([model1,model2...,modeln])\r\n
        '''
        try:
            if self.collection:
                if flag.lower() == "one":
                    return self.collection.insert_one(args)
                elif flag.lower() == "many":
                    return self.collection.insert_many(args)
            return None
        except Exception as e:
            raise e

    def update(self, query, args):
        try:
            if self.collection:
                return self.collection.update(query, {'$set': args})
            return None
        except Exception as e:
            raise e

    def remove(self, query=None):
        try:
            if self.collection:
                if query:
                    return self.collection.remove(query)
                else:
                    return self.collection.remove()
            return None
        except Exception as e:
            raise e

    def findOne(self, query):
        try:
            if self.collection:
                return self.collection.find_one(query)
            return None
        except Exception as e:
            raise e

    def find(self, **kwargs):
        '''
        查询记录并返回结果集

        - parameters
            **kwargs: { 'query'= usr_query_str, 'limit'= usr_limit}
        '''
        try:
            if self.collection:
                if "query" in kwargs:
                    if "limit" in kwargs:
                        return self.collection.find(kwargs["query"]).limit(kwargs["limit"])
                    return self.collection.find(kwargs["query"])
                else:
                    if "limit" in kwargs:
                        return self.collection.find().limit(kwargs["limit"])
                    return self.collection.find()
        except Exception as e:
            raise e

    def findByPage(self, **kwargs):
        '''
        查询记录并返回分页结果集

        - parameters
            **kwargs: { 'query': usr_query_str, 'pagesize': usr_pagesize, 'pageno': pageno}
        '''
        try:
            if self.collection:
                if "query" in kwargs:
                    if ("pagesize" in kwargs) and ("pageno" in kwargs):
                        m_skip = (int(kwargs['pageno'])-1) * pagesize
                        if m_skip < 0:
                            m_skip = 0
                        return self.collection.find(kwargs["query"]).limit(kwargs["pagesize"]).skip(m_skip)
                    return self.collection.find(kwargs["query"])
                return self.collection.find()
        except Exception as e:
            raise e
