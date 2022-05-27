#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AppZoo.
# @File         : user_ann
# @Time         : 2021/4/17 1:54 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :


from meutils.pipe import *
from meutils.annzoo.ann import ANN
from meutils.zk_utils import zk
from meutils.http_utils.results import get_ac, get_simbert_vectors
from meutils.db.mongo import Mongo

# project

mongo = Mongo(url=None)
browser_push_user_ann = mongo.db.browser_push_user_ann


class KW(BaseConfig):
    topk: int = 10000
    ann_index: int = 0
    ann_part: int = 0
    docid: str = None
    title: str = None


def recall_user(ann_part, ann, push_vec, topk=10000, nprobe=32, threshold=None):  # todo: 多条查询
    entities = ann.user_ann.search(
        push_vec, topk,
        nprobe=nprobe,
        scalar_list=[{'term': {'ann_part': [ann_part]}}]
    )
    if threshold is None:
        ids = entities.ids
    else:
        ids = np.array(entities.ids)[np.where(np.array(entities.distances) > threshold)[0]].tolist()

    # id mapping
    r = browser_push_user_ann.find({'id': {'$in': ids}, 'ann_part': ann_part}, {'userId': 1, '_id': 0})  # 只返回 userId
    return pd.DataFrame(r)['userId'].tolist()


def func(**kwargs):
    ips = zk.get_children('/mipush/ann/ips')
    anns = list(map(ANN, ips))

    cfg = KW.parse_obj(kwargs)
    if cfg.docid:
        title = get_ac(cfg.docid)['title']
    else:
        title = cfg.title
    push_vec = get_simbert_vectors(title)

    return recall_user(cfg.ann_part, anns[cfg.ann_index], push_vec, cfg.topk)


if __name__ == '__main__':
    from appzoo import App

    app = App()
    app.add_route('/ann', func, "GET")
    app.add_route('/ann', func, "POST")

    app.run()
