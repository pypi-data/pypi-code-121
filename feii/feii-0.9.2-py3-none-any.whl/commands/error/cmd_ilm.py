#!/usr/bin/python3

import click
from feii.main import class_structure, class_log, logging_level, updating_variables, generating_variables_for_indices, generating_variables_for_fix_error, deleting_unnecessary_variables
from feii.error import FixError

class_fix_error = FixError()
class_fix_error.logger = class_log.logger

def start_fix_error_ilm_all(check_mode):
  if not check_mode:
    class_fix_error.fix_error_ilm_last_index()
    class_fix_error.fix_error_ilm_not_hot_phase_index()
    class_fix_error.fix_error_ilm_not_last_index()
    class_fix_error.fix_error_ilm_shrink_index()

def start_check_mode_fix_error_ilm_all(check_mode):
  if check_mode:
    class_fix_error.fix_error_ilm_last_index_in_check_mode()
    class_fix_error.fix_error_ilm_not_hot_phase_index_in_check_mode()
    class_fix_error.fix_error_ilm_not_last_index_in_check_mode()
    class_fix_error.fix_error_ilm_shrink_index_in_check_mode()

@click.command(short_help='Starts fixing all ILM errors.')
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
  """Starts fixing all ILM errors"""

  logging_level(log_level)
  class_log.logger.info("Starts fixing all ILM errors")

  updating_variables(path_to_file)

  generating_variables_for_indices()
  generating_variables_for_fix_error()
  deleting_unnecessary_variables()

  start_fix_error_ilm_all(check_mode)
  start_check_mode_fix_error_ilm_all(check_mode)

if __name__ == "__main__":
  cli()
