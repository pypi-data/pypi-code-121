#encoding=utf-8
import traceback

from pymongo import MongoClient

import logging
operators=['gt','lt','gte','lte','eq','ne','exist','regex','options','not','nor','or','and','in','nin','all','elemMatch','within','near','nearSphere']

class MongoDBService:
    def __init__(self,db,settings=None):
        self.settings = settings
        self.db = db
        self.conn = None

    def __connect(self):
        if self.conn is None:
            self.conn = MongoClient(self.settings.host,self.settings.port)
            db_auth = self.conn.admin
            db_auth.authenticate(self.settings.account,self.settings.password)


    def __close(self):
        if self.conn != None:
            try:
                self.conn.close()
            finally:
                logging.info('Close the connnection with mongodb.')

    def close(self):
        self.__close()

    #向${collection}表新增一条记录${data}
    def insert_one(self,collection,data):
        if data is None:
            return
        self.__connect()
        db=self.conn[self.db]
        tbl=db[collection]
        x = tbl.insert_one(data)
        logging.debug("New a record into {}: {}".format(collection,data))
        return x.inserted_id

    # 向${collection}表新增一条记录${data}
    def insert_many(self, collection, data):
        if data is None:
            return
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        x = tbl.insert_many(data)
        cnt=len(x.inserted_ids)
        logging.debug("New {} records into {}".format(cnt,collection))
        return cnt




    #根据${query}查找一条记录
    def find_one(self,collection,query):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]

        filter=self.__toMongoOperator(query)
        return tbl.find_one(filter)

    #根据${query}查找多条记录 query: {field: ${filed_filter}},sort: [{field: ${1 | -1}}]
    def find(self,collection,query,sort,page_no,page_size,fields=None):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        limit = 0 if page_size is None or page_size <= 0 else page_size
        skip = 0 if page_size is None or page_size <= 0 else (page_no-1)*page_size
        pn = 1 if page_size is None or page_size <= 0 else page_no
        result = None
        if sort is None or len(sort) ==0:
            sort=[('_id', -1)]
        if fields is not None and len(fields) > 0:
            fieldMap = {}

            for field in fields:
                fieldMap[field] = 1
            #result= tbl.find(filter=filter, limit=limit, skip=skip, sort=sort,fields=fieldMap)
            result=tbl.find(filter,fieldMap).sort(sort).skip(skip).limit(limit)
        else:
            #result= tbl.find(filter=filter, limit=limit, skip=skip, sort=sort)
            result=tbl.find(filter).sort(sort).skip(skip).limit(limit)
        total=tbl.find(filter=filter).count()

        return {'total':total,'page_no': pn,'cursor': skip,'limit': limit, 'result':list(result)}

    """
    根据filte计算符合的记录条数
    """
    def count(self,collection,query):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        cnt = tbl.find(filter=filter).count()
        return cnt

    """
        更新最先匹配filter的一行记录
        update: {${field}:${value}}
        """

    def upsert(self, collection, query, update):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter = self.__toMongoOperator(query)
        result = tbl.update_one(filter, {'$set': update},upsert=True)
        return result.matched_countind(filter=filter).count()
        return cnt
    """
    更新最先匹配filter的一行记录
    update: {${field}:${value}}
    """
    def update_one(self,collection,query,update):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        result = tbl.update_one(filter,{'$set':update})
        return result.matched_count
    """
    更新最先匹配filter的所有记录
    update: {${field}:${value}}
    """
    def update_many(self,collection,query,update):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        result= tbl.update_many(filter,{'$set':update})
        return result.matched_count

    def delete(self,collection,query):
        self.__connect()
        db = self.conn[self.db]
        tbl = db[collection]
        filter=self.__toMongoOperator(query)
        result= tbl.remove(filter,update)
        return result['ok']



    def __fromMathOprator(self,operator):
        if operator=='>':
            return 'gt'
        elif operator == '>=':
            return 'gte'
        elif operator=='<':
            return 'lt'
        elif operator == '<=':
            return 'lte'
        elif operator=='==':
            return 'eq'
        elif operator == '!=':
            return 'ne'
        else:
            return operator


    def __toMongoOperator(self,filters):
        query={}
        for key in filters.keys():
            newKey=self.__fromMathOprator(key)
            if newKey in operators:
                newKey = '$'+key
            v=filters[key]
            if isinstance(v,dict):
                query[newKey]=self.__toMongoOperator(v)
            elif isinstance(v,list):
                vs = []
                for item in v:
                    if isinstance(item,dict):
                        vs.append(self.__toMongoOperator(item))
                    else:
                        vs.append(item)

                query[newKey]=vs
            else:
                query[newKey]=v

        return query








