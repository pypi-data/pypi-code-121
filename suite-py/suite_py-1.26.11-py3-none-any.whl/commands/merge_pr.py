# -*- coding: utf-8 -*-
import sys

from halo import Halo

from suite_py.lib import logger
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.drone_handler import DroneHandler
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.qainit_handler import QainitHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler
from suite_py.lib.symbol import CHECKMARK, CROSSMARK
from suite_py.commands.login import Login


class MergePR:
    def __init__(self, project, config, tokens):
        self._project = project
        self._config = config
        self._youtrack = YoutrackHandler(config, tokens)
        self._captainhook = CaptainHook(config)
        self._git = GitHandler(project, config)
        self._github = GithubHandler(tokens)
        self._drone = DroneHandler(config, tokens, repo=project)
        self._qainit = QainitHandler(project, config, tokens)

    def run(self):
        # pylint: disable=too-many-branches
        self._stop_if_master_locked()

        pr = self._select_pr()

        print(f"\nYou have selected: \n{self._check_pr_status(pr)}")
        if not prompt_utils.ask_confirm(
            "Do you want to continue the merge?", default=False
        ):
            sys.exit()

        branch_name = pr.head.ref
        youtrack_id = self._youtrack.get_card_from_name(branch_name)

        _check_migrations_merge(pr)

        logger.info("Merging...")

        merge_status = pr.merge(
            commit_title=f"{pr.title} (#{pr.number})",
            commit_message="",
            merge_method="squash",
        )

        if not merge_status.merged:
            logger.error("An error occurred during the merge.")
            sys.exit(-1)

        drone_build_number = self._drone.get_pr_build_number(merge_status.sha)
        drone_build_url = self._drone.get_build_url(drone_build_number)

        if drone_build_url:
            logger.info(
                f"Pull request merged on master! You can follow the build status at {drone_build_url}"
            )
        else:
            logger.info("Pull request merged on master!")

        self._git.fetch()
        if self._git.remote_branch_exists(branch_name):
            self._git.delete_remote_branch(branch_name)

        if prompt_utils.ask_confirm(
            "Do you want to lock staging? (If you need to test on staging)",
            default=False,
        ):
            self._captainhook.lock_project(self._project, "staging")

        if youtrack_id:
            logger.info("Updating card status on YouTrack...")
            self._youtrack.update_state(
                youtrack_id, self._config.youtrack["merged_state"]
            )
            logger.info("Card updated")

            if (
                not self._qainit.user_info()
                and self._config.user["delete_qa_after_merge"]
            ):
                logger.warning("You're not logged in.")
                Login(self._config).run()

            if self._config.user["delete_qa_after_merge"]:
                with Halo(
                    text="Searching for related QA environments...",
                    spinner="dots",
                    color="magenta",
                ):

                    response = self._qainit.list(
                        {
                            "user": "all",
                            "card": youtrack_id,
                            "status": ["created", "updated", "failed", "frozen"],
                        }
                    ).json()

                for qa in response["list"]:
                    logger.info(f"Found {qa['name']}")

                if len(response["list"]) > 0 and prompt_utils.ask_confirm(
                    "Do you want to delete the QA env(s) I found?",
                    default=True,
                ):
                    for qa in response["list"]:
                        logger.info(f"Deleting {qa['name']} ")
                        self._qainit.delete(qa["hash"])

        else:
            logger.warning(
                "There is no YouTrack issue in the branch name or the selected issue does not exist."
            )
            logger.warning(
                "No card updated on YouTrack and no QA turned off automatically"
            )

        logger.info("All done!")
        sys.exit()

    def _select_pr(self):
        if self._github.user_is_admin(self._project):
            logger.warning(
                "You are admin of the repository, you can merge it skipping the checks (CI, review, etc ...)\nWith great power comes great responsibility"
            )

        with Halo(text="Loading pull requests...", spinner="dots", color="magenta"):
            choices = [
                {"name": pr.title, "value": pr}
                for pr in self._github.get_list_pr(self._project)
            ]
        if choices:
            choices.sort(key=lambda x: x["name"])
            return prompt_utils.ask_choices("Select PR: ", choices)

        logger.error(
            f"There are no pull requests ready to be merged or you may not have the permissions, please check on https://github.com/primait/{self._project}/pulls"
        )
        sys.exit(-1)

    def _stop_if_master_locked(self):
        request = self._captainhook.status(self._project, "staging")

        if request.status_code != 200:
            logger.error("Unable to determine lock status on master.")
            sys.exit(-1)

        request_object = request.json()
        if request_object["locked"]:
            logger.error(
                f"The project is locked on staging by {request_object ['by']}. Unable to continue."
            )
            sys.exit(-1)

    def _check_pr_status(self, pr):
        build_status = CHECKMARK
        reviews = CHECKMARK
        print(pr.mergeable_state)
        if pr.mergeable_state == "dirty":
            logger.error(
                "The selected pull request is not mergeable. Check for conflicts."
            )
            sys.exit(-1)
        if pr.mergeable_state == "blocked":
            build_status = self._pr_build_status(pr)
            reviews = _pr_reviews(pr)

        return f"#{pr.number} {pr.title}\n     build: {build_status} - reviews: {reviews}\n"

    def _pr_build_status(self, pr):
        if self._github.get_build_status(self._project, pr.head.sha).state == "success":
            return CHECKMARK
        return CROSSMARK


def _check_migrations_merge(pr):
    files_changed = [x.filename for x in pr.get_files()]
    if git.migrations_found(files_changed):
        logger.warning("WARNING: migrations detected in the code")
        if not prompt_utils.ask_confirm("Are you sure you want to continue?"):
            sys.exit()


def _pr_reviews(pr):
    reviews = [r for r in pr.get_reviews() if r.state == "APPROVED"]
    if reviews:
        return CHECKMARK
    return CROSSMARK
