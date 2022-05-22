# -*- coding: utf-8 -*-
import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple

import typer
import yaml
from blessed import Terminal
from cs_sync.github import chain
from cs_sync.github import group
from cs_sync.handlers import parse_repo
from cs_sync.helpers import expand_path
from cs_sync.helpers import flatten_list


term = Terminal()
cli = typer.Typer()


# Config
config_file = Path.home() / '.cssync'


def load_config() -> Tuple[List, List]:
    """Get configuration from config file.

    Returns repo_paths and bare_repo_dicts.
    """
    if config_file.exists():
        with open(config_file, "r") as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.Loader)
        repo_paths = flatten_list(
            [expand_path(i) for i in config.get('repo_paths', [])]
        )
        bare_repo_dicts: List[Dict] = config.get('bare_repos', [])
        bare_repo: Dict[str, str]
        for bare_repo in bare_repo_dicts:
            bare_repo['git_dir'] = expand_path(bare_repo['git_dir'])[0]
            bare_repo['work_tree'] = expand_path(bare_repo['work_tree'])[0]
    else:
        repo_paths = []
        bare_repo_dicts = []
    return repo_paths, bare_repo_dicts


def measure_time_async(original_async_function):
    async def wrapper(*args, **kwargs):

        # Work Before
        start = time.perf_counter()

        # Run Async Function
        results = await original_async_function(*args, **kwargs)

        # Work After
        elapsed = time.perf_counter() - start
        print(term.red(f"Executed in {elapsed:0.2f} seconds."))

        # Return results
        return results

    return wrapper


def measure_time(original_async_function):
    def wrapper(*args, **kwargs):

        # Work Before
        start = __import__('time').perf_counter()

        # Run Async Function
        results = original_async_function(*args, **kwargs)

        # Work After
        elapsed = __import__('time').perf_counter() - start
        print(term.red(f"Executed in {elapsed:0.2f} seconds."))

        # Return results
        return results

    return wrapper


async def chain_handler(async_def, handler, *args, **kwargs):
    results = await async_def
    await handler(results, *args, **kwargs)
    return results


@cli.command()
def all(short: bool = typer.Option(False, "--short")):
    """Git, AWS, System Settings (Windows Terminal), etc."""
    git(short=short)
    task()


@measure_time
@cli.command()
def git(short: bool = typer.Option(False, "--short")):
    """Status, Pull, etc. all git repos."""

    repo_paths, bare_repo_dicts = load_config()
    repo_paths = [
        i
        for i in repo_paths
        if Path(i).is_dir() and '.git' in [j.name for j in Path(i).glob('*')]
    ]

    repos = repo_paths + bare_repo_dicts
    chains = [chain_handler(chain(r), parse_repo, short) for r in repos]
    tasks = group(chains)
    if sys.version > '3.6':
        _ = asyncio.run(tasks)
    else:
        loop = asyncio.get_event_loop()
        _ = loop.run_until_complete(tasks)


@cli.command()
def task():
    """Sync Taskwarrior with Taskserver."""

    command = ['task', 'sync']
    if sys.platform == 'win32':
        command = ['wsl'] + command
    subprocess.run(command)


if __name__ == '__main__':
    cli()
