#!/usr/bin/python3

import re

class Config:

  path: str = ''
  ELASTIC_URL: str = 'http://localhost:9200'

  def __init__(self,
    ES_URLS: str = [],
    MAX_CURRENT_INDEX_SIZE_GB: int = 50,
    MAX_RELOCATING: int = 25,
    MAX_TASKS: int = 500,
    MASTER_TIMEOUT: str = '2m',
    HOT_DELAYED_TIMEOUT: str = '10m',
    COLD_DELAYED_TIMEOUT: str = '25m',
    SERVICE_INDEX: str = '.feii_ilm',
    index_pattern: str = re.compile(r'^(shrink-)?(.+)-(\d{6})$'),
    index_pools: str = '',
    alias_list: str = '',
    settings_list: str = '',
    ilm_list: str = '',
    shards_list: str = '',
    ilm_policy: str = ''
  ):
    self.ES_URLS: str = [
      "{0}/_cat/indices?format=json&bytes=gb".format(self.ELASTIC_URL),
      "{0}/_alias".format(self.ELASTIC_URL),
      "{0}/*/_settings".format(self.ELASTIC_URL),
      "{0}/*/_ilm/explain".format(self.ELASTIC_URL),
      "{0}/_cat/shards/*?format=json&h=index,prirep,state,unassigned.reason,unassigned.details".format(self.ELASTIC_URL),
      "{0}/_ilm/policy".format(self.ELASTIC_URL),
    ]
    self.MAX_CURRENT_INDEX_SIZE_GB = MAX_CURRENT_INDEX_SIZE_GB
    self.MAX_RELOCATING = MAX_RELOCATING
    self.MAX_TASKS = MAX_TASKS
    self.MASTER_TIMEOUT = MASTER_TIMEOUT
    self.HOT_DELAYED_TIMEOUT = HOT_DELAYED_TIMEOUT
    self.COLD_DELAYED_TIMEOUT = COLD_DELAYED_TIMEOUT
    self.SERVICE_INDEX = SERVICE_INDEX
    self.index_pattern = index_pattern
    self.index_pools = index_pools
    self.alias_list = alias_list
    self.settings_list = settings_list
    self.ilm_list = ilm_list
    self.shards_list = shards_list
    self.ilm_policy = ilm_policy
