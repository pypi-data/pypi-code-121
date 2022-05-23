#!/usr/bin/env python3

"""async git utils"""

import asyncio
from asyncio.subprocess import Process
from os import PathLike


async def git_get_all_remotes(cwd: PathLike | None = None) -> list[str]:
    program = ['git', 'remote']
    proc: Process = await asyncio.create_subprocess_exec(
        *program, stdout=asyncio.subprocess.PIPE, cwd=cwd
    )
    # logger.info(f'Getting all remotes of {cwd} .')
    # logger.info(f'Running: {program}')
    stdout, _ = await proc.communicate()
    return stdout.decode().strip().splitlines()


async def git_get_current_branch(cwd: PathLike | None = None) -> str:
    program = ['git', 'branch', '--show-current']
    proc: Process = await asyncio.create_subprocess_exec(
        *program, stdout=asyncio.subprocess.PIPE, cwd=cwd
    )
    stdout, _ = await proc.communicate()
    return stdout.decode().strip()
