#!/usr/bin/python3

import re
import requests
# from feii.log import Log
from feii.config import Config
# from feii.init import Init
from feii.request import Request
# from feii.function import Function

class Index(Config, Request):
  def __init__(self,
    indices: str = [],
    index_details: str = [],
    shrink_indices: str = [],
    index_to_remove: str = [],
    index_current_num: str = {},
    invalid_size_indices: str = [],
    unmanaged_indices: str = [],
    not_hot_box_indices: str = [],
    not_hot_phase_indices: str = [],
    last_indices: str = [],
    not_last_indices: str = [],
    last_shrink_indices: str = [],
    not_last_shrink_indices: str = [],
    indices_no_alias: str = [],
    indices_no_necessary_alias: str = [],
    shrink_indices_no_alias: str = [],
    indices_not_write: str = [],
    indices_write_false: str = [],
    error_ilm_indices: str = [],
    error_ilm_shrink_indices: str = [],
    error_ilm_last_indices: str = [],
    error_ilm_not_last_indices: str = [],
    error_ilm_not_hot_phase_indices: str = [],
    delete_last_indices: str = [],
    timeout_last_indices: str = [],
    timeout_not_last_indices: str = [],
    prev_index_to_check: str = {},
    without_shrink_prev_index: str = '',
    new_index_name: str = '',
    indices_to_remove_by_ilm_policy: str = [],
    indices_with_age: str = [],
    list_indexes_to_delete: str = [],
    full_deleted_indexes: str = []
  ):
    super().__init__()
    self.indices = indices
    self.index_details = index_details
    self.shrink_indices = shrink_indices
    self.index_to_remove = index_to_remove
    self.index_current_num = index_current_num
    self.invalid_size_indices = invalid_size_indices
    self.unmanaged_indices = unmanaged_indices
    self.not_hot_box_indices = not_hot_box_indices
    self.not_hot_phase_indices = not_hot_phase_indices
    self.last_indices = last_indices
    self.not_last_indices = not_last_indices
    self.last_shrink_indices = last_shrink_indices
    self.not_last_shrink_indices = not_last_shrink_indices
    self.indices_no_alias = indices_no_alias
    self.indices_no_necessary_alias = indices_no_necessary_alias
    self.shrink_indices_no_alias = shrink_indices_no_alias
    self.indices_not_write = indices_not_write
    self.indices_write_false = indices_write_false
    self.error_ilm_indices = error_ilm_indices
    self.error_ilm_shrink_indices = error_ilm_shrink_indices
    self.error_ilm_last_indices = error_ilm_last_indices
    self.error_ilm_not_last_indices = error_ilm_not_last_indices
    self.error_ilm_not_hot_phase_indices = error_ilm_not_hot_phase_indices
    self.delete_last_indices = delete_last_indices
    self.timeout_last_indices = timeout_last_indices
    self.timeout_not_last_indices = timeout_not_last_indices
    self.prev_index_to_check = prev_index_to_check
    self.without_shrink_prev_index = without_shrink_prev_index
    self.new_index_name = new_index_name
    self.indices_to_remove_by_ilm_policy = indices_to_remove_by_ilm_policy
    self.indices_with_age = indices_with_age
    self.list_indexes_to_delete = list_indexes_to_delete
    self.full_deleted_indexes = full_deleted_indexes

  def debug_detail_index(self):
    self.alias = 'test'
    self.index = 'test-000001'

  def creating_array_index_details_in_open(self):
    for details in Config.index_pools[0].json():
      if details['status'] == 'open':
        self.index_details.append(details)

  def creating_array_index_to_remove(self):
    for details in self.index_details:
      if not self.index_pattern.match(details['index']):
        self.index_to_remove.append(details)
        self.logger.warning("[{0}] encountered a strange index name".format(details['index']))

  def remove_invalid_index_name_in_array(self):
    for details in self.index_to_remove:
      self.index_details.remove(details)

  def creating_array_indices(self):
    for details in self.index_details:
      index_details = details.copy()
      index_details['number'] = int(self.index_pattern.match(details['index']).group(3))
      index_details['index.alias'] = self.index_pattern.match(details['index']).group(2)
      self.indices.append(index_details)

  def creating_array_max_indices(self):
    for details in self.index_details:
      if self.index_current_num.get(self.index_pattern.match(details['index']).group(2), -1) < int(self.index_pattern.match(details['index']).group(3)):
        self.index_current_num[self.index_pattern.match(details['index']).group(2)] = int(self.index_pattern.match(details['index']).group(3))

  def creating_array_invalid_size_index(self):
    for index in self.indices:
      if index['pri.store.size'] is None or int(index['pri.store.size']) <= self.MAX_CURRENT_INDEX_SIZE_GB:
        self.invalid_size_indices.append(index)

  def creating_array_unmanaged_index(self):
    for index in self.indices:
      if not Config.ilm_list['indices'][index['index']]['managed']:
        self.unmanaged_indices.append(index)
        self.logger.warning("[{0}] not management".format(index['index']))

  def creating_array_not_hot_box_index(self):
    for index in self.indices:
      if Config.settings_list[index['index']]['settings']['index']['routing']['allocation']['require']['box_type'] != 'hot':
        self.not_hot_box_indices.append(index)

  def creating_array_not_hot_phase_index(self):
    for index in self.indices:
      if 'phase' in Config.ilm_list['indices'][index['index']] and Config.ilm_list['indices'][index['index']]['phase'] != 'hot':
        self.not_hot_phase_indices.append(index)

  def creating_array_shrink_index(self):
    for index in self.indices:
      if self.index_pattern.match(index['index']).group(1):
        self.shrink_indices.append(index)

  def creating_array_last_index(self):
    for index in self.indices:
      if self.index_current_num[index['index.alias']] == index['number']:
        self.last_indices.append(index)

  def creating_array_not_last_index(self):
    for index in self.indices:
      if self.index_current_num[index['index.alias']] != index['number']:
        self.not_last_indices.append(index)

  def creating_array_last_shrink_index(self):
    for index in self.shrink_indices:
      if self.index_current_num[index['index.alias']] == index['number']:
        self.last_shrink_indices.append(index)

  def creating_array_not_last_shrink_index(self):
    for index in self.shrink_indices:
      if self.index_current_num[index['index.alias']] != index['number']:
        self.not_last_shrink_indices.append(index)

  def creating_array_no_alias_in_index(self):
    for index in self.indices:
      if not Config.alias_list[index['index']]['aliases']:
        self.indices_no_alias.append(index)

  def creating_array_no_necessary_alias_in_index(self):
    for index in self.indices:
      if not index['index.alias'] in Config.alias_list[index['index']]['aliases']:
        self.indices_no_necessary_alias.append(index)

  def creating_array_no_shrink_alias_in_index(self):
    for index in self.shrink_indices:
      alias = re.sub(r'(shrink-)', '', index['index'])
      if not alias in Config.alias_list[index['index']]['aliases']:
        self.shrink_indices_no_alias.append(index)

  def creating_array_not_write_in_index(self):
    for index in self.indices:
      if not 'is_write_index' in Config.alias_list[index['index']]['aliases'][index['index.alias']]:
        self.indices_not_write.append(index)

  def creating_array_write_false_in_index(self):
    for index in self.indices:
      if Config.alias_list[index['index']]['aliases'][index['index.alias']]['is_write_index'] == False:
        self.indices_write_false.append(index)

  def creating_array_error_ilm_index(self):
    for index in self.indices:
      if 'step' in Config.ilm_list['indices'][index['index']] and Config.ilm_list['indices'][index['index']]['step'] == "ERROR":
        index_details = index.copy()
        index_details['error.type'] = Config.ilm_list['indices'][index['index']]['step_info']['type']
        index_details['error.reason'] = Config.ilm_list['indices'][index['index']]['step_info']['reason']
        self.error_ilm_indices.append(index_details)

  def creating_array_error_ilm_shrink_index(self):
    for index in self.error_ilm_indices:
      if self.index_pattern.match(index['index']).group(1):
        self.error_ilm_shrink_indices.append(index)

  def creating_array_error_ilm_last_indices(self):
    for index in self.error_ilm_indices:
      if self.index_current_num[index['index.alias']] == index['number']:
        self.error_ilm_last_indices.append(index)

  def creating_array_error_ilm_not_last_indices(self):
    for index in self.error_ilm_indices:
      if self.index_current_num[index['index.alias']] != index['number']:
        self.error_ilm_not_last_indices.append(index)

  def creating_array_error_ilm_not_hot_phase_indices(self):
    for index in self.error_ilm_indices:
      if 'phase' in Config.ilm_list['indices'][index['index']] and Config.ilm_list['indices'][index['index']]['phase'] != 'hot':
        self.error_ilm_not_hot_phase_indices.append(index)

  def creating_array_delete_index(self): #номер должен быть выше 3
    for index in self.last_indices:
      if int(self.index_pattern.match(index['index']).group(3)) > 3:
        self.delete_last_indices.append(index)

  def creating_array_not_shrink_prev_index(self):
    for index_array in self.indices:
      if index_array['index'] == self.without_shrink_prev_index:
        self.prev_index_to_check['index'] = self.without_shrink_prev_index
        self.prev_index_to_check['docs.count'] = index_array['docs.count']

  def creating_array_shrink_prev_index(self):
    for index_array in self.indices:
      if index_array['index'] == 'shrink-' + self.without_shrink_prev_index:
        self.prev_index_to_check['index'] = 'shrink-' + self.without_shrink_prev_index
        self.prev_index_to_check['docs.count'] = index_array['docs.count']

  def creating_array_timeout_last_index(self):
    for index in self.last_indices:
      if not 'unassigned' in Config.settings_list[index['index']]['settings']['index'] or Config.settings_list[index['index']]['settings']['index']['unassigned']['node_left']['delayed_timeout'] != self.HOT_DELAYED_TIMEOUT:
        self.timeout_last_indices.append(index)

  def creating_array_timeout_not_last_index(self):
    for index in self.not_last_indices:
      if not 'unassigned' in Config.settings_list[index['index']]['settings']['index'] or Config.settings_list[index['index']]['settings']['index']['unassigned']['node_left']['delayed_timeout'] != self.COLD_DELAYED_TIMEOUT:
        self.timeout_not_last_indices.append(index)

  def creating_array_index_to_remove_by_ilm_policy(self):
    for index in self.not_last_indices:
      if self.index_or_alias == index['index.alias']:
        self.indices_to_remove_by_ilm_policy.append(index['index'])

  def remove_invalid_indexes_in_array(self, indexes_array: str = []):
    for index in indexes_array:
      self.indices.remove(index)

  def remove_invalid_error_ilm_indexes_in_array(self, indexes_array: str = []):
    for index in indexes_array:
      self.error_ilm_indices.remove(index)

  def create_new_index(self):
    self.new_index_name = re.sub(r'(shrink-)', '', self.next_index)
    data = { "aliases": { self.alias: { "is_write_index" : False } } }
    self.request = requests.put("{0}/{1}?master_timeout={2}".format( self.ELASTIC_URL, self.new_index_name, self.MASTER_TIMEOUT), json=data)

  def check_create_new_index(self):
    if self.status_request():
      self.logger.info("Create new index [{0}] - True".format( self.new_index_name ))
      return True

  def update_index(self):
    self.request = requests.put("{0}/{1}/_settings?master_timeout={2}".format( self.ELASTIC_URL, self.index, self.MASTER_TIMEOUT ), json=self.data )

  def check_update_index(self):
    if self.status_request():
      self.logger.info("Updating index settings [{0}] - True".format( self.index ))
      return True

  def delete_index(self):
    self.request = requests.delete("{0}/{1}".format( self.ELASTIC_URL, self.index ))

  def check_delete_index(self):
    if self.status_request():
      self.logger.info("Deleting index [{0}] - True".format( self.index ))
      return True

  def reindexed(self):
    self.request = requests.post("{0}/_reindex?slices=60&refresh".format( self.ELASTIC_URL ), json=self.data)

  def check_reindexed(self):
    if self.status_request():
      self.logger.info("Reindexed [{0}] - True".format( self.index ))
      return True

  def request_find_service_index(self):
    self.request = requests.get("{0}/_cat/indices/{1}".format( self.ELASTIC_URL, self.SERVICE_INDEX ))

  def check_request_find_service_index(self):
    if self.status_request():
      self.logger.info("Service index [{0}] has already been created".format( self.SERVICE_INDEX ))
      return True

  def create_service_index(self):
    self.request = requests.put("{0}/{1}?master_timeout={2}".format( self.ELASTIC_URL, self.SERVICE_INDEX, self.MASTER_TIMEOUT))

  def check_create_service_index(self):
    if self.status_request():
      self.logger.info("Create service index [{0}] - True".format( self.SERVICE_INDEX ))
      return True

  def creating_array_index_with_age(self):
    indexes = requests.get("{0}/{1}/_search?format=json&filter_path=hits.hits._source,hits.hits._id".format( self.ELASTIC_URL, self.SERVICE_INDEX )).json()
    if 'hits' in indexes:
      for indices in indexes['hits']['hits']:
        index_details = indices.copy()
        index_details['_source']['policy.age'] = re.sub("[^0-9\.]", "", self.age_ilm_policies[indices['_source']['policy']]['policy.age'])
        self.indices_with_age.append(index_details)

  def update_array_index_with_age(self):
    for document in self.indices_with_age[:]:
      for index in document['_source']['indexes'][:]:
        if not index in Config.ilm_list['indices']:
          document['_source']['indexes'].remove(index)

  def creating_array_index_to_expired_policy(self):
    for indices in self.indices_with_age:
      for index in indices['_source']['indexes']:
        age = int(indices['_source']['policy.age'])
        if "d" in Config.ilm_list['indices'][index]['age'] and int(float(re.sub("[^0-9\.]", "", Config.ilm_list['indices'][index]['age']))) >= age:
          self.list_indexes_to_delete.append(index)

  def update_doc_to_service_index(self):
    for document in self.indices_with_age[:]:
      self.document_id = document['_id']
      document['_source'].pop('policy.age')
      data = document['_source']
      self.request = requests.post("{0}/{1}/_doc/{2}?timeout={3}".format( self.ELASTIC_URL,  self.SERVICE_INDEX, self.document_id, self.MASTER_TIMEOUT ), json=data)
      self.check_update_doc_to_service_index()

  def check_update_doc_to_service_index(self):
    if self.status_request():
      self.logger.info("Document [{0}] has been updated in the service index [{1}]".format( self.document_id, self.SERVICE_INDEX))
      return True

  def checking_for_empty_doc_to_service_index(self):
    for document in self.indices_with_age[:]:
      if not document['_source']['indexes']:
        self.full_deleted_indexes.append(document)
