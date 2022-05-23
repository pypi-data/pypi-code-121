#!/usr/bin/python3

import os
import click

cmd_folder = os.path.join(os.path.dirname(__file__), 'commands')
rollover_folder = os.path.join(os.path.dirname(__file__), 'commands/rollover')
alias_folder = os.path.join(os.path.dirname(__file__), 'commands/alias')
error_folder = os.path.join(os.path.dirname(__file__), 'commands/error')
delete_folder = os.path.join(os.path.dirname(__file__), 'commands/delete')
update_folder = os.path.join(os.path.dirname(__file__), 'commands/update')
write_folder = os.path.join(os.path.dirname(__file__), 'commands/write')
policy_folder = os.path.join(os.path.dirname(__file__), 'commands/policy')

class AllCLI(click.MultiCommand):
  def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(cmd_folder):
      if filename.endswith('.py') and filename.startswith("cmd_"):
        rv.append(filename[4:-3])
    rv.sort()
    return rv

  def get_command(self, ctx, name):
    try:
      mod = __import__(f"feii.commands.cmd_{name}", None, None, ["cli"])
    except ImportError:
      return
    return mod.cli

class RolloverCLI(click.MultiCommand):
  def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(rollover_folder):
      if filename.endswith('.py') and filename.startswith("cmd_"):
        rv.append(filename[4:-3])
    rv.sort()
    return rv

  def get_command(self, ctx, name):
    try:
      mod = __import__(f"feii.commands.rollover.cmd_{name}", None, None, ["cli"])
    except ImportError:
      return
    return mod.cli

class AliasCLI(click.MultiCommand):
  def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(alias_folder):
      if filename.endswith('.py') and filename.startswith("cmd_"):
        rv.append(filename[4:-3])
    rv.sort()
    return rv

  def get_command(self, ctx, name):
    try:
      mod = __import__(f"feii.commands.alias.cmd_{name}", None, None, ["cli"])
    except ImportError:
      return
    return mod.cli

class ErrorCLI(click.MultiCommand):
  def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(error_folder):
      if filename.endswith('.py') and filename.startswith("cmd_"):
        rv.append(filename[4:-3])
    rv.sort()
    return rv

  def get_command(self, ctx, name):
    try:
      mod = __import__(f"feii.commands.error.cmd_{name}", None, None, ["cli"])
    except ImportError:
      return
    return mod.cli

class DeleteCLI(click.MultiCommand):
  def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(delete_folder):
      if filename.endswith('.py') and filename.startswith("cmd_"):
        rv.append(filename[4:-3])
    rv.sort()
    return rv

  def get_command(self, ctx, name):
    try:
      mod = __import__(f"feii.commands.delete.cmd_{name}", None, None, ["cli"])
    except ImportError:
      return
    return mod.cli

class UpdateCLI(click.MultiCommand):
  def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(update_folder):
      if filename.endswith('.py') and filename.startswith("cmd_"):
        rv.append(filename[4:-3])
    rv.sort()
    return rv

  def get_command(self, ctx, name):
    try:
      mod = __import__(f"feii.commands.update.cmd_{name}", None, None, ["cli"])
    except ImportError:
      return
    return mod.cli

class WriteCLI(click.MultiCommand):
  def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(write_folder):
      if filename.endswith('.py') and filename.startswith("cmd_"):
        rv.append(filename[4:-3])
    rv.sort()
    return rv

  def get_command(self, ctx, name):
    try:
      mod = __import__(f"feii.commands.write.cmd_{name}", None, None, ["cli"])
    except ImportError:
      return
    return mod.cli

class PolicyCLI(click.MultiCommand):
  def list_commands(self, ctx):
    rv = []
    for filename in os.listdir(policy_folder):
      if filename.endswith('.py') and filename.startswith("cmd_"):
        rv.append(filename[4:-3])
    rv.sort()
    return rv

  def get_command(self, ctx, name):
    try:
      mod = __import__(f"feii.commands.policy.cmd_{name}", None, None, ["cli"])
    except ImportError:
      return
    return mod.cli

@click.command(cls=AllCLI, epilog="Run 'feii COMMAND --help' for more information on a command.")
@click.version_option()
def cli():
  """
  \b
  Feii - utility for ilm indexes in Elasticsearch that allows you to:
    * fix errors in indexes
    * delete empty indexes
    * rollover big indexes
    * adding alias in indexes
    * applying parameters
    * fix write in indices
    * update policy
  """

if __name__ == '__main__':
  cli()
