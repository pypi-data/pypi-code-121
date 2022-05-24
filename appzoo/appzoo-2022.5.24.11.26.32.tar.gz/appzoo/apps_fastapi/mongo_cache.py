#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : mongo_cache
# @Time         : 2020/11/25 4:40 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 
"""help
from bson.objectid import ObjectId

"""

from meutils.pipe import *
from meutils.zk_utils import get_zk_config
from mi.db import Mongo

# cfg
ac_url = get_zk_config('/mipush/cfg')['ac_url']

m = Mongo()

# articleinfo_cache
collection_name = 'articleinfo'
ac = m.db[collection_name]


@lru_cache(100000)
def request(docid='0003899b202871b7fd3dab15f2f9549a'):
    url = f"{ac_url}/{docid}"
    r = requests.request('get', url)
    return r.json()['item']


def articleinfo_cache(**kwargs):
    docid = kwargs.get('id', 'id')
    articleinfo = ac.find_one({'id': docid})

    if articleinfo:
        logger.info(f'dup key: {docid}')
        return eval(articleinfo['ac'])
    else:
        articleinfo = request(docid)
        doc = {'id': docid, 'ac': str(articleinfo)}
        _ = ac.insert(doc)
        return articleinfo


if __name__ == '__main__':
    from appzoo import App

    app = App()
    app.add_route('/mongocache/ac', articleinfo_cache, method="GET")
    app.run(port=8000, access_log=False)
