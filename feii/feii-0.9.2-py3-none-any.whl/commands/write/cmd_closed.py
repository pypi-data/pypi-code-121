#!/usr/bin/python3

import click
from feii.main import class_structure, class_log, logging_level, updating_variables, generating_variables_for_indices, generating_variables_for_write_close_indices, deleting_unnecessary_variables
from feii.write import Write

class_write = Write()
class_write.logger = class_log.logger

def start_creating_new_index_for_writing(check_mode):
  if not check_mode:
    class_write.adding_no_write_to_array()
    class_write.adding_disabled_write_to_array()
    class_write.creating_new_index_for_writing()

def start_check_mode_creating_new_index_for_writing(check_mode):
  if check_mode:
    class_write.no_write_last_indices_check_mode()
    class_write.write_disabled_in_last_indices_check_mode()

@click.command(short_help='Creates indexes from closed ones and includes write.')
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
  """Creates indexes from closed ones and includes write"""

  logging_level(log_level)
  class_log.logger.info("Starts creates indexes from closed ones and includes write")

  updating_variables(path_to_file)

  generating_variables_for_indices()
  generating_variables_for_write_close_indices()
  deleting_unnecessary_variables()

  start_creating_new_index_for_writing(check_mode)
  start_check_mode_creating_new_index_for_writing(check_mode)

if __name__ == "__main__":
  cli()
