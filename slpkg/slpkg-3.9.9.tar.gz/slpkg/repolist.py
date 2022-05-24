#!/usr/bin/python3
# -*- coding: utf-8 -*-

# repolist.py file is part of slpkg.

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


from slpkg.messages import Msg
from slpkg.repositories import Repo
from slpkg.__metadata__ import MetaData as _meta_


class RepoList:
    """List of repositories
    """
    def __init__(self):
        self.meta = _meta_
        self.green = self.meta.color["GREEN"]
        self.red = self.meta.color["RED"]
        self.grey = self.meta.color["GREY"]
        self.endc = self.meta.color["ENDC"]
        self.msg = Msg()
        self.all_repos = Repo().default_repository()
        self.all_repos["slack"] = Repo().slack()
        self.all_repos.update(Repo().custom_repository())

    def repos(self):
        """View or enabled or disabled repositories
        """
        def_cnt, cus_cnt = 0, 0
        self.msg.template(78)
        print("{0}{1}{2}{3}{4}{5}{6}".format(
            "| Repo_id", " " * 2,
            "Repo_URL", " " * 44,
            "Default", " " * 3,
            "Status"))
        self.msg.template(78)
        for repo_id, repo_URL in sorted(self.all_repos.items()):
            status, COLOR = "disabled", self.red
            default = "yes"
            if len(repo_URL) > 49:
                repo_URL = repo_URL[:48] + "~"
            if repo_id in self.meta.repositories:
                def_cnt += 1
                status, COLOR = "enabled", self.green
            if repo_id not in self.meta.default_repositories:
                cus_cnt += 1
                default = "no"
            print("  {0}{1}{2}{3}{4}{5}{6}{7:>8}{8}".format(
                repo_id, " " * (9 - len(repo_id)),
                repo_URL, " " * (52 - len(repo_URL)),
                default, " " * (8 - len(default)),
                COLOR, status, self.endc))

        print("\nRepositories summary")
        print("=" * 79)
        print(f"{self.grey}{def_cnt}/{len(self.all_repos)} enabled default "
              f"repositories and {cus_cnt} custom.")
        print("Edit the file '/etc/slpkg/repositories.conf' for enable "
              "and disable default\nrepositories or run 'slpkg "
              f"repo-enable' command.{self.endc}")
