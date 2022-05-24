from typing import List

import pymongo
from pymongo import ReadPreference
from pymongo.results import InsertOneResult, InsertManyResult


class BasePyMongo(object):

    def __init__(self, conn=None, dbname=None):
        self.conn_string = conn
        self.dbname = dbname
        if self.conn_string:
            self.conn()

    def conn(self):
        """
        mongodb://cjrw:vipdatacenter@192.168.31.220:27017/
        collection
        :return:
        """
        self.client = pymongo.MongoClient(self.conn_string)

    def auth(self, username, password, mechanism='SCRAM-SHA-1'):
        """
            mongoDB有不同的认证机制，3.0版本以后采用的是'SCRAM-SHA-1', 之前的版本采用的是'MONGODB-CR'。所以，以我的版本情况，显然应该用'MONGODB-CR'
        :param username:
        :param password:
        :param mechanism:
        :return:
        """
        self.db.authenticate(username, password, mechanism=mechanism)

    def use_db(self, db=None):
        if db:
            self.db = self.client[db]
        else:
            self.db = self.client[self.dbname]

    def get_database(self, db, read_preference=ReadPreference.SECONDARY_PREFERRED, **kwargs):
        if db:
            self.db = self.client.get_database(db, read_preference=read_preference, **kwargs)
        else:
            self.db = self.client.get_database(self.dbname, read_preference=read_preference, **kwargs)

    def show_dbs(self):
        """
        查询数据库列表
        database_names 在最新版本的 Python 中已废弃，Python3.7+ 之后的版本改为了 list_database_names()。
        :return:
        """
        dblist = self.client.list_database_names()
        return dblist

    def create_col(self, colname):
        """
        在 MongoDB 中，集合只有在内容插入后才会创建! 就是说，创建集合(数据表)后要再插入一个文档(记录)，集合才会真正创建。
        创建集合
        :return:
        """
        self.col = self.db[colname]

    def get_all_col(self):
        """
        获取所有集合
        collection_names 在最新版本的 Python 中已废弃，Python3.7+ 之后的版本改为了 list_collection_names()。
        :return:
        """
        collist = self.db.list_collection_names()
        return collist

    def insert_one(self, dicts, *args, **kwargs):
        """
        插入一条数据
        :param dicts:
        :param args:
        :param kwargs:
        :return:
        """
        return self.col.insert_one(dicts, *args, **kwargs)

    def get_insert_id(self, insertresult: InsertOneResult):
        """
        返回_id
        :param insertresult:
        :return:
        """
        return insertresult.inserted_id

    def insert_many(self, lists: List[dict], ordered=False, *args, **kwargs):
        """
        插入多条 直接返回插入的id
        指定id 插入时 dict里面需要包含{"_id":1}这样的格式
        :param lists:
        :param ordered: 如果某一条出现错误 设置为False会继续处理其他数据，默认为true
                        ,根据测试和说明文档, False后会将list乱序, 乱序后的list, 如果
                        没问题的数据在前列, 则会插入, 如果不在前列, 则不会插入 并且返回错误
                        , 因此该方法不适合用于 list中的数据 好坏掺杂情况(包括主键冲突)
        :param args:
        :param kwargs:
        :return: InsertManyResult
        """
        list_result = self.col.insert_many(lists, ordered=False, *args, **kwargs)
        return list_result

    def get_insert_many_ids(self, list_result: InsertManyResult, *args, **kwargs):
        return list_result.inserted_ids

    def find_one(self, query=None, filter=None):
        """
        查询一条
        :return:
        """
        if query is None:
            query = {}
        return self.col.find_one(query, filter)

    def find(self, query=None, feild=None, limit=None, **kwargs):
        """
        kwargs:
            no_cursor_timeout: 设置 no_cursor_timeout=True 解决游标超时问题
            sort: 设置id 升序 sort = [("_id",pymongo.ASCENDING)] # 降序 pymongo.DESCENDING

        #################################################
        查询所有
        feild = { "_id": 0, "name": 1, "alexa": 1 }
        除了 _id 你不能在一个对象中同时指定 0 和 1，如果你设置了一个字段为 0，则其他都为 1，反之亦然。

        以下实例除了 alexa 字段外，其他都返回：

        { "alexa": 0 }
        以下代码同时指定了 0 和 1 则会报错：
        ,{ "name": 1, "alexa": 0 }

        条件
        { "name": 1, "alexa": 0 }
        :return: 返回一个pymongo.cursor.Cursor  迭代出结果为dict字典
        """
        if query is None:
            query = {}
        if feild:
            my_result = self.col.find(query, feild, **kwargs)
        else:
            my_result = self.col.find(query, **kwargs)

        if limit:
            my_result = my_result.limit(limit)

        return my_result

    def update_one(self, query, newvalues):
        """
        更新一条
        :param query:
        :param newvalues:
        :return:
        """
        return self.col.update_one(query, newvalues)

    def update_many(self, query, newvalues):
        """
        更新多条
        :param query:
        :param newvalues:
        :return:
        """
        return self.col.update_many(query, newvalues)

    def sort(self, keys, sorts=-1):
        """
        查询出来的排序
        :param keys:
        :param sorts:
        :return:
        """
        return self.col.find().sort(keys, sorts)

    def delete(self, query):
        """
        删除一条
        :param query:
        :return:
        """
        return self.col.delete_one(query)

    def delete_many(self, query):
        """
        删除多条
        :param query:
        :return:
        """
        return self.col.delete_many(query)

    def delet_all(self):
        """
        x.deleted_count 删除数
        :return:
        """
        return self.col.delete_many({})

    def delete_col(self):
        """
        删除表
        :return:
        """
        return self.col.drop()

    def find_count(self, query=None, feild=None, **kwargs):
        """
        获取计数
        :return:
        """
        if query is None:
            query = {}
        if feild:
            my_count = self.col.find(query, feild, **kwargs).count()
        else:
            my_count = self.col.find(query, **kwargs).count()

        return my_count
