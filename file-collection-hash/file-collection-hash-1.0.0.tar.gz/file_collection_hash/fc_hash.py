# Copyright (c) 2022 Samuel J. McKelvie
#
# MIT License - See LICENSE file accompanying this package.
#

"""Function that computes a stable hash of a directory or set of files"""

from typing import Optional, Union, List

import subprocess
import sys

_DEBUG = False

def file_collection_hash(
        base_dir: Optional[str] = None,
        files: Optional[Union[str, List[str]]] = None,
        ignore_owner: bool=True,
        ignore_group: bool=True,
        ignore_permissions: bool=False,
        ignore_modify_time: bool=True,
        exclude: Optional[Union[str, List[str]]]=None,
        hash_cmd: str='sha256sum',
    ) -> str:
  """Computes a stable hash string from a directory or set of files.

  A directory that is an rsync -a duplicate of another directory will produce
  the same hash.

  Uses the tar utility to create a repeatable hashable stream from the set of files.
  This stream is then filtered through the designated hashing command (by default
  sha256sum). All the heavy lifting is done out-of process by optimized
  standard tools.

  Args:
      base_dir (Optional[str], optional):
                The directory from which all filenames are relative. If None, the current
                working directly is used. Defaults to None.
      files (Optional[Union[str, List[str]]], optional): 
                Optionally, a single file/directory name or a list of file/directory names relative
                to base_dir to include in the hash. If None, then '.' is used, which hashes the
                base dir (with fixed name '.') and all of its contents recursively. Defaults to None.
                Note that the names in this list are included in the hash, so changing the name
                of an item will change the hash.
      ignore_owner (bool, optional):
                If True, the posix owner/UID associated with each file is not hashed.
                Defaults to True.
      ignore_group (bool, optional):
                If True, the piosix Group/GID associated with each file is not hashed.
                Defaults to True.
      ignore_permissions (bool, optional):
               If True, the permission/mode bits associated with each file are not hashed.
               Defaults to False.
      ignore_modify_time (bool, optional):
               If True, the modification time associated with each file is not hashed.
               Defaults to True.
      exclude (Optional[Union[str, List[str]]], optional):
               An optional file pattern or list of file patterns for files to exclude from
               the hash. Pattern format is the same as for "tar --exclude=". Defaults to None.
      hash_cmd (str, optional): 
               The name of an exceutable program that will read from STDIN and write a textual
               hash to stdout. Any output from the first whitespace character is ignored.
               Defaults to 'sha256sum'.

  Raises:
      subprocess.CalledProcessError: tar or the hash_cmd failed.

  Returns:
      str: A hash string with no whitespace.
  """
  if files is None:
    files = []
  elif isinstance(files, str):
    files = [ files ]
  if len(files) == 0:
    files.append('.')
  cmd: List[str] = [ 'tar', '-cf', '-', '--sort=name' ]
  if not base_dir is None:
    cmd.extend([ '-C', base_dir ])
  if not exclude is None:
    if isinstance(exclude, str):
      exclude = [ exclude ]
    for pattern in exclude:
      cmd.append(f"--exclude={pattern}")
  if ignore_owner:
    cmd.append('--owner=root:0')
  if ignore_group:
    cmd.append('--group=root:0')
  if ignore_modify_time:
    cmd.append("--mtime=UTC 2001-01-01")
  if ignore_permissions:
    cmd.append("--mode=a+rwx")
  for filename in files:
    cmd.append(f"--add-file={filename}")
  
  if _DEBUG: print(f"cmd={cmd}", file=sys.stdout)

  with subprocess.Popen(cmd, stdout=subprocess.PIPE) as tar_proc:
    result = subprocess.check_output([ hash_cmd ], stdin=tar_proc.stdout).decode('utf-8').split(None, 1)[0]
    exit_code = tar_proc.wait()
    if exit_code != 0:
      raise subprocess.CalledProcessError(exit_code, cmd)
  return result

