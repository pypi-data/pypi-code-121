#!/usr/bin/python3

# import re
# import requests
# from feii.log import Log
# from feii.config import Config
# from feii.request import Request
# from feii.init import Init
from feii.structure import Structure

class Update(Structure):
  def debug_detail_index(self):
    self.index = 'test-000001'
    self.index_docs_count = 0

  def failed_check_update_timeout_index(self):
    if not self.update_index_and_check():
      self.logger.error("Failed updating timeout index [{0}]".format( self.index ))
      self.logger.warning("Skip this index and continue with the following index")

  def update_timeout_for_last_indexes(self):
    for index in self.timeout_last_indices:
      self.index = index['index']
      self.data = { "settings": { "index.unassigned.node_left.delayed_timeout": self.HOT_DELAYED_TIMEOUT } }

      self.failed_check_update_timeout_index()

  def update_timeout_for_not_last_indexes(self):
    for index in self.timeout_not_last_indices:
      self.index = index['index']
      self.data = { "settings": { "index.unassigned.node_left.delayed_timeout": self.COLD_DELAYED_TIMEOUT } }

      self.failed_check_update_timeout_index()

  def update_timeout_for_last_indexes_check_mode(self):
    for index in self.timeout_last_indices:
      self.logger.warning("[check_mode] Updating last index [{0}] settings (delayed_timeout - {1})".format( index['index'], self.HOT_DELAYED_TIMEOUT ))

  def update_timeout_for_not_last_indexes_check_mode(self):
    for index in self.timeout_not_last_indices:
      self.logger.warning("[check_mode] Updating not last index [{0}] settings (delayed_timeout - {1})".format( index['index'], self.COLD_DELAYED_TIMEOUT ))
