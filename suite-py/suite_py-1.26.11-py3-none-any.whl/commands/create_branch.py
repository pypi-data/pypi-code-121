# -*- coding: utf-8 -*-
import re
import sys

from suite_py.lib import logger
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class CreateBranch:
    def __init__(self, project, card, config, tokens):
        self._project = project
        self._card = card
        self._config = config
        self._youtrack = YoutrackHandler(config, tokens)
        self._git = GitHandler(project, config)

    def run(self):
        if not self._git.is_detached() and self._git.is_dirty():
            # Default behaviour is to pull when not detached.
            # Can't do that with uncommitted changes.
            logger.error("You have some uncommited changes, I can't continue")
            sys.exit(-1)

        try:
            if self._card:
                issue = self._youtrack.get_issue(self._card)
            else:
                issue = self._youtrack.get_issue(self._ask_card())
        except Exception:
            logger.error(
                "There was a problem retrieving the issue from YouTrack. Check that the issue number is correct"
            )
            sys.exit(-1)

        self._checkout_branch(issue)

        user = self._youtrack.get_current_user()
        self._youtrack.assign_to(issue["id"], user["login"])

        self._youtrack.update_state(issue["id"], self._config.youtrack["picked_state"])

    def _ask_card(self):
        return prompt_utils.ask_questions_input(
            "Insert the YouTrack issue number:",
            self._config.user["default_slug"],
        )

    def _checkout_branch(self, issue):
        branch_name = prompt_utils.ask_questions_input(
            "Enter branch name: ",
            re.sub(
                r'([\s\\.,~\^:\(\)\[\]\<\>"\'?\#]|[^\x00-\x7F]|[0-9])+',
                "-",
                issue["summary"],
            ).lower(),
        )

        default_parent_branch_name = self._config.user.get(
            "default_parent_branch", self._git.current_branch_name()
        )

        parent_branch_name = prompt_utils.ask_questions_input(
            "Insert initial branch: ", default_parent_branch_name
        )

        branch_type = issue["Type"].lower().replace(" ", "-")

        branch_name = f"{issue['idReadable']}/{branch_type}/{branch_name}"

        self._git.checkout(parent_branch_name)

        self._git.checkout(branch_name, new=True)
