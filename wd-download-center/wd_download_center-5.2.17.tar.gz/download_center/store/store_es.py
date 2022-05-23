# -*- coding: utf8 -*-

from elasticsearch import Elasticsearch
import elasticsearch.helpers
from datetime import time


class StoreEs(object):
    def __init__(self, host="localhost", port=9200, params=None):
        if params is not None:
            self.es = Elasticsearch("{0}:{1}".format(host, port),
                                    **params)
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

    def bulk(self, index, doc_type, body):
        actions = [
            {
                '_op_type': 'index',
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

# def save(html, es, q):
#     for i in range(5000):
#         id = str(uuid.uuid1())
#         val = {
#             'result': html,
#             'iden': i,
#         }
#         es.save('yuqing', 'urls_11', val, id=id)
#         q.put(id)

# def delete(es, q):
#     import time
#     from Queue import Empty
#     import traceback
#     while True:
#         try:
#             id = q.get_nowait()
#             # r = es.get('yuqing', 'urls_11', id)
#             # print r['_source']['iden']
#             r = es.es.delete('yuqing', 'urls_11', id)
#             print r
#         except Empty:
#             time.sleep(2)
#             print 'sleep'
#         except Exception, e1:
#             print(traceback.format_exc())


if __name__ == '__main__':
    # import uuid
    # from Queue import Queue
    # from threading import Thread
    from download_center.store.store_es import StoreEs

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
    except:
        pass


