import dataclasses
from typing import Dict, List, Optional

import semver
from halo import Halo
from typing_extensions import Literal

from suite_py.lib import logger
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.github_handler import GithubHandler, GitRelease, Repository

VersionPart = Literal["major", "minor", "patch", "release", "build"]
DEFAULT_VERSION = "0.1.0"


@dataclasses.dataclass
class VersionHandler:
    """
    Manages version-related stuff across different commands.
    """

    _repo: Repository
    _git: git.GitHandler
    _github: GithubHandler

    def select_new_version(
        self,
        current_version: str,
        allow_prerelease: bool = False,
        allow_custom_version: bool = False,
    ) -> str:
        """
        Asks the user for a new semantic version.

        Args:
            current_version: The current project version (for static bumping options)
            allow_prerelease: Whether to give the user the option customize prerelease and build.

        Returns:
            A tuple in the form (selected_part, selected_version).
        """
        bump_options = self.get_bump_options(
            current_version, allow_prerelease, allow_custom_version
        )
        selected_version = prompt_utils.ask_choices("Select version:", bump_options)

        if allow_prerelease and selected_version == "release":
            return self.prompt_prerelease_version(current_version)
        if allow_custom_version and selected_version == "custom":
            return self.prompt_custom_version()
        return selected_version

    def prompt_prerelease_version(self, current_version: str) -> str:
        """
        Asks the user to specify a release token to be used.
        """
        pre_token = prompt_utils.ask_choices(
            "Select prerelease token:", self.get_prerelease_token_options()
        )
        return semver.bump_prerelease(current_version, token=pre_token)

    def prompt_custom_version(self) -> str:
        """
        Asks the user to input a custom semantic version.
        """
        version = prompt_utils.ask_questions_input("Please type a semantic version:")
        while not self.is_valid_semver(version):
            version = prompt_utils.ask_questions_input(
                "Please type a semantic version:"
            )
        return version

    @staticmethod
    def is_valid_semver(version: str) -> bool:
        try:
            semver.VersionInfo.parse(version)
            return True
        except ValueError:
            logger.error(f"The string {version} is not a valid semantic version.")
            return False

    def get_bump_options(
        self, current_version: str, allow_prerelease: bool, allow_custom_version: bool
    ) -> List[Dict[str, str]]:
        """
        Returns a dict of bump alternatives from `current_version`.

        Args:
            current_version: The current project version.

        Returns:
            The mapping between the version part to be bumped and the resulting version.
        """
        options = [
            ("Patch", semver.bump_patch(current_version), None),
            ("Minor", semver.bump_minor(current_version), None),
            ("Major", semver.bump_major(current_version), None),
        ]
        if allow_prerelease:
            options.append(("Release", "release", "(rc, dev, pre...)"))
        if allow_custom_version:
            options.append(("Custom", "custom", "(input a semantic version)"))
        return [
            {"name": f"{name} {desc or value}", "value": value}
            for name, value, desc in options
        ]

    def get_prerelease_token_options(self) -> List[Dict[str, str]]:
        return [{"name": token, "value": token} for token in ["rc", "dev", "pre"]]

    def get_latest_version(self) -> str:
        """
        Retrieves the latest project version using GitHub.

        Returns:
            The latest project version.
        """
        tags = self._repo.get_tags()
        tag = git.get_last_tag_number(tags)
        latest_release = self.get_release(tag)
        current_version = latest_release.tag_name if latest_release else tag
        return current_version or ""

    def get_release(self, tag: str) -> Optional[GitRelease]:
        """
        Retrieves the latest release from GitHub.
        """
        with Halo(text="Loading...", spinner="dots", color="magenta"):
            latest_release = self._github.get_latest_release_if_exists(self._repo)
            if latest_release and latest_release.title == tag:
                return latest_release
        return None
