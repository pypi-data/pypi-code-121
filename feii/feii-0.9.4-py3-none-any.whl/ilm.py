#!/usr/bin/python3

# import re
import requests
# from feii.log import Log
from feii.config import Config
from feii.request import Request
# from feii.function import Function

class Ilm(Config, Request):
  def __init__(self,
    ilm_info_for_index: str = {},
    age_ilm_policies: str = {}
  ):
    super().__init__()
    self.ilm_info_for_index = ilm_info_for_index
    self.age_ilm_policies = age_ilm_policies

  def debug_detail_index(self):
    self.alias = 'test'
    self.index = 'test-000001'

  def rollover_index(self):
    return requests.post("{0}/{1}/_rollover?master_timeout={2}".format( self.ELASTIC_URL, self.alias, self.MASTER_TIMEOUT ))

  def check_create_next_index(self):
    self.request = requests.get("{0}/{1}/_ilm/explain".format( self.ELASTIC_URL, self.next_index ))

  def check_rollover_index(self):
    if self.status_request():
      self.logger.info("Rollover index for alias [{0}], new index [{1}] is created".format( self.alias, self.next_index ))
      return True

  def ilm_retry_for_index(self):
    self.request = requests.post("{0}/{1}/_ilm/retry?master_timeout={2}".format( self.ELASTIC_URL, self.index, self.MASTER_TIMEOUT ))

  def check_ilm_retry_for_index(self):
    if self.status_request():
      self.logger.info("Retrying ILM for index [{0}] - True".format( self.index ))
      return True

  def current_ilm_info_for_index(self):
    self.request = requests.get("{0}/{1}/_ilm/explain".format( self.ELASTIC_URL, self.index )).json()

  def create_current_ilm_info_for_index(self):
    self.ilm_info_for_index['phase'] = self.request['indices'][self.index]['phase']
    self.ilm_info_for_index['action'] = self.request['indices'][self.index]['action']
    self.ilm_info_for_index['step'] = self.request['indices'][self.index]['step']

  def next_step_index_in_warm(self):
    self.data = { "current_step": { "phase": self.ilm_info_for_index['phase'], "action": self.ilm_info_for_index['action'], "name": self.ilm_info_for_index['step']}, "next_step": { "phase": "warm", "action": "set_priority", "name": "set_priority" } }

  def next_step_index_in_cold(self):
    self.data = { "current_step": { "phase": self.ilm_info_for_index['phase'], "action": self.ilm_info_for_index['action'], "name": self.ilm_info_for_index['step']}, "next_step": { "phase": "cold", "action": "set_priority", "name": "set_priority" } }

  def request_step_for_index(self):
    self.request = requests.post("{0}/_ilm/move/{1}?master_timeout={2}".format( self.ELASTIC_URL, self.index, self.MASTER_TIMEOUT ), json=self.data )

  def check_next_step_for_index(self):
    if self.status_request():
      self.logger.info("Next step ILM for index [{0}] - True".format( self.index ))
      return True

  def check_re_step_for_index(self):
    if self.status_request():
      self.logger.info("Re step ILM for index [{0}] - True".format( self.index ))
      return True

  def remove_block_index(self):
    data = { "index": { "blocks": { "read_only_allow_delete": False } } }
    self.request = requests.put("{0}/{1}/_settings?master_timeout={2}".format( self.ELASTIC_URL, self.index, self.MASTER_TIMEOUT ), json=data )

  def check_remove_block_index(self):
    if self.status_request():
      self.logger.info("Remove cluster block for index [{0}] - True".format( self.index ))
      return True

  def remove_ilm_policy(self):
    self.request = requests.post("{0}/{1}/_ilm/remove?master_timeout={2}".format( self.ELASTIC_URL, self.index, self.MASTER_TIMEOUT ))

  def check_remove_ilm_policy(self):
    if self.status_request():
      self.logger.info("Removing the ilm policy - True")
      return True

  def adding_new_ilm_policy(self):
    data = { "index.lifecycle.name": self.policy }
    self.request = requests.put("{0}/{1}/_settings?master_timeout={2}".format( self.ELASTIC_URL, self.index, self.MASTER_TIMEOUT ), json=data )

  def check_adding_new_ilm_policy(self):
    if self.status_request():
      self.logger.info("New ilm policy [{0}] added to index [{1}]".format( self.policy, self.index ))
      return True

  def creating_array_age_ilm_policy(self):
    for policy in Config.ilm_policy:
      if 'delete' in Config.ilm_policy[policy]['policy']['phases']:
        self.age_ilm_policies[policy] = { "policy.age": Config.ilm_policy[policy]['policy']['phases']['delete']['min_age'] }
