# -*- coding: utf8 -*-

import time
import sys


from pymongo import *

class StoreMongo(object):

    """
    mongoDB数据库链接
    mongodb://{username}:{password}@{host}:{port}/{db_name}?authMechanism=MONGODB-CR
    Args:
        host:数据库ip
        user:数据库用户名
        password:数据库用户密码
        db:数据库名
        port:数据库端口，默认3306
        authset:数据库认证模式，mongodb2.+默认为MONGODB-CR；3.0+默认为SCRAM-SHA-1
    """
    def __init__(self, host, port, user, password, db, authset='MONGODB-CR'):
        uri = 'mongodb://%s:%s@%s:%d/%s?authMechanism=%s' % (user, password, host, port, db, authset)
        client = MongoClient(uri)
        self.db = client[db]
