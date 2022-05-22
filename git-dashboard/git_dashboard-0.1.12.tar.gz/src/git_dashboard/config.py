# Git Dashboard
# Copyright (C) 2022 Jung Ko <kojung@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Configuration functionality

Configuration is stored as a YAML file with the following format:

"""

import os
import re
import copy

from appdirs import user_config_dir
import yaml
from git import (
    Repo,
    InvalidGitRepositoryError,
    NoSuchPathError,
    GitCommandError
)
from git.compat import (
    defenc
)
from git.util import (
    finalize_process
)

import git_dashboard

CONFIG_DIR = user_config_dir(git_dashboard.__name__, git_dashboard.__author__)
CONFIG = os.path.join(CONFIG_DIR, "config.yaml")

def find_git_repos_from_path(dirname, depth=0, maxdepth=-1):
    """
    recursively find all git repos given the path. stop recusion when `depth == maxdepth`
    """
    # avoid symlinks
    if os.path.islink(dirname):
        return []
    try:
        results = []
        dirpath, dirnames, _ = next(os.walk(dirname))
        if ".git" in dirnames:
            return [dirpath]
        if depth != maxdepth:
            for name in dirnames:
                absname = os.path.join(dirname, name)
                results += find_git_repos_from_path(absname, depth+1, maxdepth)
        return results
    except StopIteration:
        # skip directories where we don't have permission
        return []

def create_default_configuration(root, group='home', config=CONFIG):
    """scan for git repos starting from root"""
    print(f"Scanning git repos from '{root}': ", end='')
    repos = {group: find_git_repos_from_path(root)}
    print(f"found {len(repos['home'])} git repos")
    os.makedirs(os.path.dirname(config), exist_ok=True)
    with open(config, "w", encoding="utf-8") as cfg:
        yaml.dump(repos, cfg)

def short_sha(sha):
    """return a shorter sha signature"""
    return str(sha)[0:8]

def count_untracked_files(repo) -> int:
    """
    return number of untracked files in repo

    :note: equivalent to `return len(repo.untracked_files)` but that operation is too expensive
    if all we want is the number of untracked files.
    """
    proc = repo.git.status(porcelain=True, untracked_files=True, as_process=True)
    # Untracked files preffix in porcelain mode
    prefix = "?? "
    untracked_files = 0
    for line in proc.stdout:
        line = line.decode(defenc)
        if line.startswith(prefix):
            untracked_files += 1
    finalize_process(proc)
    return untracked_files

def analyze(path):
    """
    given a path to a git repository, return:
    {name: name, branch: branch, status: status, path: path}
    """
    name = os.path.basename(path)
    try:
        repo = Repo(path)
        head = repo.head
        # determine branch
        if head.is_detached:
            branch = f"detached:{short_sha(head.commit)}"
        else:
            branch = head.reference.name

        status = []
        # check for modified files
        if repo.is_dirty():
            status.append("dirty")
        else:
            status.append("clean")

        # check for ahead/behind w.r.t to upstream ref
        try:
            cmd = "git rev-parse --abbrev-ref --symbolic-full-name @{u}"
            upstream = repo.git.execute(cmd, shell=True)

            cmd = f"git rev-list --left-right --count HEAD...{upstream}"
            ahead, behind = [int(x) for x in repo.git.execute(cmd, shell=True).split()]

            status += [f"-{behind}", f"+{ahead}"]
        except GitCommandError:
            pass

        # count untracked files
        status.append(f"u{count_untracked_files(repo)}")

        # count staged files
        status.append(f"s{len(repo.index.diff('HEAD'))}")

        joined_status = "/".join(status)

        # simplify the clean case
        if joined_status in ["clean/-0/+0/u0/s0", "clean/u0/s0"]:
            joined_status = "clean"
        return {"name": name, "branch": branch, "status": joined_status, "path": path}
    except (InvalidGitRepositoryError, NoSuchPathError):
        return {"name": name, "branch": "n/a", "status": "not a git repo", "path": path}

def load_configuration(config=CONFIG, initial:bool = False):
    """
    Load configuration in YAML format.
    If `initial` is True, display warnings if some repos are not valid.
    """
    with open(config, "r", encoding="utf-8") as cfg:
        groups = yaml.safe_load(cfg)

    # iterate through each group and do:
    # 1. expand paths that contain other git repos
    # 2. analyze git repos
    results  = {}
    excludes = set()
    for name, group in groups.items():
        # expand directories that contain other git repos
        results[name] = []
        for dirname in group:
            if re.match(r"^!", dirname):
                excludes.add(re.sub(r"^!", "", dirname))
                continue
            try:
                _, dirnames, _ = next(os.walk(dirname))
                if ".git" not in dirnames:
                    for sub_repo in find_git_repos_from_path(dirname, 0, 1):
                        results[name].append(analyze(sub_repo))
                else:
                    results[name].append(analyze(dirname))
            except StopIteration:
                # dirname is not valid, warn about it for the first time
                if initial:
                    print(f"WARNING: Directory {dirname} is not valid. Ignoring directory")

        # process exclusions
        for repo in copy.copy(results[name]):
            if repo["path"] in excludes:
                results[name].remove(repo)
                if initial:
                    print(f"WARNING: Excluding directory '{repo['path']}'")
    return results
