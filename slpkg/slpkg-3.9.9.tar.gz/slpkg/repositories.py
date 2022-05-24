#!/usr/bin/python3
# -*- coding: utf-8 -*-

# repositories.py file is part of slpkg.

# Copyright 2014-2022 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://gitlab.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os

from slpkg.utils import Utils
from slpkg.__metadata__ import MetaData as _meta_


class Repo(Utils):
    """Manage repositories configuration files
    """
    def __init__(self):
        self.meta = _meta_
        self.DEFAULT_REPOS_NAMES = self.meta.default_repositories
        self.custom_repo_file = "/etc/slpkg/custom-repositories"
        self.default_repo_file = "/etc/slpkg/default-repositories"
        self.custom_repositories_list = self.read_file(
            self.custom_repo_file)
        self.default_repositories_list = self.read_file(
            self.default_repo_file)
        self.default_repository()

    def add(self, repo, url):
        """Write custom repository name and url in a file
        """
        repo_name = []
        if not url.endswith("/"):
            url += "/"
        for line in self.custom_repositories_list.splitlines():
            line = line.lstrip()
            if line and not line.startswith("#"):
                repo_name.append(line.split()[0])
        if (repo in self.meta.repositories or repo in repo_name or
                repo in self.meta.default_repositories):
            raise SystemExit(f"\nRepository name '{repo}' exist, "
                             f"select different name.\n"
                             f"View all repositories with command 'slpkg "
                             f"repo-list'.\n")
        elif len(repo) > 6:
            raise SystemExit("\nslpkg: Error: Maximum repository name length "
                  "must be six (6) characters\n")
        with open(self.custom_repo_file, "a") as repos:
            new_line = f"  {repo}{' ' * (10 - len(repo))}{url}\n"
            repos.write(new_line)
        print(f"\nRepository '{repo}' successfully added\n")

    def remove(self, repo):
        """Remove custom repository
        """
        rem_repo = False
        with open(self.custom_repo_file, "w") as repos:
            for line in self.custom_repositories_list.splitlines():
                repo_name = line.split()[0]
                if repo_name != repo:
                    repos.write(f"{line}\n")
                else:
                    print(f"\nRepository '{repo}' successfully "
                          "removed\n")
                    rem_repo = True
        if not rem_repo:
            print(f"\nRepository '{repo}' doesn't exist\n")

    def custom_repository(self):
        """Return dictionary with repo name and url (used external)
        """
        custom_dict_repo = {}
        for line in self.custom_repositories_list.splitlines():
            line = line.lstrip()
            if not line.startswith("#"):
                custom_dict_repo[line.split()[0]] = line.split()[1]
        return custom_dict_repo

    def default_repository(self):
        """Return dictionary with default repo name and url
        """
        default_dict_repo = {}
        for line in self.default_repositories_list.splitlines():
            line = line.lstrip()
            if not line.startswith("#"):
                if line.split()[0] in self.DEFAULT_REPOS_NAMES:
                    default_dict_repo[line.split()[0]] = line.split()[1]
                else:
                    raise SystemExit(f"\nslpkg: Error: Repository name "
                                     f"'{line.split()[0]}'"
                                     f" is not default.\n              "
                                     f"Please check file: "
                                     f"/etc/slpkg/default-repositories\n")
        return default_dict_repo

    def slack(self):
        """Official slackware repository
        """
        default = "http://mirrors.slackware.com/slackware/"
        if self.meta.arch.startswith("arm"):
            default = "http://ftp.arm.slackware.com/slackwarearm/"
        if os.path.isfile("/etc/slpkg/slackware-mirrors"):
            mirrors = self.read_file(
                f"{self.meta.conf_path}slackware-mirrors")
            for line in mirrors.splitlines():
                line = line.rstrip()
                if not line.startswith("#") and line:
                    default = line.split()[-1]
        if not default.endswith("/"):
            default += "/"
        return default
