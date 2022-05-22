# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path
from typing import Coroutine
from typing import Iterable


async def async_run_command(command):
    """Run an async command and return stdout and stderr."""
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()

    return stdout, stderr


async def async_git_pull(repo_path=None, git_dir=None, work_tree=None):
    """`git pull` on a directory, or git directory and work tree for bare
    repos."""
    if repo_path:
        command = ['git', '-C', fr'"{repo_path}"', 'pull']
        command = ' '.join(command)
    else:
        command = [
            'git',
            f'--git-dir="{git_dir}"',
            f'--work-tree="{work_tree}"',
            'pull',
        ]
        command = ' '.join(command)

    stdout, stderr = await async_run_command(command)

    return stdout, stderr


async def async_git_push(repo_path=None, git_dir=None, work_tree=None):
    """`git push` on a directory, or git directory and work tree for bare
    repos."""
    if repo_path:
        command = ['git', '-C', fr'"{repo_path}"', 'push']
        command = ' '.join(command)
    else:
        command = [
            'git',
            f'--git-dir="{git_dir}"',
            f'--work-tree="{work_tree}"',
            'push',
        ]
        command = ' '.join(command)

    stdout, stderr = await async_run_command(command)

    return stdout, stderr


async def async_git_status(repo_path=None, git_dir=None, work_tree=None):
    """`git status` on a directory, or git directory and work tree for bare
    repos."""

    if repo_path:
        command = [
            'git',
            '-C',
            fr'"{ repo_path }"',
            'status',
            '--porcelain=2',
            '-b',
        ]
        command = " ".join(command)
    else:
        command = [
            'git',
            f'--git-dir="{git_dir}"',
            f'--work-tree="{work_tree}"',
            'status',
            '--porcelain=2',
            '-b',
        ]
        command = ' '.join(command)
    stdout, stderr = await async_run_command(command)

    return stdout, stderr


async def chain(repo_path=None, git_dir=None, work_tree=None, name=None):
    """Chain pull, status, and push (for bare repos)."""

    if type(repo_path) != str:

        git_dir = repo_path['git_dir']
        work_tree = repo_path['work_tree']
        name = repo_path.get('name', None)
        repo_path = None

    if name:
        pass
    elif repo_path:
        name = Path(repo_path).name
    else:
        name = Path(git_dir).name

    results = dict(name=name, pull={}, status={}, push={})

    if not repo_path:  # Bare Repos
        # Can't check ahead-behind, so...
        stdout, stderr = await async_git_push(repo_path, git_dir, work_tree)
        results['push']['stdout'], results['push']['stderr'] = stdout, stderr
    stdout, stderr = await async_git_pull(repo_path, git_dir, work_tree)
    results['pull']['stdout'], results['pull']['stderr'] = stdout, stderr
    stdout, stderr = await async_git_status(repo_path, git_dir, work_tree)
    results['status']['stdout'], results['status']['stderr'] = stdout, stderr

    return results


async def group(repos: Iterable[Coroutine]):
    """Main function, but async.
    Chain pulls and status checks to each repo/bare repo, then run them.
    """
    return await asyncio.gather(*repos)
