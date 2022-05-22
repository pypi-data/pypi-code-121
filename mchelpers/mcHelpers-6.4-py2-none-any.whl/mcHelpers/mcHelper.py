# -*- coding: utf-8 -*-
'''
@Time    : 2022/5/18 10:46 AM
@Author  : oujiewen2@shoplineapp.com
@File    : mcHelper.py
'''
import json

from mcHelpers import loginHelper
import sliceHelper
import sqlHelper

class mcHelper:
    def __init__(self,parmas):
        self.parmas=parmas
        self.db_config=json.loads(self.parmas['db_config'])
        self.hp= loginHelper.loginHelper(self.parmas)
        self.users=json.loads(self.parmas["users"])
        self.slice=sliceHelper.sliceHelper()

    def login(self,userName):
        return self.hp.login_main(self.users[userName],userName)

    def login_all(self):
        for key in self.users:
            self.login(key)
        return self.parmas

    def query_execute(self,sqlStr,storeId=None,merchantId=None):
        db_config=self.parmas['db_config']
        if storeId!=None:
            print(self.parmas['maxTableID'])
            tableId=self.slice.tableId(int(storeId),self.parmas['maxTableID'])
            sqlStr=sqlStr.format(tableId=tableId)
            print(sqlStr)
        if merchantId!=None:
            mid=self.slice.tableId(int(merchantId),self.parmas['maxDbID'])
            print(self.db_config)
            self.db_config['dbName']=self.db_config['dbName']+str(mid)
            print(self.db_config)
        self.db = sqlHelper.MysqlUtil(self.db_config['dbHost'], int(self.db_config['dbPort']), self.db_config['dbUser'],
                               self.db_config['dbPassword'],
                               self.db_config['dbName'])

        return self.db.query_execute(sqlStr)



if __name__ == '__main__':
    dict={'maxTableID':'32','merchantId':'4201060205','user_list': '[{"acct":"oujiewen2+xiaohei@shoplineapp.com","pwd":"9baca9a3b4cb6a6195fe559c118d8bcd2f5e9a398a1c486cb571d7cc6f6ae26257e4dda78f85ce1c86f09408d93fb1c5cb830870f45c4c5c51e16528d89545573d41028bdc42290f500ae681a074e31da00b81f29f846f611efd6b182cf8058a4a264ef0e4ef1ee4046fca6ca66283d972173f6a969f5b6cb428564b3b6b94c5","handel":"interface-automation","cookiesName":"小黑"}, { "acct":"oujiewen2+0001@shoplineapp.com", "pwd":"9baca9a3b4cb6a6195fe559c118d8bcd2f5e9a398a1c486cb571d7cc6f6ae26257e4dda78f85ce1c86f09408d93fb1c5cb830870f45c4c5c51e16528d89545573d41028bdc42290f500ae681a074e31da00b81f29f846f611efd6b182cf8058a4a264ef0e4ef1ee4046fca6ca66283d972173f6a969f5b6cb428564b3b6b94c5","handel":"interface-automation","cookiesName":"店长"}, { "acct":"oujiewen2+auto@shoplineapp.com", "pwd":"9baca9a3b4cb6a6195fe559c118d8bcd2f5e9a398a1c486cb571d7cc6f6ae26257e4dda78f85ce1c86f09408d93fb1c5cb830870f45c4c5c51e16528d89545573d41028bdc42290f500ae681a074e31da00b81f29f846f611efd6b182cf8058a4a264ef0e4ef1ee4046fca6ca66283d972173f6a969f5b6cb428564b3b6b94c5","handel":"interface-automation","cookiesName":"商家"}]', 'storeId': '1638944951560', 'users': '{"oujiewen2+xiaohei@shoplineapp.com":{"pwd":"9baca9a3b4cb6a6195fe559c118d8bcd2f5e9a398a1c486cb571d7cc6f6ae26257e4dda78f85ce1c86f09408d93fb1c5cb830870f45c4c5c51e16528d89545573d41028bdc42290f500ae681a074e31da00b81f29f846f611efd6b182cf8058a4a264ef0e4ef1ee4046fca6ca66283d972173f6a969f5b6cb428564b3b6b94c5","handel":"interface-automation","cookiesName":"小黑"},"oujiewen2+0001@shoplineapp.com":{"pwd":"9baca9a3b4cb6a6195fe559c118d8bcd2f5e9a398a1c486cb571d7cc6f6ae26257e4dda78f85ce1c86f09408d93fb1c5cb830870f45c4c5c51e16528d89545573d41028bdc42290f500ae681a074e31da00b81f29f846f611efd6b182cf8058a4a264ef0e4ef1ee4046fca6ca66283d972173f6a969f5b6cb428564b3b6b94c5","handel":"interface-automation","cookiesName":"店长"}}', 'maxDbID': '2', 'handel': 'https://interface-automation.myshoplinestg.com', 'appid': '1163336839', 'host': 'https://admin.myshoplinestg.com', 'db_config': '{"dbHost":"10.130.84.60","dbPort":6306,"dbUser":"sl_root","dbPassword":"qDoxncq4FI","dbName":"sl_sc_mc_test"}'}
    h=mcHelper(dict)
    # print(h.login_all())
    # # print(h.query_execute("select * from mc_catalog{tableId}"))
    print(h.query_execute('select * from mc_conversation_{tableId}',storeId=1638944951560))
    # print(json.loads(dict["users"]))