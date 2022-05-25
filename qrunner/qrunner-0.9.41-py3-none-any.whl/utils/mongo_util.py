# coding=utf-8
# @Time    : 2022/2/21 11:21
# @Author  : kang.yang@qizhidao.com
# @File    : mongo_util.py
import pymongo


class BaseDB(object):
    def __init__(self, ip, db_name, table_name):
        self.client = pymongo.MongoClient(f"mongodb://{ip}:27017/")
        self.db = self.client[db_name]
        self.table = self.db[table_name]

    def insert_one(self, data: dict):
        print(f'插入数据: {data}')
        try:
            result = self.table.insert_one(data)
        except Exception as e:
            print(e)
        else:
            print('插入成功')
            print(result.inserted_id)
        finally:
            self.client.close()

    def insert_list(self, data: list):
        print(f'插入数据: {data}')
        try:
            result = self.table.insert_many(data)
        except Exception as e:
            print(e)
        else:
            print('插入成功')
            print(result.inserted_ids)
        finally:
            self.client.close()

    def select_all(self):
        print('查询表中所有数据')
        try:
            result = list(self.table.find())
        except Exception as e:
            print(e)
        else:
            print('查询成功')
            # print(result)
            return result
        finally:
            self.client.close()

    def select(self, query_data: dict):
        print(f'查询满足 {query_data} 条件的数据')
        try:
            result = list(self.table.find(query_data))
        except Exception as e:
            print(e)
        else:
            print('查询成功')
            # print(result)
            return result
        finally:
            self.client.close()

    def delete_all(self):
        print(f'删除所有数据')
        try:
            result = self.table.delete_many({})
        except Exception as e:
            print(e)
        else:
            print(result.deleted_count, "个文档已删除")
        finally:
            self.client.close()




