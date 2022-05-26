#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : mongo_item
# @Time         : 2021/4/12 7:17 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.db.mongo import Mongo
from bson.objectid import ObjectId

m = Mongo(url=None)
collection_name = 'item'
c = m.db[collection_name]


# df['date'] = datetime.datetime.utcnow()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def insert(**kwargs):
    kwargs.pop('_id', None)

    logger.info(kwargs)

    c.insert(kwargs)
    return 'ok'


def query(**kwargs):
    logger.info(kwargs)
    rst = c.find_one(kwargs)

    return JSONEncoder().encode(rst)


if __name__ == '__main__':
    from appzoo import App

    app = App()
    app.add_route('/mongocache/item/insert', insert, method="POST")
    app.add_route('/mongocache/item/query', query, method="GET")

    app.run(port=8000, access_log=False)
