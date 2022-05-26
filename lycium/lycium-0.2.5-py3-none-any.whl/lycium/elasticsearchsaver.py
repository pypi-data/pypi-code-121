#!/usr/bin/python
#-*- coding:utf-8 -*-

import json
from typing import Union
import logging
import time
import threading
import queue
import elasticsearch
from elasticsearch import Elasticsearch

from .supports import singleton

LOG = logging.getLogger('common.elasticsearch_saver')

_elastic_save_helper_queue_mutex = threading.Lock()
_elastic_save_helper_queue = queue.Queue()

@singleton
class ElasticSearchSaver(object):
    """ElasticSearch saver
    """

    def __init__(self):
        super().__init__()
        self.SAVE_THRESHOLD = 10
        self.SAVE_INTERVAL_SECONDS = 2
        self.es_instance = Elasticsearch()
        self.pendings = []
        self.queue_mutex = threading.Lock()

    def configure(self, es_host: Union[str, list]) -> bool:
        if isinstance(es_host, str):
            if ',' in es_host:
                es_host = [h.strip() for h in es_host.split(',')]
            else:
                es_host = [es_host]
        try:
            self.es_instance = Elasticsearch(es_host)
        except Exception as e:
            LOG.error('FATAL: initialize elasticsearch connection:%s failed with error:%s', str(es_host), str(e))
            return False
        return True

    def ensure_index(self, index: str, doc_type: str, mappings: dict = {}) -> bool:
        if self.es_instance:
            if doc_type and not mappings:
                mappings = {
                    'mappings': {
                        'properties': {
                            '@timestamp': {
                                'type': 'date',
                            }
                        }
                    }
                }
            create_index = True
            try:
                if self.es_instance.indices.exists(index):
                    if not self.es_instance.indices.exists_type(index=index, doc_type=doc_type):
                        self.es_instance.indices.put_mapping(body=mappings, doc_type=doc_type, index=index, allow_no_indices=True, include_type_name=True)
                        create_index = False
                else:
                    self.es_instance.indices.create(index=index, body=mappings)
                    create_index = False
            except Exception as e:
                LOG.error('elasticsearch saver ensure index:%s with doc_type:%s failed with error:%s', str(index), str(doc_type), str(e))
                return False
            if create_index:
                try:
                    self.es_instance.indices.put_mapping(body=mappings, doc_type=doc_type, index=index, allow_no_indices=True, include_type_name=True, ignore=[400])
                except Exception as e:
                    LOG.error('elasticsearch saver ensure index:%s with doc_type:%s failed with error:%s', str(index), str(doc_type), str(e))
                return False
            return True
        return False

    def ensure_template(self, index: str, mappings: dict = {}) -> bool:
        if self.es_instance:
            if not mappings:
                mappings = {
                    'mappings': {
                        'properties': {
                            '@timestamp': {
                                'type': 'date',
                            }
                        }
                    }
                }
            try:
                if self.es_instance.indices.exists_template(index):
                    pass
                else:
                    self.es_instance.indices.put_template(name=index, body=mappings)
            except Exception as e:
                LOG.error('elasticsearch saver ensure template:%s failed with error:%s', str(index), str(e))
                return False
            return True
        return False

    def save(self, index: str, doc_type: str, body: dict, id=None) -> bool:
        for param in (index, doc_type, body):
            if param in elasticsearch.client.SKIP_IN_PATH:
                raise ValueError("Empty value passed for a required argument.")
                return False
        
        _elastic_save_helper_queue_mutex.acquire()
        _elastic_save_helper_queue.put_nowait({'action':'index', 'meta_data':{'_index':index, '_type':doc_type, '_id':id}, 'body':body})
        # LOG.info(" put es object to queue, now queue size:%d", _elastic_save_helper_queue.qsize())
        _elastic_save_helper_queue_mutex.release()
        return True

    def _batch_save(self, item_queue: list) -> bool:
        if not queue:
            return False
        items = []
        for item in item_queue:
            meta_data = {}
            for k,v in item['meta_data'].items():
                if v is not None:
                    meta_data[k] = v
            action_and_meta_data = {}
            action_and_meta_data[item['action']] = meta_data
            items.append(action_and_meta_data)
            items.append(item['body'])
        
        try:
            if not self.es_instance.bulk(items):
                LOG.error('elasticsearch batch save item failed')
        except Exception as e:
            LOG.error(" elasticsearch batch save %d items failed with error:%s", len(item_queue), str(e))
            return False
        LOG.info(" elasticsearch batch saved %d items.", len(item_queue))
        return True

ELASTICSEARCH_SAVER = ElasticSearchSaver()

def _elastic_save_helper_worker():
    tmp_queue = []
    tmp_queue_len = 0
    tmp_cur_time = 0
    last_looping_time = time.time()
    while True:
        _elastic_save_helper_queue_mutex.acquire()
        tmp_queue_len = _elastic_save_helper_queue.qsize()
        tmp_cur_time = time.time()
        tmp_queue = None
        if (tmp_queue_len >= ELASTICSEARCH_SAVER.SAVE_THRESHOLD) or (tmp_cur_time - last_looping_time >= ELASTICSEARCH_SAVER.SAVE_INTERVAL_SECONDS):
            if tmp_queue_len:
                LOG.debug(" elasticsearch save helper triggered batch save objects, queue size:%d", tmp_queue_len)
                tmp_queue = []
                while not _elastic_save_helper_queue.empty():
                    item = _elastic_save_helper_queue.get_nowait()
                    _elastic_save_helper_queue.task_done()
                    if item:
                        tmp_queue.append(item)
            else:
                tmp_queue = None
            last_looping_time = tmp_cur_time

        _elastic_save_helper_queue_mutex.release()
        
        if tmp_queue:
            if not ELASTICSEARCH_SAVER._batch_save(tmp_queue):
                _elastic_save_helper_queue_mutex.acquire()
                for item in tmp_queue:
                    _elastic_save_helper_queue.put_nowait(item)
                _elastic_save_helper_queue_mutex.release()

        time.sleep(0.1)

_elastic_saver_thread = threading.Thread(target=_elastic_save_helper_worker)
_elastic_saver_thread.start()
