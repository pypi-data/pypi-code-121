# Author: Snow Yang
# Date  : 2022/03/28

"""Objects for library reference handling."""
import os
import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Generator, List

from mdev.project._internal import git_utils
from mdev.project.exceptions import VersionControlError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, order=True)
class MxosLibReference:
    """Metadata associated with an Mxos library.

    An Mxos library is an external dependency of an MxosProgram. The MxosProgram is made aware of the library
    dependency by the presence of a .component file in the project tree, which we refer to as a library reference file. The
    library reference file contains a URI where the dependency's source code can be fetched.

    Attributes:
        reference_file: Path to the .component reference file for this library.
        source_code_path: Path to the source code if it exists in the local project.
    """

    reference_file: Path
    source_code_path: Path

    def is_resolved(self) -> bool:
        """Determines if the source code for this library is present in the source tree."""
        return self.source_code_path.exists() and self.source_code_path.is_dir()

    def get_git_reference(self) -> git_utils.GitReference:
        """Get the source code location from the library reference file.

        Returns:
            Data structure containing the contents of the library reference file.
        """
        raw_ref = self.reference_file.read_text().strip()
        url, sep, ref = raw_ref.partition("#")

        if url.endswith("/"):
            url = url[:-1]

        return git_utils.GitReference(repo_url=url, ref=ref)


@dataclass
class LibraryReferences:
    """Manages library references in an MxosProgram."""

    root: Path
    ignore_paths: List[str]

    def fetch(self) -> None:
        """Recursively clone all dependencies defined in .component files."""
        for lib in self.iter_unresolved():
            git_ref = lib.get_git_reference()
            logger.info(f"Resolving library reference {git_ref.repo_url}.")
            _clone_at_ref(git_ref.repo_url, lib.source_code_path, git_ref.ref)
            self._ignore_component(lib.source_code_path)

        # Check if we find any new references after cloning dependencies.
        if list(self.iter_unresolved()):
            self.fetch()

    def checkout(self, force: bool) -> None:
        """Check out all resolved libs to revision specified in .component files."""
        for lib in self.iter_resolved():
            repo = git_utils.get_repo(lib.source_code_path)
            git_ref = lib.get_git_reference()

            if not git_ref.ref:
                git_ref.ref = git_utils.get_default_branch(repo)

            git_utils.fetch(repo, git_ref.ref)
            git_utils.checkout(repo, "FETCH_HEAD", force=force)
        
            if lib.reference_file.name == 'mxos.component':
                for submodule in repo.submodules:
                    if submodule.module_exists():
                        submodule.update(init=True)

    def iter_all(self) -> Generator[MxosLibReference, None, None]:
        """Iterate all library references in the tree.

        Yields:
            Iterator to library reference.
        """
        for lib in self.root.rglob("*.component"):
            if not self._in_ignore_path(lib):
                yield MxosLibReference(lib, lib.with_suffix(""))

    def iter_unresolved(self) -> Generator[MxosLibReference, None, None]:
        """Iterate all unresolved library references in the tree.

        Yields:
            Iterator to library reference.
        """
        for lib in self.iter_all():
            if not lib.is_resolved():
                yield lib

    def iter_resolved(self) -> Generator[MxosLibReference, None, None]:
        """Iterate all resolved library references in the tree.

        Yields:
            Iterator to library reference.
        """
        for lib in self.iter_all():
            if lib.is_resolved():
                yield lib

    def _in_ignore_path(self, lib_reference_path: Path) -> bool:
        """Check if a library reference is in a path we want to ignore."""
        return any(p in lib_reference_path.parts for p in self.ignore_paths)

    def _ignore_component(self, path: Path) -> Path:
        for parent in path.parents:
            if parent == self.root.parents[0]:
                break
            git_exclude = parent / '.git' / 'info' / 'exclude'
            if git_exclude.exists():
                content = git_exclude.read_text()
                relpath = str(path.relative_to(str(parent))).replace('\\', '/')
                if relpath not in content.splitlines():
                    git_exclude.write_text(f'{content}{relpath}\n')
                break


def _clone_at_ref(url: str, path: Path, ref: str) -> None:
    if ref:
        logger.info(f"Checking out revision {ref} for library {url}.")
        try:
            git_utils.clone(url, path, ref)
        except VersionControlError:
            # We weren't able to clone. Try again without the ref.
            # We couldn't clone the ref and had to fall back to cloning
            # just the default branch. Fetch the ref before checkout, so
            # that we have it available locally.
            logger.warning(f"Fetching {path} ...")
            repo = git_utils.clone(url, path)
            git_utils.fetch(repo, ref)
            git_utils.checkout(repo, "FETCH_HEAD")
    else:
        git_utils.clone(url, path)
