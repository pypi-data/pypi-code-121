"""Service for performing git workflows."""
from typing import Optional

import inject
import structlog

from db_contrib_tool.clients.git_client import GitClient

LOGGER = structlog.get_logger(__name__)


class GitService:
    """A service for performing git workflows."""

    @inject.autoparams()
    def __init__(self, git_client: GitClient) -> None:
        """
        Initialize the service.

        :param git_client: Client for interacting with git.
        """
        self.git_client = git_client

    def get_merge_base_commit(self, mongo_version: str) -> Optional[str]:
        """
        Get the merge-base between origin/master and the given version.

        :param version: Mongo version to find mergebase of.
        :return: Commit hash of merge-base.
        """
        target_branch = f"origin/v{mongo_version}"
        result = self.git_client.merge_base("origin/master", target_branch)
        if result.return_code != 0:
            current_branch_result = self.git_client.rev_parse("HEAD", abbrev_ref=True)
            if current_branch_result.output == "master":
                LOGGER.warning(
                    "Git command failed.",
                    cmd="merge-base",
                    branch=target_branch,
                    error=result.error,
                )
                LOGGER.warning("Falling back to the latest starting from the current commit.")

                result = self.git_client.rev_parse("HEAD", verify=True)

        if result.return_code != 0:
            LOGGER.warning(
                "Could not find mergebase",
                error=result.error,
            )
            LOGGER.warning("Falling back to the latest.")
            return None

        commit_hash = result.output
        LOGGER.info("Found commit.", commit=commit_hash)
        return commit_hash

    def get_commit_from_tag(self, tag: str) -> Optional[str]:
        """
        Get the commit hash that git tag points to.

        :param tag: Git tag.
        :return: Commit hash.
        """
        result = self.git_client.rev_list(tag, 1)
        if result.return_code != 0:
            LOGGER.warning(
                "Git command failed.",
                cmd="rev-parse",
                error=result.error,
            )
            return None

        commit_hash = result.output
        LOGGER.info("Found commit.", commit=commit_hash)
        return commit_hash
