#!/usr/bin/python3

import click
from feii.main import class_structure, class_log, logging_level, updating_variables, generating_variables_for_indices, generating_variables_for_rollover, generating_variables_for_rollover_next_step, deleting_unnecessary_variables
from feii.rollover import Rollover

class_rollover = Rollover()
class_rollover.logger = class_log.logger

def start_rollover_last_index(check_mode):
  if not check_mode:
    class_rollover.rollover_last_index()

def start_check_mode_rollover_last_index(check_mode):
  if check_mode:
    class_rollover.rollover_last_index_in_check_mode()

@click.command(short_help='Rollover only the latest big indexes (not shrink).')
@click.option(
  '-c', '--check_mode',
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
  """Rollover only the latest big indexes (not shrink index)"""

  logging_level(log_level)
  class_log.logger.info("Started rollover only the latest big indexes (not shrink index).")

  updating_variables(path_to_file)

  generating_variables_for_indices()
  generating_variables_for_rollover()
  generating_variables_for_rollover_next_step()
  deleting_unnecessary_variables()

  start_rollover_last_index(check_mode)
  start_check_mode_rollover_last_index(check_mode)

if __name__ == "__main__":
  cli()
