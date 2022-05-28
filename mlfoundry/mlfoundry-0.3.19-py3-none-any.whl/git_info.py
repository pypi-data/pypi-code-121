"""
This code may not be needed going forward in future.


mlflow.set_experiment("my_experiment")
with mlflow.start_run(run_name=str(time.time())) as run:
    mlflow.set_tag("foo", "bar")

The above snippet adds commit sha in
mlflow.source.git.commit tag
https://www.mlflow.org/docs/latest/tracking.html#system-tags

This does not work if we use MlflowClient directly.
"""


import logging
import typing

from git.exc import InvalidGitRepositoryError

logger = logging.getLogger(__name__)


class GitInfo:
    def __init__(self, path: str):
        try:
            self.repo = self.build_repo(path)
        except InvalidGitRepositoryError as ex:
            # NOTE: gitpython library does not set proper exception message while raising the
            # exception. So we are catching and raising the same exception with proper message
            raise InvalidGitRepositoryError("git repository is not present") from ex

    def build_repo(self, path: str):
        # https://github.com/gitpython-developers/GitPython/blob/cd29f07b2efda24bdc690626ed557590289d11a6/git/cmd.py#L365
        # looks like the import itself may fail in case the git executable
        # is not found
        # putting the import here so that the caller can handle the exception
        import git

        repo = git.Repo(path, search_parent_directories=True)

        return repo

    @property
    def current_commit_sha(self) -> str:
        return self.repo.head.object.hexsha

    @property
    def current_branch_name(self) -> str:
        try:
            branch_name = self.repo.active_branch.name
            return branch_name
        except TypeError as ex:
            # NOTE: TypeError will be raised here if
            # head is in detached state.
            # git checkout commit_sha
            # in this case returning empty string
            logger.warning(f"cannot get branch name because of {ex}")
            return ""

    @property
    def remote_url(self) -> typing.Optional[str]:
        remotes = self.repo.remotes
        if len(remotes) != 1:
            logger.warning("either more than one or no remote detected")
            return None
        return remotes[0].url

    @property
    def diff_patch(self) -> str:
        return self.repo.git.diff("--patch", "HEAD")

    @property
    def is_dirty(self) -> bool:
        return self.repo.is_dirty()
