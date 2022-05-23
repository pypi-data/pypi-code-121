#!/usr/bin/python3

# from feii.log import Log
# from feii.config import Config
# from feii.init import Init
from feii.structure import Structure

class Rollover(Structure):
  def rollover_last_index(self):
    for index in self.last_indices:
      self.index = index['index']
      self.alias = index['index.alias']
      self.logger.warning("Index [{0}][{1}gb] is larger the allowed size - {2}gb".format( self.index, int(index['pri.store.size']), self.MAX_CURRENT_INDEX_SIZE_GB ))

      if not self.rollover_index_and_check():
        self.logger.error("Not rollover index for alias [{0}]".format( self.alias ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.not_next_step_for_index_and_check()

  def rollover_not_last_index(self):
    for index in self.not_last_indices:
      self.index = index['index']
      self.alias = index['index.alias']
      self.logger.warning("Index [{0}][{1}gb] is larger the allowed size - {2}gb".format( self.index, int(index['pri.store.size']), self.MAX_CURRENT_INDEX_SIZE_GB ))

      self.index = self.find_next_index()
      if not self.add_write_disable_for_index_and_check():
        self.logger.error("Failed add alias [{0}] to next index [{1}] and disable write".format( self.alias, self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = index['index']
      if not self.add_write_disable_for_index_and_check():
        self.logger.error("Failed disable write to index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = self.find_next_index()
      if not self.add_write_enable_for_index_and_check():
        self.logger.error("Failed enable write to next index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      if not self.ilm_retry_index_and_check():
        self.logger.error("Failed ilm retry to next index [{0}]".format( self.index ))

      self.index = index['index']
      self.not_next_step_for_index_and_check()

  def rollover_last_shrink_index(self):
    for index in self.last_shrink_indices:
      self.index = index['index']
      self.alias = index['index.alias']
      self.logger.warning("Index [{0}][{1}gb] is larger the allowed size - {2}gb".format( self.index, int(index['pri.store.size']), self.MAX_CURRENT_INDEX_SIZE_GB ))

      if not self.create_new_index_and_check():
        self.logger.error("Failed create new index [{0}]".format( self.new_index_name ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      if not self.add_write_disable_for_index_and_check():
        self.logger.error("Failed disable write to index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = self.new_index_name
      if not self.add_write_enable_for_index_and_check():
        self.logger.error("Failed enable write to next index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      if not self.ilm_retry_index_and_check():
        self.logger.error("Failed ilm retry to next index [{0}]".format( self.index ))

      self.index = index['index']
      self.not_next_step_for_index_and_check()

  def rollover_last_index_in_check_mode(self):
    for index in self.last_indices:
      self.logger.warning("[check_mode] Las index [{0}][{1}gb] is larger the allowed size - {2}gb".format( index['index'], int(index['pri.store.size']), self.MAX_CURRENT_INDEX_SIZE_GB ))

  def rollover_not_last_index_in_check_mode(self):
    for index in self.not_last_indices:
      self.logger.warning("[check_mode] Not last index [{0}][{1}gb] is larger the allowed size - {2}gb".format( index['index'], int(index['pri.store.size']), self.MAX_CURRENT_INDEX_SIZE_GB ))

  def rollover_last_shrink_index_in_check_mode(self):
    for index in self.last_shrink_indices:
      self.logger.warning("[check_mode] Last shrink index [{0}][{1}gb] is larger the allowed size - {2}gb".format( index['index'], int(index['pri.store.size']), self.MAX_CURRENT_INDEX_SIZE_GB ))

  def next_step_for_not_last_index(self):
    for index in self.not_last_indices:
      self.index = index['index']

      self.not_next_step_for_index_and_check()

  def next_step_for_not_last_index_in_check_mode(self):
    for index in self.not_last_indices:
      self.index = index['index']
      self.logger.warning("[check_mode] The index [{0}] is in the wrong step".format( index['index'] ))
