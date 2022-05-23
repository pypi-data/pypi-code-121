#!/usr/bin/python3

# import re
# import requests
# from feii.log import Log
# from feii.config import Config
# from feii.init import Init
from feii.structure import Structure
# from feii.function import Function

class Write(Structure):
  def __init__(self,
    closed_indices: str = [],
  ):
    super().__init__()
    self.closed_indices = closed_indices

  def adding_no_write_to_array(self):
    for index in self.indices_not_write:
      self.closed_indices.append(index)

  def adding_disabled_write_to_array(self):
    for index in self.indices_write_false:
      self.closed_indices.append(index)

  def creating_new_index_for_writing(self):
    for index in self.closed_indices:
      self.index = index['index']
      self.alias = index['index.alias']

      if not self.create_new_index_and_check():
        self.logger.error("Failed create new index [{0}]".format( self.new_index_name ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

      self.index = self.new_index_name
      if not self.add_write_enable_for_index_and_check():
        self.logger.error("Failed enable write to next index [{0}]".format( self.index ))
        self.logger.warning("Skip this index and continue with the following index")
        continue

  def no_write_last_indices_check_mode(self):
    for index in self.indices_not_write:
      self.logger.warning("[check_mode] Not write last index [{0}]".format( index['index'] ))

  def write_disabled_in_last_indices_check_mode(self):
    for index in self.indices_write_false:
      self.logger.warning("[check_mode] Write false last index [{0}]".format( index['index'] ))
