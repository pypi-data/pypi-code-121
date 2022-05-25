import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from vessl.util.exception import GitError


class GitRepository:
    def __init__(self):
        self.remote = "origin"
        if shutil.which("git"):
            self.root_path = self._get_root_path()
            self.owner, self.repo, self.remote = self._get_github_repo()
            self.commit_ref, self.branch, self.is_head = self._get_remote_revision()

    def check_revision_in_remote(self, revision):
        remote_branches = (
            subprocess.check_output(["git", "branch", "-r", "--contains", revision])
            .decode("utf-8")
            .strip()
            .split("\n")
        )
        for remote_branch in remote_branches:
            if remote_branch.startswith(f"{self.remote}/"):
                return True
        return False

    @staticmethod
    def get_commit_message(revision, format="%h %s (%cr) <%an>"):
        return (
            subprocess.check_output(
                ["git", "log", "--format=%s" % format, "-n", "1", revision]
            )
            .decode("utf-8")
            .strip()
        )

    @staticmethod
    def get_current_diff_status(revision_or_branch):
        untracked_files = (
            subprocess.check_output(["git", "ls-files", "-o", "--exclude-standard"])
            .decode("utf-8")
            .strip()
            .split("\n")
        )
        uncommitted_files = (
            subprocess.check_output(["git", "diff", "--stat", revision_or_branch])
            .decode("utf-8")
            .strip()
            .split("\n")
        )

        untracked_files = [x for x in untracked_files if len(x) > 0]
        uncommitted_files = [x for x in uncommitted_files if len(x) > 0]

        return len(untracked_files) > 0 or len(uncommitted_files) > 0, {
            "untracked": untracked_files,
            "uncommitted": uncommitted_files,
        }

    @staticmethod
    def get_current_diff_file(revision_or_branch, with_untracked=True):
        fp = tempfile.NamedTemporaryFile(suffix=".patch")

        untracked_files = []
        if with_untracked:
            untracked_files = (
                subprocess.check_output(["git", "ls-files", "-o", "--exclude-standard"])
                .decode("utf-8")
                .strip()
                .split("\n")
            )
            untracked_files = [x for x in untracked_files if len(x) > 0]
            for f in untracked_files:
                subprocess.check_output(["git", "add", "-N", f])

        subprocess.call(
            ["git", "diff", "-p", "--binary", f"{revision_or_branch}"], stdout=fp
        )

        if with_untracked:
            for f in untracked_files:
                subprocess.check_output(["git", "reset", "--", f])

        return fp

    @staticmethod
    def _get_root_path():
        try:
            return (
                subprocess.check_output(
                    ["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL
                )
                .decode("utf-8")
                .strip()
            )
        except subprocess.CalledProcessError:
            raise GitError("Are you running in a git repository?")

    @staticmethod
    def _get_github_repo():  # -> (owner, repo, remote)
        remotes = (
            subprocess.check_output(["git", "remote"])
            .decode("utf-8")
            .strip()
            .split("\n")
        )
        for remote in remotes:
            try:
                remote_url = (
                    subprocess.check_output(
                        ["git", "remote", "get-url", remote], stderr=subprocess.DEVNULL
                    )
                    .strip()
                    .decode("utf-8")
                )
                if "github.com" not in remote_url:
                    continue
            except subprocess.CalledProcessError:
                raise GitError(
                    "github.com is not found in remote repositories. You should add your repo to github first."
                )

            regex = re.compile(
                r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)?(/)?"
            )
            repo = regex.search(remote_url).group(7).split("/")

            return repo[-2], repo[-1].rsplit(".git", 1)[0], remote

        return None, None, None

    def _get_active_branch_name(self):
        head_dir = Path(self.root_path) / ".git" / "HEAD"
        with head_dir.open("r") as f:
            content = f.read().splitlines()

        for line in content:
            if line[0:4] == "ref:":
                return line.partition("refs/heads/")[2]

    def _get_remote_revision(self):
        try:
            revision = (
                subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
                )
                .decode("utf-8")
                .strip()
            )
        except subprocess.CalledProcessError:
            raise GitError(
                "git rev-parse HEAD failed. Are you running in git repository?"
            )

        if self.check_revision_in_remote(revision):
            # with revision and patch
            return revision, "HEAD", True
        else:
            # with remote branch and patch
            try:
                upstream_branch_name = (
                    subprocess.check_output(
                        [
                            "git",
                            "rev-parse",
                            "--abbrev-ref",
                            "--symbolic-full-name",
                            "@{u}",
                        ],
                        stderr=subprocess.DEVNULL,
                    )
                    .decode()
                    .strip()
                )
            except subprocess.CalledProcessError:
                raise GitError(
                    f"You should push your branch <{self._get_active_branch_name()}> to github first!"
                )

            revision = (
                subprocess.check_output(["git", "rev-parse", upstream_branch_name])
                .decode("utf-8")
                .strip()
            )
            return revision, upstream_branch_name, False
