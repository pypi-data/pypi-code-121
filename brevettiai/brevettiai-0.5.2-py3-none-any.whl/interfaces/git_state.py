"""
Interface to local git repositories for extracting current state of code in use
"""
import inspect
import os
from dataclasses import dataclass
from typing import Dict, Union, List

# Allow git to not be installed
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

import git


@dataclass(order=True)
class CommitState:
    """
    Json serializable information about commit and diff to current state
    """
    message: str
    author: str
    datetime: str
    sha: str
    diff: List[str]

    @classmethod
    def from_commit(cls, commit: git.Commit):
        return cls(
            message=commit.message,
            author=commit.author.name,
            datetime=str(commit.committed_datetime),
            sha=commit.hexsha,
            diff=[f"{x.change_type} {x.a_path}" for x in commit.diff(None)],
        )


@dataclass(order=True)
class GitRepositoryState:
    """
    Json serializable state of git repository
    """
    active_branch: str
    is_dirty: bool
    remote_url: str
    branches: Dict[str, Union[CommitState, str]]
    untracked_files: List[str]

    @classmethod
    def from_path(cls, path, search_parent_directories=True):
        """
        Extract git repository state from a path

        Args:
            path: path to search for git repositories
            search_parent_directories: Also search for git repos in parent directories

        Returns:

        """
        repo = git.Repo(path, search_parent_directories=search_parent_directories)
        remote = repo.remote()
        interest_points = (
            repo.active_branch.name,
            f"{remote.name}/{repo.active_branch.name}",
        )
        return cls(
            active_branch=repo.active_branch.name,
            is_dirty=repo.is_dirty(),
            remote_url=remote.url,
            branches={b: _git_safe_commit_state(repo, b) for b in interest_points},
            untracked_files=repo.untracked_files
        )

    @classmethod
    def from_type(cls, type_):
        """
        Extract git information from object type

        Args:
            type_:

        Returns:

        """
        path = os.path.dirname(inspect.getfile(type_))
        return cls.from_path(path)


def _git_safe_commit_state(repo, ref):
    try:
        return CommitState.from_commit(repo.commit(ref))
    except Exception as ex:
        return str(ex)
