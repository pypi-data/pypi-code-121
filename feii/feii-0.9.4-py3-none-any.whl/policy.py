#!/usr/bin/python3

import re
import requests
from feii.structure import Structure

class Policy(Structure):
  def __init__(self,
    index_or_alias: str = ""
  ):
    super().__init__()
    self.index_or_alias = index_or_alias

  def update_ilm_policy(self, set_index: str = '', set_alias: str = '', set_policy: str = ''):
    self.check_service_index()

    self.index = set_index
    self.alias = set_alias
    self.policy = set_policy

    self.check_on_alias()
    self.check_on_index()

    if self.index and not self.check_for_latest_index():
      self.logger.warning("The specified index [{0}] is not the last one".format( self.index ))
      self.find_latest_index()

    if self.alias:
      self.find_latest_index()

    self.remove_ilm_policy()
    self.check_remove_ilm_policy()

    self.adding_new_ilm_policy()
    self.check_adding_new_ilm_policy()

    self.creating_array_index_to_remove_by_ilm_policy()
    self.writing_to_service_index()
    self.check_writing_to_service_index()

  def update_ilm_policy_check_mode(self, set_index: str = '', set_alias: str = '', set_policy: str = ''):
    self.index = set_index
    self.alias = set_alias
    self.policy = set_policy

    self.check_on_alias()
    self.check_on_index()

    if self.index and not self.check_for_latest_index():
      self.logger.warning("The specified index [{0}] is not the last one".format( self.index ))
      self.find_latest_index()

    if self.alias:
      self.find_latest_index()

    self.logger.warning("[check_mode] Updating the index [{0}] policy on the [{1}]".format( self.index, self.policy ))

  def check_for_latest_index(self):
    for index in self.last_indices:
      if self.index == index['index']:
        return True

  def check_on_alias(self):
    if not self.index and self.alias:
      self.index_or_alias = re.sub(r'(shrink-)', '', self.alias)

  def check_on_index(self):
    if not self.alias and self.index:
      self.index_or_alias = re.sub(r'(shrink-)', '', self.index[:-7])

  def find_latest_index(self):
    for index in self.last_indices:
      if self.index_or_alias == index['index.alias']:
        self.index = index['index']

  def writing_to_service_index(self):
    if self.indices_to_remove_by_ilm_policy:
      data = { "indexes": self.indices_to_remove_by_ilm_policy, "policy": self.policy }
      self.request = requests.post("{0}/{1}/_doc/?timeout={2}".format( self.ELASTIC_URL,  self.SERVICE_INDEX, self.MASTER_TIMEOUT ), json=data )

  def check_writing_to_service_index(self):
    if self.indices_to_remove_by_ilm_policy and self.status_request():
      self.logger.info("The array of indexes is written to the service index [{0}]".format( self.SERVICE_INDEX))
      return True
