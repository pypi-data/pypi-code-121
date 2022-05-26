#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
from typing import Optional
from .supports import singleton
from .elasticsearchsaver import ELASTICSEARCH_SAVER

LOG = logging.getLogger('exception.reporter')

@singleton
class ExceptionReporter(object):
    """Configures address that would reports execption content to
    """
    def __init__(self):
        super().__init__()
        self.db_connector = 'es-should-be-configured'
        self.db_category = 'exceptions'
        self.address = '127.0.0.1:9200'
        self.es_index = 'exceptions'
        self.es_doc_type = '_doc'

    def configure(self, category: str, conf: dict) -> bool:
        connector = conf.get('connector', '')
        host = conf.get('host', '127.0.0.1')
        port = int(conf.get('port', 0))
        configure_result = True
        if 'es' == connector or 'elasticsearch' == connector:
            self.db_connector = 'es'
            self.address = '%s:%d' % (host, port)
            # self.es_doc_type = category
            configure_result = ELASTICSEARCH_SAVER.configure(self.address)
            if configure_result:
                # mappings = {
                #     'index_patterns': [self.es_index+'-*'],
                #     'template': {
                #         'mappings': {
                #             'properties': {
                #                 'key': { 'type': 'text' },
                #                 'type': { 'type': 'text' },
                #                 'level': { 'type': 'text' },
                #                 'endpoint': { 'type': 'text' },
                #                 'method': { 'type': 'text' },
                #                 '@timestamp': {
                #                     'type': 'date',
                #                 },
                #                 'timestamp': {
                #                     'type': 'date',
                #                 }
                #             }
                #         },
                #     }
                # }
                mappings = self.get_elasticsearch_template(self.es_index)
                configure_result = ELASTICSEARCH_SAVER.ensure_template(index=self.es_index, mappings=mappings)
        elif 'restful' == connector or 'rest' == connector:
            self.db_connector = 'restful'
            self.address = host
        else:
            LOG.error('configure exception reporter failed while unknown connector:%s', connector)
            return False
        self.db_category = category
        return configure_result

    def report(self, key: str, typ: str, endpoint: str, method: str, inputs: str, outputs: str, content: str, level: str = 'ERROR', extra: Optional[dict] = None) -> bool:
        cur_date_endfix = '-' + time.strftime('%Y-%m-%d', time.localtime())
        data = {
            'key': key,
            'type': typ,
            'level': level,
            'endpoint': endpoint,
            'method': method,
            'input': inputs,
            'output': outputs,
            'content': content,
            'timestamp': time.time()*1000
        }
        if extra:
            for k, v in extra.items():
                if k not in data:
                    data[k] = v

        if 'es' == self.db_connector:
            data['@timestamp'] = data['timestamp']
            return ELASTICSEARCH_SAVER.save(index=self.es_index+cur_date_endfix, doc_type=self.es_doc_type, body=data)
        else:
            # not supported
            log_texts = ['%s:[%s]' % (k, str(v)) for k, v in data.items()]
            LOG.error('reports of %s', ' '.join(log_texts))
            return False
        
    def get_elasticsearch_template(self, index: str) -> dict:
        mappings = {
            "order" : 0,
            "template": index + "-*",
            "index_patterns": [index + "-*"],
            "settings": {
                "index": {
                    "refresh_interval": "5s"
                }
            },
            "mappings": {
                "properties" : {
                    "@timestamp" : {
                        "type" : "date"
                    },
                    "@version" : {
                        "type" : "text"
                    },
                    'key': { 'type': 'text' },
                    'type': { 'type': 'text' },
                    'level': { 'type': 'text' },
                    'endpoint': { 'type': 'text' },
                    'method': { 'type': 'text' },
                    'input': { 'type': 'text' },
                    'output': { 'type': 'text' },
                    'timestamp': {
                        'type': 'date',
                    }
                }
            },
            "aliases" : { }
        }
        return mappings
