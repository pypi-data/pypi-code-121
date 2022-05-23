# -*- encoding: utf-8 -*-
import sys

from github import GithubException

from suite_py.commands.ask_review import AskReview
from suite_py.lib import logger
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.git_handler import GitHandler, get_commit_logs
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class OpenPR:
    def __init__(self, project, config, tokens):
        self._project = project
        self._config = config
        self._tokens = tokens
        self._youtrack = YoutrackHandler(config, tokens)
        self._git = GitHandler(project, config)
        self._branch_name = self._git.current_branch_name()
        self._github = GithubHandler(tokens)

    def run(self):
        if not self._git.remote_branch_exists(self._branch_name):
            logger.warning(f"No branch named {self._branch_name} found on GitHub")
            if prompt_utils.ask_confirm(
                "Do you want to commit all the files and push them?"
            ):
                self._git.add()
                self._git.commit("Initial commit")
                self._git.push(self._branch_name)
            else:
                logger.error("Please, run 'git push' manually")
                sys.exit(-1)

        pulls = self._github.get_pr_from_branch(self._project, self._branch_name)
        if pulls.totalCount:
            pr = pulls[0]
            logger.info(
                f"There is a pull request on GitHub for the branch {self._branch_name}"
            )

            if prompt_utils.ask_confirm(
                "Do you want to change the description of the pull request?"
            ):
                self._edit_pr(pr)
            sys.exit(0)

        youtrack_id = self._get_youtrack_id()

        self._create_pr(youtrack_id)

    def _get_youtrack_id(self):
        youtrack_id = self._youtrack.get_card_from_name(self._branch_name)
        if youtrack_id:
            return youtrack_id

        logger.warning(
            "Couldn't find a YouTrack issue in the branch name or the selected issue does not exist"
        )
        if prompt_utils.ask_confirm(
            "Do you want to link the pull request with an issue?"
        ):
            return self._ask_for_card_id()
        return None

    def _ask_for_card_id(self):
        card_id = prompt_utils.ask_questions_input("Enter card ID (ex: PRIMA-1234): ")
        if self._youtrack.validate_issue(card_id):
            return card_id
        logger.error("ID does not exist on YouTrack")
        return self._ask_for_card_id()

    def _create_pr(self, youtrack_id):
        if youtrack_id:
            logger.info(
                f"Creating pull request on the {self._project} project for the {self._branch_name} branch linked with the {youtrack_id} card"
            )
            link = self._youtrack.get_link(youtrack_id)
            title = (
                f"[{youtrack_id}]: {self._youtrack.get_issue(youtrack_id)['summary']}"
            )
        else:
            logger.warning(
                f"Creating pull request on the {self._project} project for the {self._branch_name} branch NOT linked to YouTrack card"
            )
            link = ""
            title = _ask_for_title()

        base_branch = self._ask_for_base_branch()
        body = self._ask_for_description("", base_branch=base_branch, link=link)

        is_draft = prompt_utils.ask_confirm(
            "Do you want to open the pull request as a draft?", default=False
        )

        try:
            pr = self._github.create_pr(
                self._project, self._branch_name, title, body, base_branch, is_draft
            )
            logger.info(f"Pull request with number {pr.number} created! {pr.html_url}")
        except GithubException as e:
            logger.error("Error during GitHub invocation: ")
            logger.error(e.data["errors"][0])
            sys.exit(-1)

        if youtrack_id:
            self._youtrack.comment(youtrack_id, f"PR {self._project} -> {pr.html_url}")
            logger.info(f"Added the pull request link in the card {youtrack_id}")

        if not is_draft and prompt_utils.ask_confirm(
            "Do you want to insert reviewers?"
        ):
            AskReview(self._project, self._config, self._tokens).run()

    def _edit_pr(self, pr):
        pr_body = self._ask_for_description(pr.body)
        pr.edit(body=pr_body)
        logger.info("Pull request modified")

    def _ask_for_base_branch(self):
        branch = prompt_utils.ask_questions_input(
            "Enter the base branch of the pull request: ", "master"
        )
        return branch

    def _ask_for_description(self, pr_body, **opts):
        link = opts.get("link")
        base_branch = opts.get("base_branch")
        if pr_body == "":
            if link:
                pr_body = link + "\n\n"
            try:
                with open("pull_request_template.md", "r", encoding="utf-8") as f:
                    pr_body = pr_body + f.read() + "\n"
            except Exception:
                pass
            if base_branch and self._config.user["use_commits_in_pr_body"]:
                commit_list = get_commit_logs(base_branch)
                commit_list.reverse()
                pr_body = pr_body + "\n---\n".join(commit_list)
                input(
                    "Enter the description of the pull request. Pressing enter will open the default editor"
                )
        description = prompt_utils.ask_questions_editor(
            question_text="Enter the description of the PR: ", default_text=pr_body
        )
        if description == "":
            logger.warning("The description of the pull request cannot be empty")
            return self._ask_for_description(pr_body)
        return description


def _ask_for_title():
    title = prompt_utils.ask_questions_input("Enter the title of the pull request: ")
    if title == "":
        logger.warning("The title of the pull request cannot be empty")
        return _ask_for_title()
    return title
