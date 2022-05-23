#! -*- encoding: utf-8 -*-
import subprocess
import logging
import os
import sys
from typing import Optional

import click
from autoupgrade import Package

from suite_py.__version__ import __version__
from suite_py.commands.aggregator import Aggregator
from suite_py.commands.ask_review import AskReview
from suite_py.commands.bump import Bump
from suite_py.commands.check import Check
from suite_py.commands.create_branch import CreateBranch
from suite_py.commands.deploy import Deploy
from suite_py.commands.generator import Generator
from suite_py.commands.id import ID
from suite_py.commands.ip import IP
from suite_py.commands.login import Login
from suite_py.commands.merge_pr import MergePR
from suite_py.commands.open_pr import OpenPR
from suite_py.commands.project_lock import ProjectLock
from suite_py.commands.qa import QA
from suite_py.commands.release import Release
from suite_py.commands.secret import Secret
from suite_py.commands.status import Status
from suite_py.lib import logger
from suite_py.lib.config import Config
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.tokens import Tokens

ALLOW_NO_GIT_SUBCOMMAND = ["login", "qa", "aggregator"]
ALLOW_NO_HOME_SUBCOMMAND = ["login", "qa", "aggregator"]


def upgrade_suite_py_if_needed(break_on_missing_package: bool = False) -> None:
    """
    Sometimes, when `suite-py` is launched with a virtual environment active, autoupgrade
    cannot see the package as installed (as the command is used from the "global" user environment)
    and raises an exception.
    """
    try:
        # This checks that suite-py is available in the current environment
        subprocess.run(["pip3", "show", "suite-py"], check=True, capture_output=True)
        # If available, upgrade (if needed)
        Package("suite_py").upgrade()
    except Exception as error:
        logger.warning(
            "Skipping Suite-Py autoupgrade because the package was not found in the current environment."
        )
        if break_on_missing_package:
            raise error


@click.group()
@click.option(
    "--project",
    type=click.Path(exists=True),
    default=os.getcwd(),
    help="Path of the project to run the command on (the default is current directory)",
)
@click.option(
    "--timeout",
    type=click.INT,
    help="Timeout in seconds for Captainhook operations",
)
@click.option("-v", "--verbose", count=True)
@click.pass_context
def main(ctx, project, timeout, verbose):
    upgrade_suite_py_if_needed(break_on_missing_package=False)
    print(f"v{__version__}")

    config = Config()

    if ctx.invoked_subcommand not in ALLOW_NO_GIT_SUBCOMMAND and not git.is_repo(
        project
    ):
        print(f"the folder {project} is not a git repo")
        sys.exit(-1)

    if ctx.invoked_subcommand not in ALLOW_NO_HOME_SUBCOMMAND and not os.path.basename(
        project
    ) in os.listdir(config.user["projects_home"]):
        print(f"the folder {project} is not in {config.user['projects_home']}")
        sys.exit(-1)

    skip_confirmation = False
    if type(config.user.get("skip_confirmation")).__name__ == "bool":
        skip_confirmation = config.user.get("skip_confirmation")
    elif type(
        config.user.get("skip_confirmation")
    ).__name__ == "list" and ctx.invoked_subcommand in config.user.get(
        "skip_confirmation"
    ):
        skip_confirmation = True

    if not skip_confirmation and not prompt_utils.ask_confirm(
        f"Do you want to continue on project {os.path.basename(project)}?"
    ):
        sys.exit()

    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Logging as 'DEBUG'")

    ctx.ensure_object(dict)
    ctx.obj["project"] = os.path.basename(project)
    if timeout:
        config.user["captainhook_timeout"] = timeout
    ctx.obj["config"] = config
    ctx.obj["tokens"] = Tokens()

    # Skip chdir if not needed
    if (
        ctx.invoked_subcommand not in ALLOW_NO_GIT_SUBCOMMAND
        or ctx.invoked_subcommand not in ALLOW_NO_HOME_SUBCOMMAND
    ):
        os.chdir(os.path.join(config.user["projects_home"], ctx.obj["project"]))


@main.command("bump", help="Bumps the project version based on the .versions.yml file")
@click.option("--project", required=False, type=str)
@click.pass_obj
def bump(obj, project: Optional[str] = None):
    Bump(obj["project"], obj["config"], obj["tokens"]).run(project=project)


