#!/usr/bin/python3

# import click
from feii.log import Log
from feii.config import Config
from feii.init import Init
from feii.structure import Structure
from feii.path_to_file import PathToFile

class_config = Config
class_path_to_file = PathToFile()
class_structure = Structure()
class_log = Log()

class_log.remove_old_log_file()
class_log.get_file_handler()
class_log.get_stream_handler()
class_log.get_logger()

def updating_variables(path_to_file):
  class_config.path = path_to_file
  class_path_to_file.get_config()

def logging_level(level):
  if level:
    class_log.logging_level_critical(level)
    class_log.logging_level_error(level)
    class_log.logging_level_warning(level)
    class_log.logging_level_info(level)
    class_log.logging_level_debug(level)
    class_log.logging_level_notset(level)

def generating_variables_for_indices():
  class_config.index_pools = Init(count = 5).list_pools()
  class_config.ilm_list = class_config.index_pools[3].json()
  class_config.settings_list = class_config.index_pools[2].json()
  class_config.alias_list = class_config.index_pools[1].json()
  class_config.ilm_policy = class_config.index_pools[5].json()

  class_structure.logger = class_log.logger

  class_structure.creating_array_index_details_in_open()
  class_structure.creating_array_index_to_remove()
  class_structure.remove_invalid_index_name_in_array()
  class_structure.creating_array_indices()
  class_structure.creating_array_max_indices()

  del(class_structure.index_details)
  del(class_structure.index_to_remove)

def generating_variables_for_shards():
  class_config.index_pools = Init(count = 5).list_pools()
  class_config.ilm_list = class_config.index_pools[3].json()
  class_config.settings_list = class_config.index_pools[2].json()
  class_config.alias_list = class_config.index_pools[1].json()

  class_structure.logger = class_log.logger

  class_structure.creating_array_shard_details_in_primary()
  class_structure.creating_array_shard_not_duplicates()
  class_structure.creating_array_shard_to_remove()
  class_structure.remove_invalid_shard_name_in_array()
  class_structure.creating_array_shards()

  del(class_structure.shard_details)
  del(class_structure.shards_details)
  del(class_structure.shard_to_remove)

def generating_variables_for_unassigned_shard():
  class_structure.creating_array_unassigned_shard()

def generating_variables_for_delete():
  class_structure.creating_array_last_index()
  class_structure.creating_array_not_last_index()

  class_structure.creating_array_delete_index()

def generating_variables_for_alias():
  class_structure.creating_array_unmanaged_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.unmanaged_indices )

  class_structure.creating_array_shrink_index()

  class_structure.creating_array_no_alias_in_index()
  class_structure.creating_array_no_necessary_alias_in_index()
  class_structure.creating_array_no_shrink_alias_in_index()

def generating_variables_for_alias_not_shrink():
  class_structure.creating_array_unmanaged_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.unmanaged_indices )

  class_structure.creating_array_shrink_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.shrink_indices )

  class_structure.creating_array_no_alias_in_index()
  class_structure.creating_array_no_necessary_alias_in_index()

def generating_variables_for_write_alias():
  class_structure.creating_array_unmanaged_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.unmanaged_indices )

  class_structure.creating_array_shrink_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.shrink_indices )

  class_structure.creating_array_not_last_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.not_last_indices )

  class_structure.creating_array_no_alias_in_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.indices_no_alias )

  class_structure.creating_array_no_necessary_alias_in_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.indices_no_necessary_alias )

  class_structure.creating_array_not_write_in_index()

def generating_variables_for_rollover():
  class_structure.creating_array_invalid_size_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.invalid_size_indices )

def generating_variables_for_rollover_next_step():
  class_structure.creating_array_unmanaged_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.unmanaged_indices )

  class_structure.creating_array_not_hot_box_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.not_hot_box_indices )

  class_structure.creating_array_not_hot_phase_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.not_hot_phase_indices )

  class_structure.creating_array_shrink_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.shrink_indices )

  class_structure.creating_array_last_index()
  class_structure.creating_array_not_last_index()
  class_structure.creating_array_last_shrink_index()

def generating_variables_for_update():
  class_structure.creating_array_last_index()
  class_structure.creating_array_not_last_index()

  class_structure.creating_array_timeout_last_index()
  class_structure.creating_array_timeout_not_last_index()

def generating_variables_for_fix_error():
  class_structure.creating_array_unmanaged_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.unmanaged_indices )

  class_structure.creating_array_error_ilm_index()
  class_structure.creating_array_error_ilm_shrink_index()
  class_structure.remove_invalid_error_ilm_indexes_in_array( class_structure.error_ilm_shrink_indices )
  class_structure.creating_array_error_ilm_last_indices()

  class_structure.remove_invalid_error_ilm_indexes_in_array( class_structure.error_ilm_last_indices )
  class_structure.creating_array_error_ilm_not_hot_phase_indices()

  class_structure.remove_invalid_error_ilm_indexes_in_array( class_structure.error_ilm_not_hot_phase_indices )
  class_structure.creating_array_error_ilm_not_last_indices()

def generating_variables_for_write_close_indices():
  class_structure.creating_array_unmanaged_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.unmanaged_indices )

  class_structure.creating_array_not_last_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.not_last_indices )

  class_structure.creating_array_last_index()
  class_structure.creating_array_not_write_in_index()

  class_structure.remove_invalid_indexes_in_array( class_structure.indices_not_write )
  class_structure.creating_array_write_false_in_index()

def generating_variables_for_update_ilm_policy():
  class_structure.creating_array_unmanaged_index()
  class_structure.remove_invalid_indexes_in_array( class_structure.unmanaged_indices )

  class_structure.creating_array_last_index()
  class_structure.creating_array_not_last_index()

def deleting_unnecessary_variables():
  del(class_structure.invalid_size_indices)
  del(class_structure.unmanaged_indices)
  del(class_structure.not_hot_box_indices)
  del(class_structure.not_hot_phase_indices)
