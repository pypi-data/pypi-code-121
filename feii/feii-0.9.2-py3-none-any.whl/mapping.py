#!/usr/bin/python3

# import re
import requests
# from feii.log import Log
# from feii.config import Config
# from feii.init import Init
from feii.structure import Structure
# from feii.function import Function

class Mapping(Structure):
  def check_dock_count_indexes(self):
    for count in range(3):
      self.retry += 1; self.time_sleep()
      index = requests.get("{0}/_cat/indices/{1}?format=json&bytes=gb".format( self.ELASTIC_URL, self.index )).json()
      new_index = requests.get("{0}/_cat/indices/{1}?format=json&bytes=gb".format( self.ELASTIC_URL, self.next_index )).json()
      if new_index[0]['docs.count'] == index[0]['docs.count']:
        break
    else:
      self.retry = 0; return False

  def cycle_reindexing(self):
    for count in range(5):
      self.cluster_status()
      self.data = { "conflicts": "proceed", "source": { "index": self.index }, "dest": { "index": self.next_index, "op_type": "create" } }
      if self.reindexed_and_check():
        break
    else:
      self.retry = 0; return False

  def cycle_next_steps(self):
    for count in range(3):
      self.cluster_status()
      if self.next_step_for_index_and_check():
        break
    else:
      self.retry = 0; return False

  def fix_mapping_error_in_unassigned_shards_using_retry(self):
    for shard in self.unassigned_shards:

      self.index = shard['index.name']
      self.data = { "settings": { "index.routing.allocation.require._id": None } }
      if not self.update_index_and_check():
        self.logger.error("Failed updating settings index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      if not self.re_step_for_index_and_check():
        self.logger.error("Failed ilm retry to warm index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = shard['index']
      if not self.delete_index_and_check():
        self.logger.error("Failed delete unassigned shrink index [{0}]".format( shard['index'] ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

  def fix_mapping_error_in_unassigned_shards(self):
    for shard in self.unassigned_shards:

      self.alias = shard['index.alias'] + '-reindexed'
      self.next_index = shard['index.alias'] + '-reindexed-' + shard['index.name'][-6:]
      if not self.create_index_and_check():
        self.logger.error("Failed create index [{0}]".format( self.new_index_name ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = self.next_index
      self.data = { "settings": { "index.number_of_replicas": 0 } }
      if not self.update_index_and_check():
        self.logger.error("Failed updating settings index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = shard['index.name']
      if self.cycle_reindexing() is False:
        self.logger.error("Failed reindexed [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      if self.check_dock_count_indexes() is False:
        self.logger.error("Failed check dock count [{0}]".format( self.new_index_name ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      if not self.delete_index_and_check():
        self.logger.error("Failed delete index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = shard['index']
      if not self.delete_index_and_check():
        self.logger.error("Failed delete unassigned shrink index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.alias = shard['index.alias']
      self.next_index = shard['index.name']
      if not self.create_index_and_check():
        self.logger.error("Failed create index [{0}]".format( self.new_index_name ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = shard['index.alias'] + '-reindexed-' + shard['index.name'][-6:]
      if self.cycle_reindexing() is False:
        self.logger.error("Failed reindexed [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      if self.check_dock_count_indexes() is False:
        self.logger.error("Failed check dock count [{0}]".format( self.new_index_name ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      if not self.delete_index_and_check():
        self.logger.error("Failed delete reindexed index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = shard['index.name']
      if self.cycle_next_steps() is False:
        self.logger.error("Failed next step to index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

  def fix_mapping_error_in_unassigned_shards_check_mode(self):
    for shard in self.unassigned_shards:
      self.logger.warning("[check_mode] Shard index [{0}] - unassigned details [{1}]".format( shard['index'], shard['unassigned.reason'] ))
