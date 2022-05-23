# -*- encoding: utf-8 -*-
import os
import re
import subprocess
import sys
from itertools import groupby
from subprocess import CalledProcessError

import semver
from halo import Halo

from suite_py.lib import logger


class GitHandler:
    def __init__(self, repo, config):
        self._repo = repo
        self._projects_home = config.user["projects_home"]
        self._path = os.path.join(self._projects_home, repo)

    def get_repo(self):
        return self._repo

    def get_path(self):
        return self._path

    def clone(self):
        subprocess.run(
            ["git", "clone", f"git@github.com:primait/{self._repo}.git"],
            cwd=self._projects_home,
            check=True,
        )

    def checkout(self, branch, new=False):
        try:
            if new:
                subprocess.run(
                    ["git", "checkout", "-b", branch],
                    cwd=self._path,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.run(
                    ["git", "checkout", branch],
                    cwd=self._path,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if not self.is_detached():  # Skip pulling if detached
                    self.pull(rebase=True)
        except (CalledProcessError) as e:
            logger.error(f"Error during command execution: {e}")
            sys.exit(-1)

    def commit(self, commit_message="", dummy=False):
        try:
            if dummy:
                subprocess.run(
                    ["git", "commit", "--allow-empty", "-m", commit_message],
                    cwd=self._path,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.run(
                    ["git", "commit", "-am", commit_message],
                    cwd=self._path,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except (CalledProcessError) as e:
            logger.error(f"Error during command execution: {e}")
            sys.exit(-1)

    def add(self):
        try:
            subprocess.run(["git", "add", "."], cwd=self._path, check=True)
        except (CalledProcessError) as e:
            logger.error(f"Error during command execution: {e}")
            sys.exit(-1)

    def push(self, branch, remote="origin"):
        with Halo(text=f"Pushing {self._repo}...", spinner="dots", color="magenta"):
            try:
                subprocess.run(
                    ["git", "push", remote, branch],
                    cwd=self._path,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except (CalledProcessError) as e:
                logger.error(f"Error during command execution: {e}")
                sys.exit(-1)

    def pull(self, rebase=False):
        with Halo(text=f"Pulling {self._repo}...", spinner="dots", color="magenta"):
            try:
                if rebase:
                    subprocess.run(
                        ["git", "pull", "--rebase"],
                        cwd=self._path,
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    subprocess.run(
                        ["git", "pull"],
                        cwd=self._path,
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
            except (CalledProcessError) as e:
                logger.error(f"Error during command execution: {e}")
                sys.exit(-1)

    def fetch(self, remote="origin"):
        with Halo(text=f"Fetching {self._repo}...", spinner="dots", color="magenta"):
            try:
                subprocess.run(
                    ["git", "fetch", "--quiet"],
                    cwd=self._path,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                subprocess.run(
                    ["git", "fetch", "-p", remote, "--quiet"],
                    cwd=self._path,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except (CalledProcessError) as e:
                logger.error(f"Error during command execution: {e}")
                sys.exit(-1)

    def sync(self):
        self.fetch()
        self.checkout("master")
        self.pull()

    def check_repo_cloned(self):
        if self._repo not in os.listdir(self._projects_home):
            logger.warning("The project is not in your home path, cloning it now...")
            self.clone()

    def delete_remote_branch(self, branch):
        try:
            self.push(f":{branch}")
            return True
        except BaseException:
            return False

    def get_last_tag(self):
        self.sync()
        return (
            subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"])
            .decode("utf-8")
            .strip()
        )

    def search_remote_branch(self, regex):
        try:
            output = subprocess.run(
                ["git", "branch", "-r", "--list", regex],
                cwd=self._path,
                check=True,
                stdout=subprocess.PIPE,
            )

            result = output.stdout.decode("utf-8").strip("\n").strip()

            if result.startswith("origin/"):
                return result[7:]
            return result

        except CalledProcessError:
            return ""

    def local_branch_exists(self, branch):
        try:
            subprocess.run(
                ["git", "show-ref", "--quiet", f"refs/heads/{branch}"],
                cwd=self._path,
                check=True,
            )
            return True
        except CalledProcessError:
            return False

    def remote_branch_exists(self, branch):
        try:
            self.fetch()
            subprocess.run(
                ["git", "show-ref", "--quiet", f"refs/remotes/origin/{branch}"],
                cwd=self._path,
                check=True,
            )
            return True
        except CalledProcessError:
            return False

    def current_branch_name(self):
        try:
            output = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self._path,
                stdout=subprocess.PIPE,
                check=True,
            ).stdout.decode("utf-8")
            return re.sub("\n", "", output)
        except (CalledProcessError) as e:
            logger.error(f"Error during command execution: {e}")
            sys.exit(-1)

    def is_detached(self):
        return self.current_branch_name() == "HEAD"

    def is_dirty(self, untracked=False):
        if untracked:
            command = ["git", "status", "--porcelain"]
        else:
            command = ["git", "status", "--porcelain", "-uno"]

        try:
            output = subprocess.run(
                command,
                cwd=self._path,
                check=True,
                stdout=subprocess.PIPE,
            ).stdout.decode("utf-8")

            return len(output) != 0
        except (CalledProcessError) as e:
            logger.error(f"Error during command execution: {e}")
            sys.exit(-1)

    def reset(self):
        try:
            subprocess.run(
                ["git", "reset", "HEAD", "--hard", "--quiet"],
                cwd=self._path,
                check=True,
            )
        except CalledProcessError as e:
            logger.error(f"Error during git reset on {self._repo}: {e}")
            sys.exit(-1)


def is_repo(directory):
    try:
        subprocess.run(
            ["git", "status"],
            cwd=directory,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except CalledProcessError:
        return False


def get_username():
    try:
        output = subprocess.run(
            ["git", "config", "user.name"], check=True, stdout=subprocess.PIPE
        ).stdout.decode("utf-8")
        output = re.sub("[^A-Za-z]", "", output)
        return re.sub("\n", "", output)
    except CalledProcessError:
        return None


def files_changed_between_commits(from_commit, to_commit):
    p = subprocess.Popen(  # pylint: disable=consider-using-with
        ["git", "diff", from_commit, to_commit, "--name-only"], stdout=subprocess.PIPE
    )
    result = p.communicate()[0]
    return result.decode("utf-8").splitlines()


def migrations_found(files_changed):
    for file in files_changed:
        if "migration" in file.lower():
            return True
    return False


def get_last_tag_number(tags):
    for tag in tags:
        if is_semver(tag.name):
            return tag.name
    return None


def is_semver(tag):
    try:
        return semver.parse(tag)
    except Exception:
        return None


def get_commit_logs(base_branch):
    """
    Get all the commits from HEAD that are *not* in `base_branch` and return
    their logs as a list. The commits are orderded from latest to first.
    """
    commits = subprocess.check_output(
        ["git", "log", "--pretty=medium", f"HEAD...{base_branch}"]
    ).decode("utf-8")

    commits_list = [
        "\n".join([line.lstrip() for line in split_result])
        for is_commit_line, split_result in groupby(
            commits.split("\n"),
            lambda line: re.match("commit [0-9a-f]{40}", line) is not None,
        )
        if not is_commit_line
    ]

    return commits_list
