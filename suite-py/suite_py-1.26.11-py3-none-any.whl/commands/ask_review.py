# -*- coding: utf-8 -*-
import functools
import readline
import sys

from suite_py.lib import logger
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class AskReview:
    def __init__(self, project, config, tokens):
        self._project = project
        self._config = config
        self._youtrack = YoutrackHandler(config, tokens)
        self._captainhook = CaptainHook(config)
        self._git = GitHandler(project, config)
        self._github = GithubHandler(tokens)

    def run(self):
        users = self._maybe_get_users_list()
        pr = self._get_pr()
        youtrack_reviewers = _ask_reviewer(users)
        github_reviewers = _find_github_nicks(youtrack_reviewers, users)
        pr.create_review_request(github_reviewers)
        logger.info("Adding reviewers on GitHub")
        self._maybe_adjust_youtrack_card(pr.title, youtrack_reviewers)

    def _maybe_get_users_list(self):
        try:
            users = self._captainhook.get_users_list().json()
            self._config.put_cache("users", users)
            return users
        except Exception:
            logger.warning(
                "Can't get users list from Captainhook. Using cached version."
            )
            return self._config.get_cache("users")

    def _get_pr(self):
        branch_name = self._git.current_branch_name()
        pull = self._github.get_pr_from_branch(self._project, branch_name)

        if pull.totalCount:
            pr = pull[0]
            logger.info(
                f"I found pull request number {pr.number} for branch {branch_name} on repo {self._project}"
            )
        else:
            logger.error(f"No open pull requests found for branch {branch_name}")
            sys.exit(-1)

        return pr

    def _maybe_adjust_youtrack_card(self, title, youtrack_reviewers):
        youtrack_id = self._youtrack.get_card_from_name(title)

        if youtrack_id:
            logger.info(
                f"Moving the {youtrack_id} card for review on youtrack and adding user tags"
            )
            self._youtrack.update_state(
                youtrack_id, self._config.youtrack["review_state"]
            )
            for rev in youtrack_reviewers:
                try:
                    self._youtrack.add_tag(youtrack_id, f"review:{rev}")
                except BaseException as e:
                    logger.warning(f"I was unable to add the review tags: {e}")
                    sys.exit(-1)
        else:
            logger.warning(
                "Reviewers added ONLY on GitHub. No linked card on YouTrack or missing card number in the branch name."
            )


def _ask_reviewer(users):
    u_completer = functools.partial(_completer, users)
    readline.set_completer(u_completer)
    readline.parse_and_bind("tab: complete")

    youtrack_reviewers = []

    youtrack_reviewers = list(
        input(
            "Choose the reviewers (name.surname - separated by space - press TAB for autocomplete) > "
        ).split()
    )

    if not youtrack_reviewers:
        logger.warning("You must enter at least one reviewer")
        return _ask_reviewer(users)

    return youtrack_reviewers


def _completer(users, text, state):
    options = [x["youtrack"] for x in users if text.lower() in x["youtrack"].lower()]
    try:
        return options[state]
    except IndexError:
        return None


def _find_github_nicks(youtrack_reviewers, users):
    github_reviewers = []
    for rev in youtrack_reviewers:
        for user in users:
            if user["youtrack"] == rev:
                github_reviewers.append(user["github"])

    return github_reviewers
