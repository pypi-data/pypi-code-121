# Author: Snow Yang
# Date  : 2022/03/28

"""Defines the public API of the package."""
import pathlib
import logging

import click

from typing import List, Any

from mdev.project.mxos_program import MxosProgram, parse_url
from mdev.project._internal.libraries import LibraryReferences
from mdev.project._internal import git_utils

logger = logging.getLogger(__name__)


def import_project(url: str, dst_path: Any = None, ref: str = '', recursive: bool = False) -> pathlib.Path:
    """Clones an Mxos project from a remote repository.

    Args:
        url: URL of the repository to clone.
        dst_path: Destination path for the repository.
        recursive: Recursively clone all project dependencies.

    Returns:
        The path the project was cloned to.
    """
    git_data = parse_url(url)
    url = git_data["url"]
    if not dst_path:
        dst_path = pathlib.Path(git_data["dst_path"])

    if dst_path.exists():
        click.echo(f"❌ Error: {str(dst_path)} already exists, please change a name or remove it from there.")
        exit(1)

    repo = git_utils.clone(url, dst_path)
    if ref:
        git_utils.fetch(repo, ref)
        git_utils.checkout(repo, "FETCH_HEAD")

    if recursive:
        libs = LibraryReferences(root=dst_path, ignore_paths=[])
        libs.fetch()

    return dst_path


def initialise_project(path: pathlib.Path, create_only: bool) -> None:
    """Create a new Mxos project, optionally fetching and adding mxos.

    Args:
        path: Path to the project folder. Created if it doesn't exist.
        create_only: Flag which suppreses fetching mxos. If the value is `False`, fetch mxos from the remote.
    """
    program = MxosProgram.from_new(path)
    if not create_only:
        libs = LibraryReferences(root=program.root, ignore_paths=[])
        libs.fetch()


def deploy_project(path: pathlib.Path, force: bool = False) -> None:
    """Deploy a specific revision of the current Mxos project.

    This function also resolves and syncs all library dependencies to the revision specified in the library reference
    files.

    Args:
        path: Path to the Mxos project.
        force: Force overwrite uncommitted changes. If False, the deploy will fail if there are uncommitted local
               changes.
    """
    libs = LibraryReferences(path, ignore_paths=[])
    libs.checkout(force=force)
    if list(libs.iter_unresolved()):
        logger.info("Unresolved libraries detected, downloading library source code.")
        libs.fetch()

def sync_project(path: pathlib.Path) -> None:
    """Sync a specific revision of the current Mxos project.

    This function also resolves and syncs all library dependencies to the revision specified in the library reference
    files.

    Args:
        path: Path to the Mxos project.
    """
    libs = LibraryReferences(path, ignore_paths=[])
    for lib in libs.iter_resolved():
        repo = git_utils.get_repo(lib.source_code_path)
        git_ref = lib.get_git_reference()

        current_ref = repo.head.object.hexsha
        if git_ref.ref != current_ref:
            click.echo(f'Sync {lib.reference_file.name} from {git_ref.ref} to {current_ref}')
            git_ref.ref = current_ref
            lib.reference_file.write_text(f'{git_ref.repo_url}/#{git_ref.ref}\n')

def get_known_libs(path: pathlib.Path) -> List:
    """List all resolved library dependencies.

    This function will not resolve dependencies. This will only generate a list of resolved dependencies.

    Args:
        path: Path to the Mxos project.

    Returns:
        A list of known dependencies.
    """
    libs = LibraryReferences(path, ignore_paths=[])
    return list(sorted(libs.iter_resolved()))