@main.command(
    "create-branch", help="Create local branch and set the YouTrack card in progress"
)
@click.option("--card", type=click.STRING, help="YouTrack card number (ex. PRIMA-123)")
@click.pass_obj
def cli_create_branch(obj, card):
    CreateBranch(obj["project"], card, obj["config"], obj["tokens"]).run()


@main.command("lock", help="Lock project on staging or prod")
@click.argument(
    "environment", type=click.Choice(("staging", "production", "deploy", "merge"))
)
@click.pass_obj
def cli_lock_project(obj, environment):
    ProjectLock(obj["project"], environment, "lock", obj["config"]).run()


@main.command("unlock", help="Unlock project on staging or prod")
@click.argument(
    "environment", type=click.Choice(("staging", "production", "deploy", "merge"))
)
@click.pass_obj
def cli_unlock_project(obj, environment):
    ProjectLock(obj["project"], environment, "unlock", obj["config"]).run()


@main.command("open-pr", help="Open a PR on GitHub")
@click.pass_obj
def cli_open_pr(obj):
    OpenPR(obj["project"], obj["config"], obj["tokens"]).run()


@main.command("ask-review", help="Requests a PR review")
@click.pass_obj
def cli_ask_review(obj):
    AskReview(obj["project"], obj["config"], obj["tokens"]).run()


@main.command(
    "merge-pr", help="Merge the selected branch to master if all checks are OK"
)
@click.pass_obj
def cli_merge_pr(obj):
    MergePR(obj["project"], obj["config"], obj["tokens"]).run()


@main.group("release", help="Manage releases")
def release():
    pass


@release.command("create", help="Create a github release")
@click.option("--deploy", is_flag=True, help="Trigger deploy after release creation")
@click.pass_obj
def cli_release_create(obj, deploy):
    Release(
        "create", obj["project"], obj["config"], obj["tokens"], flags={"deploy": deploy}
    ).run()


@release.command("deploy", help="Deploy a github release")
@click.pass_obj
def cli_release_deploy(obj):
    Release("deploy", obj["project"], obj["config"], obj["tokens"]).run()


@release.command("rollback", help="Rollback a deployment")
@click.pass_obj
def cli_release_rollback(obj):
    Release("rollback", obj["project"], obj["config"], obj["tokens"]).run()


@main.command("deploy", help="Deploy master branch in production")
@click.pass_obj
def cli_deploy(obj):
    Deploy(obj["project"], obj["config"], obj["tokens"]).run()


@main.command("status", help="Current status of a project")
@click.pass_obj
def cli_status(obj):
    Status(obj["project"], obj["config"]).run()


@main.command("check", help="Verify authorisations for third party services")
@click.pass_obj
def cli_check(obj):
    Check(obj["config"], obj["tokens"]).run()


@main.command("id", help="Get the ID of the hosts where the task is running")
@click.argument("environment", type=click.Choice(("staging", "production")))
@click.pass_obj
def cli_id(obj, environment):
    ID(obj["project"], obj["config"], environment).run()


@main.command("ip", help="Get the IP addresses of the hosts where the task is running")
@click.argument("environment", type=click.Choice(("staging", "production")))
@click.pass_obj
def cli_ip(obj, environment):
    IP(obj["project"], obj["config"], environment).run()


@main.command("generator", help="Generate different files from templates")
@click.pass_obj
def cli_generator(obj):
    Generator(obj["project"], obj["config"], obj["tokens"]).run()


@main.group(
    "aggregator",
    help="Manage CNAMEs of aggregators in QA envs",
    invoke_without_command=True,
)
@click.option(
    "-l", "--list", "show_list", help="deprecated", required=False, count=True
)
@click.option("-c", "--change", "change", help="deprecated", required=False, count=True)
@click.pass_context
def aggregator(ctx, show_list, change):
    if show_list == 1 or change == 1:
        logger.error(
            "suite-py aggregator [-c|-l] has been hard-deprecated. Use suite-py aggregator [list|change] instead."
        )
        sys.exit(0)

    if ctx.invoked_subcommand is None:
        logger.error("Missing command. Try suite-py aggregator --help for help.")
        sys.exit(0)


