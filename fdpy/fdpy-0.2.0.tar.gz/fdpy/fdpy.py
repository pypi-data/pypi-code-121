import os
import shlex
import subprocess
from pathlib import Path
from typing import Type, Dict, Union

from .helper import check_path
from .help_menu import LongHelp, ShortHelp


class FD():
    """
    The main class in the module.

    Attributes
    ----------
    fd : str
        the full path to `fd` binary file

    Methods
    -------
    h():
        Prints a short and concise overview of help.
    help():
        Prints help with all details.
    find(pattern, path=Path.cwd(), **kwargs):
        Main method of the FD class.
    version():
        Prints `fd` version (for the current package's version, use `fdpy.__version__`)

    """
    def __init__(self) -> None:
        self.fd = check_path()

    @staticmethod
    def h() -> str:
        """Prints a short and concise overview of help."""
        return ShortHelp().__doc__

    @staticmethod
    def help() -> str:
        """Prints help with all details."""
        return LongHelp().__doc__

    def _run(self, cmd) -> subprocess.CompletedProcess:
        return subprocess.run(shlex.split(cmd),
                              shell=False,
                              check=True,
                              capture_output=True,
                              text=True)

    def find(self, pattern, path=Path.cwd(),
             **kwargs) -> Union[list, str, None]:
        """
        ARGS:
            pattern           the search pattern (a regular expression, unless 'glob=True' is used)
            path (optional)   the root directory for the filesystem search

        KWARGS:
            hidden            Search hidden files and directories
            no_ignore         Do not respect .(git|fd)ignore files
            case_sensitive    Case_sensitive search (default: smart case)
            ignore_case       Case_insensitive search (default: smart case)
            glob              Glob_based search (default: regular expression)
            absolute_path     Show absolute instead of relative paths
            list_details      Use a long listing format with file metadata
            follow            Follow symbolic links
            full_path         Search full path (default: file_/dirname only)
            print0            Separate results by the null character

        OPTIONS:
            max_depth <depth>            Set maximum search depth (default: none)
            type <filetype>...
                    Filter by type: file (f), directory (d), symlink (l),
                    executable (x), empty (e), socket (s), pipe (p)
            extension <ext>...           Filter by file extension
            exec <cmd>                   Execute a command for each search result
            exec_batch <cmd>
                    Execute a command with all search results at once

            exclude <pattern>...
                    Exclude entries that match the given glob pattern

            size <size>...               Limit results based on the size of files.
                changed_within <date|dur>
                    Filter by file modification time (newer than)

                changed_before <date|dur>
                    Filter by file modification time (older than)

            owner <user:group>           Filter by owning user and/or group

        Note: `fd.h()` prints a short and concise overview while `fd.help()` gives all details.
        """
        args = ' '.join(
            [f'--{k}'.replace('_', '-') for k, v in kwargs.items() if v])
        str_default = ['print0', 'list_details']
        p = self._run(f'{self.fd} {args} {pattern} {path}')
        res = p.stdout.rstrip()
        if not any(kwargs.get(arg) for arg in str_default):
            res = [x for x in p.stdout.split('\n') if x]
        elif not res:
            return
        return res

    def version(self) -> str:
        """Prints `fd` version (for the current package's version, use `fdpy.__version__`)"""
        p = self._run(f'{self.fd} --version')
        return p.stdout.rstrip().split(' ')[1]
