# -*- coding: utf8 -*-

from elasticsearch import Elasticsearch
import elasticsearch.helpers
from datetime import time


class StoreEs(object):
    def __init__(self, host="localhost", port=9200, params=None, hosts=[]):
        """
        连接集群 或者单个节点
        :param host:
        :param port:
        :param params:
        :param hosts:
        """
        if hosts:
            if params:
                self.es = Elasticsearch(hosts, **params)
            else:
                self.es = Elasticsearch(hosts)
        else:
            if params:
                self.es = Elasticsearch("{0}:{1}".format(host, port), **params)
            else:
                self.es = Elasticsearch("{0}:{1}".format(host, port))

    def save(self, index, doc_type, body, id=None, params=None):
        field = dict()
        field['index'] = index
        field['doc_type'] = doc_type
        field['body'] = body
        if id:
            field['id'] = id
        if params:
            field['params'] = params
        self.es.index(**field)

    def batch_save(self, index, doc_type, body):
        for i, val in enumerate(body):
            while True:
                try:
                    self.save(index, doc_type, val)
                    break
                    pass
                except:
                    time.sleep(1)
                    continue

    def bulk_by_ids(self, index, doc_type, body, parallel=False):
        """
        批量操作指定id
        :param index:
        :param doc_type:
        :param body:
        :return:
        """
        actions = [
            {
                '_op_type': 'index',
                '_index': index,
                '_type': doc_type,
                '_id': d.pop("id"),
                '_source': d
            }
            for d in body
            ]
        if parallel:
            for success, info in elasticsearch.helpers.parallel_bulk(client=self.es, actions=actions, thread_count=10,
                                                                     chunk_size=1000):
                if not success:
                    print('Doc failed', info)
        else:
            elasticsearch.helpers.bulk(client=self.es, actions=actions,
                                       stats_only=True)  # 如果为True，则仅报告成功/失败操作的数量，而不仅仅是成功的次数和错误响应列表

    def bulk(self, index, doc_type, body):
        actions = [
            {
                '_op_type': 'index',  # 该bulk()API接受index，create， delete，和update行动。使用该_op_type字段指定操作（_op_type默认为index）：
                '_index': index,
                '_type': doc_type,
                '_source': d
            }
            for d in body
            ]
        elasticsearch.helpers.bulk(client=self.es, actions=actions)

    def search(self, index, doc_type, body=None, params=None):
        if params is None:
            res = self.es.search(index=index, doc_type=doc_type, body=body)
        else:
            res = self.es.search(index=index, doc_type=doc_type, body=body, params=params)
        return res

    def get(self, index, doc_type, id):
        return self.es.get(index=index, doc_type=doc_type, id=id)

    def update_by_query(self, index, doc_type=None, body=None, params=None):
        return self.es.update_by_query(index=index, doc_type=doc_type, body=body, params=params)

    def delete(self, index, doc_type, id):
        self.es.delete(index=index, doc_type=doc_type, id=id)


if __name__ == '__main__':
    # import uuid
    # from Queue import Queue
    # from threading import Thread
    from download_center.store.store_es_v2 import StoreEs

    config = {
        'host': '115.159.158.157',
        'port': 9200,
        'params': {
            'http_auth': ('admin', 'Iknowthat221@')
        }
    }
    try:
        es = StoreEs(**config)
        result = es.get("content_center", "tiezi", "AWBaEjLkLUY1KU5jKSwu")
        print("")
    except:
        pass
