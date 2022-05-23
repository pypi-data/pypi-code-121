# -*- coding: utf-8 -*-
import re
import sys

from suite_py.commands.release import _parse_available_countries
from suite_py.lib import logger
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.drone_handler import DroneHandler
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.version_handler import DEFAULT_VERSION, VersionHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class Deploy:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, project, config, tokens):
        self._project = project
        self._config = config
        self._youtrack = YoutrackHandler(config, tokens)
        self._captainhook = CaptainHook(config)
        self._github = GithubHandler(tokens)
        self._repo = self._github.get_repo(project)
        self._git = GitHandler(project, config)
        self._drone = DroneHandler(config, tokens, repo=project)
        self._countries = _parse_available_countries(self._drone)
        self._version = VersionHandler(self._repo, self._git, self._github)

    def run(self):
        self._stop_if_prod_locked()

        self._git.fetch()

        if len(self._countries) > 0:
            logger.error(
                "Deploy command cannot be used on this project. Try to run `suite-py release` instead."
            )
            sys.exit(1)

        current_version = self._version.get_latest_version()

        if current_version != "":
            logger.info(f"The current release is {current_version}")
            commits = self._github.get_commits_since_release(
                self._repo, current_version
            )

            _check_migrations_deploy(commits)

            message = "\n".join(
                ["* " + c.commit.message.splitlines()[0] for c in commits]
            )

            logger.info(f"\nCommits list:\n{message}\n")

            if not prompt_utils.ask_confirm("Do you want to continue?"):
                sys.exit()

            new_version = self._version.select_new_version(current_version)

        else:
            # Se non viene trovata la release e non ci sono tag, viene saltato il check delle migrations e l'update delle card su youtrack
            logger.warning(
                f"No tags found, I'm about to push the tag {DEFAULT_VERSION}"
            )
            if not prompt_utils.ask_confirm(
                "Are you sure you want to continue?", default=False
            ):
                sys.exit()
            new_version = DEFAULT_VERSION
            message = f"First release with tag {new_version}"

        self._create_release(new_version, message)
        self._manage_youtrack_card(commits, new_version)

    def _stop_if_prod_locked(self):
        request = self._captainhook.status(self._project, "production")
        if request.status_code != 200:
            logger.error("Unable to determine lock status on master.")
            sys.exit(-1)

        request_object = request.json()
        if request_object["locked"]:
            logger.error(
                f"The project is locked in production by {request_object['by']}. Unable to continue."
            )
            sys.exit(-1)

    def _create_release(self, new_version, message):
        new_release = self._repo.create_git_release(
            new_version,
            new_version,
            self._youtrack.replace_card_names_with_md_links(message),
        )
        if new_release:
            logger.info(f"The release has been created! Link: {new_release.html_url}")

            build_number = self._drone.get_build_number_from_tag(new_version)
            if build_number:
                drone_url = self._drone.get_build_url(build_number)
                logger.info(
                    f"You can follow the deployment in production here: {drone_url}"
                )

    def _manage_youtrack_card(self, commits, new_version):
        release_state = self._config.youtrack["release_state"]

        issue_ids = self._youtrack.get_issue_ids(commits)

        if len(issue_ids) > 0:
            update_youtrack_state = prompt_utils.ask_confirm(
                f"Do you want to move the associated cards to {release_state} state?",
                default=False,
            )

            for issue_id in issue_ids:
                try:
                    self._youtrack.comment(
                        issue_id,
                        f"Deploy in production of {self._project} done with the release {new_version}",
                    )
                    if update_youtrack_state:
                        self._youtrack.update_state(issue_id, release_state)
                        logger.info(f"{issue_id} moved to {release_state}")
                except Exception:
                    logger.warning(
                        f"An error occurred while moving the card {issue_id} to {release_state}"
                    )
                repos_status = self._get_repos_status_from_issue(issue_id)
                if all(r["deployed"] for r in repos_status.values()):
                    try:
                        self._youtrack.update_deployed_field(issue_id)
                        logger.info("Custom field Deployed updated on YouTrack")
                    except Exception:
                        logger.warning(
                            "An error occurred while updating the custom field Deployed"
                        )

    def _get_repos_status_from_issue(self, issue_id):
        regex_pr = r"^PR .* -> https:\/\/github\.com\/primait\/(.*)\/pull\/([0-9]*)$"
        regex_deploy = r"^Deploy in production of (.*) done with the release"
        comments = self._youtrack.get_comments(issue_id)
        repos_status = {}

        for c in comments:
            m = re.match(regex_pr, c["text"])
            if m:
                project = m.group(1)
                pr_number = int(m.group(2))
                repos_status[project] = {}
                repos_status[project]["pr"] = pr_number
                repos_status[project]["deployed"] = False
            m = re.match(regex_deploy, c["text"])
            if m:
                project = m.group(1)
                try:
                    repos_status[project]["deployed"] = True
                except Exception:
                    pass
        return repos_status


def _check_migrations_deploy(commits):
    if not commits:
        logger.error("ERROR: no commit found")
        sys.exit(-1)
    elif len(commits) == 1:
        files_changed = git.files_changed_between_commits("--raw", f"{commits[0].sha}~")
    else:
        files_changed = git.files_changed_between_commits(
            f"{commits[-1].sha}~", commits[0].sha
        )
    if git.migrations_found(files_changed):
        logger.warning("WARNING: migrations detected in the code")
        if not prompt_utils.ask_confirm(
            "Are you sure you want to continue?", default=False
        ):
            sys.exit()
