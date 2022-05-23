#!/usr/bin/python3

# from feii.log import Log
# from feii.config import Config
# from feii.init import Init
from feii.structure import Structure

class FixError(Structure):
  def not_ilm_retry_index_and_check(self):
    if not self.ilm_retry_index_and_check():
      self.logger.error("Failed ilm retry to next index [{0}]".format( self.index ))

  def remove_block_index_and_check(self):
    self.remove_block_index()
    return self.check_remove_block_index()

  def not_remove_block_index_and_check(self):
    if not self.remove_block_index_and_check():
      self.logger.error("Failed remove cluster block to index [{0}]".format( self.index ))
      return True

  def fix_error_ilm_last_index(self):
    for index in self.error_ilm_last_indices:
      self.index = index['index']

      if index['error.type'] == "process_cluster_event_timeout_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "illegal_state_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "index_closed_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "illegal_argument_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "resource_already_exists_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "cluster_block_exception":
        if self.not_remove_block_index_and_check():
          continue
        self.not_ilm_retry_index_and_check()

  def fix_error_ilm_not_hot_phase_index(self):
    for index in self.error_ilm_not_hot_phase_indices:
      self.index = index['index']

      if index['error.type'] == "process_cluster_event_timeout_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "illegal_state_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "index_closed_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "illegal_argument_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "resource_already_exists_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "cluster_block_exception":
        if self.not_remove_block_index_and_check():
          continue
        self.not_ilm_retry_index_and_check()

  def fix_error_ilm_not_last_index(self):
    for index in self.error_ilm_not_last_indices:
      self.index = index['index']

      if index['error.type'] == "process_cluster_event_timeout_exception":
        self.not_next_step_for_index_and_check()

      if index['error.type'] == "illegal_state_exception":
        self.not_next_step_for_index_and_check()

      if index['error.type'] == "index_closed_exception":
        self.not_next_step_for_index_and_check()

      if index['error.type'] == "illegal_argument_exception":
        self.not_next_step_for_index_and_check()

      if index['error.type'] == "resource_already_exists_exception":
        self.not_next_step_for_index_and_check()

      if index['error.type'] == "cluster_block_exception":
        if self.not_remove_block_index_and_check():
          continue
        self.not_next_step_for_index_and_check()

  def fix_error_ilm_shrink_index(self):
    for index in self.error_ilm_shrink_indices:
      self.index = index['index']

      if index['error.type'] == "process_cluster_event_timeout_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "index_closed_exception":
        self.not_ilm_retry_index_and_check()

      if index['error.type'] == "null_pointer_exception":
        self.not_ilm_retry_index_and_check()

  def fix_error_ilm_last_index_in_check_mode(self):
    for index in self.error_ilm_last_indices:
      self.logger.warning("[check_mode] Fix ilm error [{0}] for index [{1}]".format( index['error.type'], index['index'] ))

  def fix_error_ilm_not_hot_phase_index_in_check_mode(self):
    for index in self.error_ilm_not_hot_phase_indices:
      self.logger.warning("[check_mode] Fix ilm error [{0}] for index [{1}]".format( index['error.type'], index['index'] ))

  def fix_error_ilm_not_last_index_in_check_mode(self):
    for index in self.error_ilm_not_last_indices:
      self.logger.warning("[check_mode] Fix ilm error [{0}] for index [{1}]".format( index['error.type'], index['index'] ))

  def fix_error_ilm_shrink_index_in_check_mode(self):
    for index in self.error_ilm_shrink_indices:
      self.logger.warning("[check_mode] Fix ilm error [{0}] for index [{1}]".format( index['error.type'], index['index'] ))
