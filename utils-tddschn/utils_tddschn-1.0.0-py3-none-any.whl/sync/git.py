#!/usr/bin/env python3

"""sync git utils"""

import subprocess
from subprocess import CompletedProcess
from os import PathLike


def git_root_dir() -> str:
    """Return the root directory of the current git repository."""
    # https://stackoverflow.com/questions/22081209/find-the-root-of-the-git-repository-where-the-file-lives
    return (
        subprocess.check_output(['git', 'rev-parse', '--show-toplevel'])
        .decode('utf-8')
        .strip()
    )


def git_get_all_remotes(cwd: PathLike | None = None) -> list[str]:
    program = ['git', 'remote']
    proc: CompletedProcess = subprocess.run(program, stdout=subprocess.PIPE, cwd=cwd)
    # logger.info(f'Getting all remotes of {cwd} .')
    # logger.info(f'Running: {program}')
    stdout = proc.stdout
    return stdout.decode().strip().splitlines()


def git_get_current_branch(cwd: PathLike | None = None) -> str:
    program = ['git', 'branch', '--show-current']
    proc: CompletedProcess = subprocess.run(program, stdout=subprocess.PIPE, cwd=cwd)
    stdout = proc.stdout
    return stdout.decode().strip()
