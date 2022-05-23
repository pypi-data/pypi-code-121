#!/usr/bin/python3

import click
from feii.main import class_structure, class_log, logging_level, updating_variables
from feii.cluster import Cluster

class_cluster = Cluster()
class_cluster.logger = class_log.logger

def start_retry_failed():
    class_cluster.retry_failed()
    class_cluster.check_retry_failed()

@click.command(short_help='Starts retry failed indexes.')
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
def cli(log_level, path_to_file):
  """Starts retry failed indexes"""

  logging_level(log_level)
  class_log.logger.info("Starts retry failed indexes")

  updating_variables(path_to_file)

  start_retry_failed()

if __name__ == "__main__":
  cli()
