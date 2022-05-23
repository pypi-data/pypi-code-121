#!/usr/bin/env python3
#
# Copyright (c) 2022 Samuel J. McKelvie
#
# MIT License - See LICENSE file accompanying this package.
#

"""Command-line interface for secret_kv package"""


from typing import Optional, Sequence, List, Union, Dict, TextIO, cast, Tuple


import os
import sys
import argparse

from file_collection_hash import file_collection_hash, __version__

class CmdExitError(RuntimeError):
  exit_code: int

  def __init__(self, exit_code: int, msg: Optional[str]=None):
    if msg is None:
      msg = f"Command exited with return code {exit_code}"
    super().__init__(msg)
    self.exit_code = exit_code

class ArgparseExitError(CmdExitError):
  pass

class NoExitArgumentParser(argparse.ArgumentParser):
  def exit(self, status=0, message=None):
    if message:
      self._print_message(message, sys.stderr)
    raise ArgparseExitError(status, message)

def run_cmd(args: argparse.Namespace) -> int:
  if args.version:
    print(__version__)
    return 0

  base_dir: str = args.cwd
  ignore_owner: bool = not args.no_ignore_owner
  ignore_group: bool = not args.no_ignore_group
  ignore_modify_time: bool = not args.no_ignore_modify_time
  ignore_permissions: bool = args.ignore_permissions
  exclude: List[str] = args.exclude
  hash_cmd: Optional[str] = args.hash_cmd
  filenames: Optional[List[str]] = args.filename
  if len(filenames) == 0:
    filenames = None

  result = file_collection_hash(
      base_dir=base_dir,
      files=filenames,
      ignore_owner=ignore_owner,
      ignore_group=ignore_group,
      ignore_permissions=ignore_permissions,
      ignore_modify_time=ignore_modify_time,
      exclude=exclude,
      hash_cmd=hash_cmd)
  print(result)

  return 0

def run(argv: Optional[Sequence[str]]=None) -> int:
  """Run the file-collection-hash command-line tool with provided arguments

  Args:
      argv (Optional[Sequence[str]], optional):
          A list of commandline arguments (NOT including the program as argv[0]!),
          or None to use sys.argv[1:]. Defaults to None.

  Returns:
      int: The exit code that would be returned if this were run as a standalone command.
  """
  parser = argparse.ArgumentParser(description="Compute a stable hash of a directory or set of files.")

  parser.add_argument('--version', action='store_true', default=False,
                      help='Display version informattion.')
  parser.add_argument('--traceback', "--tb", action='store_true', default=False,
                      help='Display detailed exception information')
  parser.add_argument('-C', '--cwd', default='.',
                      help='Set the base directory. Default is ".".')
  parser.add_argument('--no-ignore-owner', action='store_true', default=False,
                      help='Include the file owner/UID in the hash.')
  parser.add_argument('--no-ignore-group', action='store_true', default=False,
                      help='Include the file group/GID in the hash.')
  parser.add_argument('--no-ignore-modify-time', action='store_true', default=False,
                      help='Include the file last modified time in the hash.')
  parser.add_argument('--ignore-permissions', action='store_true', default=False,
                      help='Do not include the file permission bits (e.g., executable flag) in the hash.')
  parser.add_argument('--exclude', action='append', default=[],
                      help='Exclude file patterns from hash. See "tar --exclude"')
  parser.add_argument('--hash-cmd', default='sha256sum',
                      help='Set the program used to compute the hash. Default is "sha256sum".')
  parser.add_argument('filename', default=[], nargs='*',
                      help='Explicitly list files/dirs relative to base directory to include.  Default is ".".')

  try:
    args = parser.parse_args(argv)
  except ArgparseExitError as ex:
    return ex.exit_code
  traceback: bool = args.traceback
  try:
    rc = run_cmd(args)
  except Exception as ex:
    if isinstance(ex, CmdExitError):
      rc = ex.exit_code
    else:
      rc = 1
    if rc != 0:
      if traceback:
        raise

      print(f"file-collection-hash: error: {ex}", file=sys.stderr)
  return rc

# allow running with "python3 -m", or as a standalone script
if __name__ == "__main__":
  sys.exit(run())
