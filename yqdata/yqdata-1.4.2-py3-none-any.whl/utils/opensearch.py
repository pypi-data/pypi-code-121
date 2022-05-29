# -*- coding: UTF-8 -*-
# Author: Hu Min
# Date: 2021-11-30
from opensearchpy import OpenSearch
import json
import pandas as pd
from pandas import json_normalize
import logging
import logging.config

class OpenSearchUtils:
    def __init__(self):
        logging.debug("init open search")
        self.client = OpenSearch(["10.10.20.1","10.10.20.2","10.10.20.3"])

    def get_index_name(self, index_name):
        return self.config['index_name_prefix'] + index_name

    def get_df_from_es(self, res):
        logging.debug("get df from es")
        
        df = pd.DataFrame()
        appended_data = []

        frame = pd.DataFrame.from_dict([document['_source'] for document in res["hits"]["hits"]])
        appended_data.append(frame)

        if len(appended_data) > 0: 
            df = pd.concat(appended_data, ignore_index=True, sort = False)
        del appended_data
        return df
    
    def search(self, index, body):
        logging.debug("search by query, index: %s, query: %s", index, body)
        res = self.client.search(index=index, body=body)
        return self.get_df_from_es(res)

    def search_by_condition(self, index, must=[], should=[], must_not=[], size=10000, fields=['*'], sort=''):
        logging.debug("search by query, index: %s, must: %s, should: %s, must_not: %s", index, must, should, must_not)
        if fields is None or len(fields) > 0:
            res = self.client.search(index=index, body={"size": size, "_source": fields,"query":{"bool":{"must":must,"should":should,"must_not":must_not}}}, sort=sort, request_timeout=30)
        else:
            res = self.client.search(index=index, body={"size": size, "query":{"bool":{"must":must,"should":should,"must_not":must_not}}}, sort=sort, request_timeout=30)
        return self.get_df_from_es(res)

def get_client():
    return OpenSearchUtils()