@aggregator.command("list", help="List all aggregators with the current record")
@click.pass_obj
def cli_aggregator_list(obj):
    Aggregator(obj["config"], "list").run()


@aggregator.command("change", help="Change aggregator record")
@click.pass_obj
def cli_aggregator_change(obj):
    Aggregator(obj["config"], "change").run()


@main.command("login", help="manage login against Auth0")
@click.pass_obj
def login(obj):
    Login(obj["config"]).run()


@main.group("qa", help="Manage QA envs")
def qa():
    pass


@qa.command("update-quota", help="Update quota in QA for a user")
@click.pass_obj
def cli_qa_update_quota(obj):
    QA("update-quota", obj["project"], obj["config"], obj["tokens"]).run()


@qa.command("list", help="List QA envs for user: all to show qa of all users.")
@click.option("-u", "--user", "user", required=False)
@click.option("-s", "--status", "status", multiple=True, type=str)
@click.option("-c", "--card", "card", type=str)
@click.pass_obj
def cli_qa_list(obj, user, status, card):
    QA(
        "list",
        obj["project"],
        obj["config"],
        obj["tokens"],
        {"user": user, "status": status, "card": card},
    ).run()


@qa.command("create", help="Create QA env")
@click.argument("microservices", nargs=-1, required=True)
@click.pass_obj
def cli_qa_create(obj, microservices):
    QA(
        "create",
        obj["project"],
        obj["config"],
        obj["tokens"],
        {"services": microservices},
    ).run()


@qa.command("update", help="Update QA env")
@click.argument("qa_hash", required=True)
@click.argument("microservices", nargs=-1, required=True)
@click.pass_obj
def cli_qa_update(obj, qa_hash, microservices):
    QA(
        "update",
        obj["project"],
        obj["config"],
        obj["tokens"],
        {"hash": qa_hash, "services": microservices},
    ).run()


@qa.command("delete", help="Delete QA env")
@click.argument("qa_hashes", nargs=-1, required=True)
@click.pass_obj
def cli_qa_delete(obj, qa_hashes):
    QA(
        "delete", obj["project"], obj["config"], obj["tokens"], {"hashes": qa_hashes}
    ).run()


@qa.command("freeze", help="Freeze QA env")
@click.argument("qa_hash", required=True)
@click.pass_obj
def cli_qa_freeze(obj, qa_hash):
    QA("freeze", obj["project"], obj["config"], obj["tokens"], {"hash": qa_hash}).run()


@qa.command("unfreeze", help="Unfreeze QA env")
@click.argument("qa_hash", required=True)
@click.pass_obj
def cli_qa_unfreeze(obj, qa_hash):
    QA(
        "unfreeze", obj["project"], obj["config"], obj["tokens"], {"hash": qa_hash}
    ).run()


@qa.command("check", help="Check QA conf")
@click.pass_obj
def cli_qa_check(obj):
    QA("check", obj["project"], obj["config"], obj["tokens"]).run()


@qa.command("describe", help="Describe QA environment")
@click.argument("qa_hash", required=True)
@click.option("--json", is_flag=True, default=False, help="Get response as JSON")
@click.pass_obj
def cli_qa_describe(obj, qa_hash, json):
    flags = {"hash": qa_hash, "json": json}
    QA("describe", obj["project"], obj["config"], obj["tokens"], flags).run()


@qa.command(
    "toggle-maintenance",
    help="Toggle maintenance mode (requires 'manage:maintenance' permission)",
)
@click.pass_obj
def cli_qa_toggle_maintenance(obj):
    QA("toggle-maintenance", obj["project"], obj["config"], obj["tokens"]).run()


@main.group(
    "secret", help="Manage secrets grants in multiple countries (aws-vault needed)"
)
def secret():
    pass


@secret.command("create", help="Create a new secret")
@click.option("-b", "--base-profile", "base_profile", required=False)
@click.pass_obj
def cli_secret_create(obj, base_profile):
    Secret(obj["project"], obj["config"], "create", base_profile).run()


@secret.command("grant", help="Grant permissions to an existing secret")
@click.option("-b", "--base-profile", "base_profile", required=False)
@click.pass_obj
def cli_secret_grant(obj, base_profile):
    Secret(obj["project"], obj["config"], "grant", base_profile).run()
