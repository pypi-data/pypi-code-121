# -*- coding: utf-8 -*-
'''
@Time    : 2022/5/18 10:46 AM
@Author  : oujiewen2@shoplineapp.com
@File    : mcHelper.py
'''
import json

from mcAssistants import loginHelper
from mcAssistants import sliceHelper
from mcAssistants import sqlHelper
import sys
sys.path.append("..")

class mcHelper:
    def __init__(self,parmas):
        self.parmas=parmas
        self.db_config=json.loads(self.parmas['db_config'])
        self.hp= loginHelper.loginHelper(self.parmas)
        self.users=json.loads(self.parmas["users"])
        self.slice=sliceHelper.tableHelper()

    def login(self,userName):
        return self.hp.login_main(self.users[userName],userName)

    def login_all(self):
        for key in self.users:
            self.login(key)
        return self.parmas

    def query_execute(self,sqlStr,storeId=None,merchantId=None):
        db_config=self.parmas['db_config']
        if storeId!=None:
            tableId=self.slice.tableId(int(storeId),self.parmas['maxTableID'])
            sqlStr=sqlStr.format(tableId=tableId)
        if merchantId!=None:
            mid=self.slice.tableId(int(merchantId),self.parmas['maxDbID'])
            self.db_config['dbName']=self.db_config['dbName']+str(mid)
        self.db = sqlHelper.MysqlUtil(self.db_config['dbHost'], int(self.db_config['dbPort']), self.db_config['dbUser'],
                               self.db_config['dbPassword'],
                               self.db_config['dbName'])

        return self.db.query_execute(sqlStr)



if __name__ == '__main__':
    pass