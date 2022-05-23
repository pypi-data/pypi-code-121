#!/usr/bin/python3

import click
from feii.main import class_structure, class_log, logging_level, updating_variables, generating_variables_for_shards, generating_variables_for_unassigned_shard
from feii.mapping import Mapping

class_mapping = Mapping()
class_mapping.logger = class_log.logger

def start_fix_mapping_error_in_unassigned_shards(check_mode):
  if not check_mode:
    class_mapping.fix_mapping_error_in_unassigned_shards()

def start_check_mode_fix_mapping_error_in_unassigned_shards(check_mode):
  if check_mode:
    class_mapping.fix_mapping_error_in_unassigned_shards_check_mode()

@click.command(short_help='Starts fixing the mapping error in unassigned shards.')
@click.option(
  '-c', '--check-mode',
  is_flag=True,
  expose_value=True,
  help='Only displaying actions, without performing them.'
)
@click.option(
  '-l', '--log-level',
  default='info',
  show_default=True,
  expose_value=True,
  help='Set the logging level ("debug"|"info"|"warning"|"error"|"critical")'
)
@click.option(
  '-P', '--path-to-file',
  default='',
  expose_value=True,
  help='path'
)
def cli(check_mode, log_level, path_to_file):
  """Starts fixing the mapping error in unassigned shards"""

  logging_level(log_level)
  class_log.logger.info("Starts fixing the mapping error in unassigned shards")

  updating_variables(path_to_file)

  generating_variables_for_shards()
  generating_variables_for_unassigned_shard()

  start_fix_mapping_error_in_unassigned_shards(check_mode)
  start_check_mode_fix_mapping_error_in_unassigned_shards(check_mode)

if __name__ == "__main__":
  cli()
