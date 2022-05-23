#!/usr/bin/python3

import re
# from feii.log import Log
# from feii.config import Config
# from feii.init import Init
from feii.structure import Structure

class Aliases(Structure):
  def add_alias_for_indices(self):
    for index in self.indices_no_alias:
      self.index = index['index']
      self.alias = index['index.alias']
      if self.add_alias_for_index_and_check():
        self.indices_not_write.append(index)

  def add_necessary_alias_for_indices(self):
    for index in self.indices_no_necessary_alias:
      self.index = index['index']
      self.alias = index['index.alias']
      if self.add_alias_for_index_and_check():
        self.indices_not_write.append(index)

  def add_alias_for_shrink_indices(self):
    for index in self.shrink_indices_no_alias:
      self.index = index['index']
      self.alias = re.sub(r'(shrink-)', '', index['index'])
      self.add_alias_for_index_and_check()

  def add_alias_for_indices_check_mode(self):
    for index in self.indices_no_alias:
      self.logger.warning("[check_mode] Adding an alias [{0}] for index [{1}]".format( index['index.alias'], index['index'] ))

  def add_necessary_alias_for_indices_check_mode(self):
    for index in self.indices_no_necessary_alias:
      self.logger.warning("[check_mode] Adding an alias [{0}] for index [{1}]".format( index['index.alias'], index['index'] ))

  def add_alias_for_shrink_indices_check_mode(self):
    for index in self.shrink_indices_no_alias:
      self.logger.warning("[check_mode] Adding an alias [{0}] for index [{1}]".format( re.sub(r'(shrink-)', '', index['index']), index['index'] ))

  def create_write_indices(self):
    for index in self.indices_not_write:
      self.index = index['index']
      self.alias = index['index.alias']

      if not self.add_write_enable_for_index_and_check():
        self.logger.error("Failed enable write to next index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

  def add_write_in_indices(self):
    for index in self.indices_not_write:
      self.index = index['index']
      self.alias = index['index.alias']

      if not self.add_write_disable_for_index_and_check():
        self.logger.error("Failed add alias [{0}] to index [{1}] and disable write".format( self.alias, self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = self.find_prev_index()
      if not self.add_write_disable_for_index_and_check():
        self.logger.error("Failed disable write to prev index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = index['index']
      if not self.add_write_enable_for_index_and_check():
        self.logger.error("Failed enable write to index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

  def add_write_in_indices_check_mode(self):
    for index in self.indices_not_write:
      self.logger.warning("[check_mode] Last index [{0}] no write capability".format( index['index'] ))
