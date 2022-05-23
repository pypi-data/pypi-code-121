#!/usr/bin/python3

import sys
import click
from feii.main import class_structure, class_log, logging_level, updating_variables, generating_variables_for_indices, generating_variables_for_update_ilm_policy, deleting_unnecessary_variables
from feii.policy import Policy

class_policy = Policy()
class_policy.logger = class_log.logger

def start_update_ilm_policy(check_mode, index, alias, policy):
  if not check_mode:
    class_policy.update_ilm_policy(index, alias, policy)

def start_check_mode_update_ilm_policy(check_mode, index, alias, policy):
  if check_mode:
    class_policy.update_ilm_policy_check_mode(index, alias, policy)

@click.command(short_help='Updating the ilm Policy.')
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
@click.option(
  '-i', '--index',
  default='',
  expose_value=True,
  help='Set the index name'
)
@click.option(
  '-a', '--alias',
  default='',
  expose_value=True,
  help='Set the alias name'
)
@click.option(
  '-p', '--policy',
  default='',
  expose_value=True,
  help='Set the ilm policy name'
)
def cli(check_mode, log_level, path_to_file, index, alias, policy):
  """Updating the ilm Policy"""

  logging_level(log_level)
  class_log.logger.info("Started updating the ilm Policy")

  if not index and not alias or not policy:
    sys.exit(class_log.logger.error("You need to specify an index or alias, as well as a policy"))

  if index and alias:
    sys.exit(class_log.logger.error("You need to specify either an index or an alias"))

  updating_variables(path_to_file)

  generating_variables_for_indices()
  generating_variables_for_update_ilm_policy()
  deleting_unnecessary_variables()

  if index and policy or alias and policy:
    start_update_ilm_policy(check_mode, index, alias, policy)
    start_check_mode_update_ilm_policy(check_mode, index, alias, policy)

if __name__ == "__main__":
  cli()
