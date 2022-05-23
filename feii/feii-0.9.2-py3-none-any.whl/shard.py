#!/usr/bin/python3

# import re
# import requests
# from feii.log import Log
from feii.config import Config
# from feii.init import Init
from feii.request import Request
# from feii.function import Function

class Shard(Config, Request):
  def __init__(self,
    shards: str = [],
    shard_details: str = [],
    shards_details: str = [],
    shard_to_remove: str = [],
    unassigned_shards: str = [],
  ):
    super().__init__()
    self.shards = shards
    self.shard_details = shard_details
    self.shards_details = shards_details
    self.shard_to_remove = shard_to_remove
    self.unassigned_shards = unassigned_shards

  def debug_detail_index(self):
    self.alias = 'test'
    self.index = 'test-000001'

  def creating_array_shard_details_in_primary(self):
    for details in Config.index_pools[4].json():
      if details['prirep'] == 'p':
        self.shards_details.append(details)

  def creating_array_shard_not_duplicates(self):
    seen = set()
    for details in self.shards_details:
      if tuple(details.items()) not in seen:
        seen.add(tuple(details.items()))
        self.shard_details.append(details)

  def creating_array_shard_to_remove(self):
    for details in self.shard_details:
      if not self.index_pattern.match(details['index']):
        self.shard_to_remove.append(details)
        self.logger.warning("[{0}] encountered a strange index name".format(details['index']))

  def remove_invalid_shard_name_in_array(self):
    for details in self.shard_to_remove:
      self.shard_details.remove(details)

  def creating_array_shards(self):
    for details in self.shard_details:
      shard_details = details.copy()
      shard_details['number'] = int(self.index_pattern.match(details['index']).group(3))
      shard_details['index.alias'] = self.index_pattern.match(details['index']).group(2)
      shard_details['index.name'] = self.index_pattern.match(details['index']).group(2) + '-' + self.index_pattern.match(details['index']).group(3)
      self.shards.append(shard_details)

  def creating_array_unassigned_shard(self):
    for shard in self.shards:
      if shard['state'] == 'UNASSIGNED':
        self.unassigned_shards.append(shard)
