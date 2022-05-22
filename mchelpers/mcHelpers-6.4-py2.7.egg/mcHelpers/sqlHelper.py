# -*- coding: utf-8 -*-


import pymysql
import json  # 测试数据用


class MysqlUtil:
    def __init__(self, dbHost, dbPort,dbUser,dbPassword,dbName):
        self.cur = self.get_db(dbHost, int(dbPort),dbUser,dbPassword,dbName)

    def get_db(self, db_host, db_port, db_user, db_password, db_name):
        try:
            self.db = pymysql.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                db=db_name)
        except Exception as e:
            print(e)
            return
        cur = self.db.cursor()
        return cur

    # 查
    def query_execute(self, sql):

        try:
            self.cur.execute(sql)
            desc = self.cur.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in self.cur.fetchall()]  # 列表表达式把数据组装起来
        except Exception as e:
            self.close()
            return {}
        self.close()
        return data_dict
    '''
    预发线上不能执行查以为的操作，暂时屏蔽
    '''
    # # 增、删、改
    # def execute_sql(self, sql):
    #     result = ''
    #     try:
    #         result = self.cur.execute(sql)
    #         self.db.commit()
    #     except Exception as e:
    #         print(e)
    #     if result == "":
    #         return False
    #     return True

    # 关闭数据库
    def close(self):
        self.db.close()


if __name__ == '__main__':
    db_config={
        # (db_config['dbHost'], db_config['dbPort'], db_config['dbUser'],
        #  db_config['dbPassword'],
        #  db_config['dbName'])
        "dbHost": "10.130.84.60",
        "dbPort": 6306,
        "dbUser": "sl_root",
        "dbPassword": "qDoxncq4FI",
        "dbName": "sl_sc_mc_test"}
    db=MysqlUtil(db_config)
    print(db.query_execute('select * from mc_catalog'))