#!/usr/bin/env python3

"""sync git utils"""

import subprocess


def git_root_dir() -> str:
    """Return the root directory of the current git repository."""
    # https://stackoverflow.com/questions/22081209/find-the-root-of-the-git-repository-where-the-file-lives
    return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'
                                    ]).decode('utf-8').strip()
