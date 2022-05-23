#!/usr/bin/python3

# import re
# import time
# import requests
# from feii.log import Log
# from feii.config import Config
# from feii.init import Init
from feii.index import Index
from feii.shard import Shard
from feii.request import Request
from feii.ilm import Ilm
from feii.alias import Alias
from feii.cluster import Cluster
from feii.function import Function

class Structure(Index, Shard, Ilm, Alias, Function, Cluster, Request):
  def cluster_status(self):
    while True:
      self.get_status_cluster()

      if not self.check_count_relocating_shards_in_cluster():
        self.logger.warning("Number of relocating shards reaches {0}".format( self.cluster['relocating_shards'] ))
        self.retry += 1
        self.time_sleep()
        continue

      if not self.check_count_pending_tasks_in_cluster():
        self.logger.warning("Number of pending tasks reaches {0}".format( self.cluster['number_of_pending_tasks'] ))
        self.retry += 1
        self.time_sleep()
        continue

      if self.check_count_relocating_shards_in_cluster() and self.check_count_pending_tasks_in_cluster():
        self.retry = 0
        break

  def rollover_index_and_check(self):
    self.cluster_status()
    self.rollover_index()
    self.find_next_index()
    self.check_create_next_index()
    return self.check_rollover_index()

  def update_index_and_check(self):
    self.cluster_status()
    self.update_index()
    return self.check_update_index()

  def delete_index_and_check(self):
    self.delete_index()
    return self.check_delete_index()

  def reindexed_and_check(self):
    self.cluster_status()
    self.reindexed()
    return self.check_reindexed()

  def add_write_disable_for_index_and_check(self):
    self.add_alias_for_index_and_write_disable()
    self.cluster_status()
    self.request_add_alias_for_index()
    return self.check_disable_write_for_index()

  def add_write_enable_for_index_and_check(self):
    self.add_alias_for_index_and_write_enable()
    self.cluster_status()
    self.request_add_alias_for_index()
    return self.check_enable_write_for_index()

  def ilm_retry_index_and_check(self):
    self.cluster_status()
    self.ilm_retry_for_index()
    return self.check_ilm_retry_for_index()

  def next_step_for_index_and_check(self):
    self.current_ilm_info_for_index()
    self.create_current_ilm_info_for_index()
    self.next_step_for_not_shrink_index()
    self.next_step_for_shrink_index()
    self.cluster_status()
    self.request_step_for_index()
    return self.check_next_step_for_index()

  def re_step_for_index_and_check(self):
    self.current_ilm_info_for_index()
    self.create_current_ilm_info_for_index()
    self.next_step_index_in_warm()
    self.cluster_status()
    self.request_step_for_index()
    return self.check_re_step_for_index()

  def next_step_for_not_shrink_index(self):
    if not self.index_pattern.match(self.index).group(1):
      self.next_step_index_in_warm()

  def next_step_for_shrink_index(self):
    if self.index_pattern.match(self.index).group(1):
      self.next_step_index_in_cold()

  def not_next_step_for_index_and_check(self):
    if not self.next_step_for_index_and_check():
      self.logger.error("Failed next step to index [{0}]".format( self.index ))

  def not_delete_index_and_check(self):
    if not self.delete_index_and_check():
      self.logger.error("Failed delete index [{0}]".format( self.index ))
      return False

  def create_new_index_and_check(self):
    self.find_next_index()
    self.cluster_status()
    self.create_new_index()
    return self.check_create_new_index()

  def create_index_and_check(self):
    self.cluster_status()
    self.create_new_index()
    return self.check_create_new_index()

  def add_alias_for_index_and_check(self):
    self.add_alias_for_index()
    self.cluster_status()
    self.request_add_alias_for_index()
    return self.check_add_alias_for_index()

  def check_service_index(self):
    self.request_find_service_index()

    if not self.check_request_find_service_index():
      self.create_service_index()
      self.check_create_service_index()
