import os
import re
from collections import OrderedDict
from typing import Generator, List, Optional, Reversible

import delegator
from git import Commit
from git.exc import InvalidGitRepositoryError
from git.repo import Repo
from github import Github
from github.Label import Label
from github.Issue import Issue
from github.GithubException import UnknownObjectException
from github.Repository import Repository

from cherrytree.classes import CherryTreeExecutionException

# PRs are either of form "Merge pull request #nnn from..." or "...(#nnn)"
PR_REGEX = re.compile(r"(^Merge pull request #(\d+) from|\(#(\d+)\)$)")


def get_github_instance(access_token: str) -> Github:
    return Github(access_token)


def get_access_token(access_token: Optional[str]) -> str:
    if access_token:
        return access_token

    access_token = os.environ.get("GITHUB_TOKEN")
    if not access_token:
        raise NotImplementedError("Env var 'GITHUB_TOKEN' is missing")

    return access_token


def get_repo(repo: str, access_token: str) -> Repository:
    g = get_github_instance(access_token)
    return g.get_repo(repo)


def get_issues_from_labels(
        repo: str,
        access_token: str,
        label: str,
        prs_only: bool = False,
) -> List[Issue]:
    label_objects: List[Label] = []
    gh_repo = get_repo(repo, access_token)
    try:
        label_objects.append(gh_repo.get_label(label))
    except UnknownObjectException:
        # unknown label
        return []
    issues = gh_repo.get_issues(labels=label_objects, state="all")
    if prs_only:
        return [o for o in issues if o.pull_request]
    return [o for o in issues]


def get_issue(repo: str, access_token: str, id_: int) -> Optional[Issue]:
    gh_repo = get_repo(repo, access_token)
    try:
        return gh_repo.get_issue(id_)
    except UnknownObjectException:
        # unknown id
        return None


def get_commits(repo: str, access_token: str, branch: str, since=None):
    """Get commit objects from a branch, over a limited period"""
    gh_repo = get_repo(repo, access_token)
    branch_object = gh_repo.get_branch(branch)
    sha = branch_object.commit.sha
    if since:
        commits = gh_repo.get_commits(sha=sha, since=since)
    else:
        commits = gh_repo.get_commits(sha=sha)
    return commits


def commit_pr_number(commit: Commit) -> Optional[int]:
    """Given a commit object, returns the PR number"""
    res = PR_REGEX.search(commit.summary)
    if res:
        groups = res.groups()
        return int(groups[1] or groups[2])
    return None


def get_commit_pr_map(commits: Reversible[Commit]):
    """Given a list of commits and prs, returns a map of pr_number to commit"""
    d = OrderedDict()
    for commit in reversed(commits):
        pr_number = commit_pr_number(commit)
        if pr_number:
            d[pr_number] = commit
    return d


def truncate_str(value: str, width: int = 90) -> str:
    cont_str = "..."
    trunc_value = value[: width - len(cont_str)].strip()
    if len(trunc_value) < len(value.strip()):
        trunc_value = f"{trunc_value}{cont_str}"
    return f"{trunc_value:<{width}}"


def git_get_current_head() -> str:
    output = os_system("git status | head -1")
    match = re.match("(?:HEAD detached at|On branch) (.*)", output)
    if not match:
        return ""
    return match.group(1)


def os_system(cmd, raise_on_error=True) -> str:
    p = delegator.run(cmd)
    if raise_on_error and p.return_code != 0:
        raise CherryTreeExecutionException(p.err)
    return p.out


def check_if_branch_exists(branch: str) -> bool:
    current_head = git_get_current_head()
    try:
        os_system(f"git checkout {branch}")
    except CherryTreeExecutionException:
        return False
    os_system(f"git checkout {current_head}")
    return True


def deduplicate_prs(prs: List[Issue]) -> List[Issue]:
    pr_set = set()
    ret: List[Issue] = []
    for pr in prs:
        if pr.number not in pr_set:
            ret.append(pr)
            pr_set.add(pr.number)
    return ret


def get_git_repo() -> Repo:
    """
    Find the path containing the git repo. Start by checking the current working
    directory, and proceed up the directory tree if a git repo can't be found.

    returns: Paath to closest git repo
    raises FileNotFoundError: if no git repo is found in the current path
    """
    def _traverse_dirs(path: str) -> Generator[str, None, None]:
        # first yield the current directory
        yield path
        # then start yielding parents until we reach the root
        while True:
            parent = os.path.dirname(path)
            if path != parent:
                yield parent
                path = parent
            else:
                break

    cwd = os.getcwd()
    for dir_ in _traverse_dirs(cwd):
        try:
            repo = Repo(dir_)
            return repo
        except InvalidGitRepositoryError:
            pass
    raise FileNotFoundError("No git repo found in path: {}". format(cwd))
