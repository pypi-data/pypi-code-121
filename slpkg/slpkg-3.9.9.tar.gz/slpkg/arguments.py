#!/usr/bin/python3
# -*- coding: utf-8 -*-

# arguments.py file is part of slpkg.

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


from slpkg.repolist import RepoList
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.slack.slack_version import slack_ver


def header():
    """help header message"""
    print(f"slpkg - version {_meta_.__version__} | Slackware release: "
          f"{_meta_.slack_rel} - {slack_ver()}\n")


def options():
    """Slpkg is a user-friendly package manager for Slackware installations

Usage: slpkg [COMMANDS|OPTIONS] {repository|package...}

                                                   _       _
                                               ___| |_ __ | | ____ _
                                              / __| | '_ \| |/ / _` |
                                              \__ \ | |_) |   < (_| |
                                              |___/_| .__/|_|\_\__, |
                                                    |_|        |___/
                                             _Slackware package manager_______

Commands:
   update, --repos=[...]                     Run this command to update all
                                             the packages lists.

   upgrade, --repos=[...]                    Delete and recreate all packages
                                             lists.

   repo-add [repository name] [URL]          Add custom repository.

   repo-remove [repository]                  Remove custom repository.

   repo-enable                               Enable or disable default
                                             repositories via dialog utility.

   repo-list                                 Print a list of all the
                                             repositories.

   repo-info [repository]                    Get information about a
                                             repository.

   update slpkg                              Upgrade the program directly from
                                             repository.

   health, --silent                          Health check installed packages.

   deps-status, --tree, --graph=[type]       Print dependencies status used by
                                             packages or drawing dependencies
                                             diagram.

   new-config                                Manage .new configuration files.

   clean-tmp                                 Clean the tmp/ directory from
                                             downloaded packages and sources.
Optional arguments:
  -h | --help                                Print this help message and exit.

  -v | --version                             Print program version and exit.

  -a | --autobuild, [script] [source...]     Auto build SBo packages.
                                             If you have already downloaded the
                                             script and the source code you can
                                             build a new package with this
                                             command.

  -b | --blacklist, [package...] --add,      Manage packages in the blacklist.
       --remove, list                        Add or remove packages and print
                                             the list. Each package is added
                                             here will not be accessible by the
                                             program.

  -q | --queue, [package...] --add,          Manage SBo packages in the queue.
       --remove, list, build, install,       Add or remove and print the list
       build-install                         of packages. Build and then
                                             install the packages from the
                                             queue.

  -g | --config, print, edit, reset          Configuration file management.
                                             Print, edit the configuration file
                                             or reset in the default values.

  -l | --list, [repository], --index,        Print a list of all available
       --installed, --name                   packages from repository, index or
                                             print only packages installed on
                                             the system.

  -c | --check, [repository], --upgrade,     Check for updated packages from
       --rebuild --skip=[...],               the repositories and upgrade or
       --resolve-off, --checklist            install with all dependencies.

  -s | --sync, [repository] [package...],    Sync packages. Install packages
       --rebuild, --reinstall,               directly from remote repositories
       --resolve-off, --download-only,       with all dependencies.
       --directory-prefix=[dir],
       --case-ins, --patches

  -t | --tracking, [repository] [package],   Tracking package dependencies and
       --check-deps, --graph=[type],         print package dependencies tree
       --case-ins                            with highlight if packages is
                                             installed. Also check if
                                             dependencies used or drawing
                                             dependencies diagram.

  -p | --desc, [repository] [package],       Print description of a package
       --color=[]                            directly from the repository and
                                             change color text.

  -n | --network, [package], --checklist,    View a standard of SBo page in
       --case-ins                            terminal and manage multiple
                                             options like reading, downloading,
                                             building, installation, etc.

  -F | --FIND, [package...], --case-ins      Find packages from each enabled
                                             repository and view results.

  -f | --find, [package...], --case-ins,     Find and print installed packages
       --third-party                         reporting the size and the sum.

  -i | --installpkg, [options] [package...]  Installs single or multiple *.tgz
       options=[--warn, --md5sum, --root,    (or .tbz, .tlz, .txz) Slackware
       --infobox, --menu, --terse, --ask,    binary packages designed for use
       --priority, --tagfile]                with the Slackware Linux
                                             distribution onto your system.

  -u | --upgradepkg, [options] [package...]  Upgrade single or multiple
       options=[--dry-run, --install-new,    Slackware binary packages from
       --reinstall, --verbose]               an older version to a newer one.

  -r | --removepkg, [options] [package...],  Removes a previously installed
       --deps, --check-deps, --tag,          Slackware binary packages,
       --checklist, --third-party            while writing a progress report
       options=[-warn, -preserve, -copy,     to the standard output.
       -keep]                                Use only package name.

  -d | --display, [package...]               Display the contents of installed
                                             packages and file list.

You can read more about slpkg from manpage or see examples from readme file.
Issues: https://gitlab.com/dslackw/slpkg/issues
Homepage: https://dslackw.gitlab.io/slpkg/
"""
    header()
    print(options.__doc__)


def usage(repo, stderr):
    """Usage: slpkg [COMMANDS|OPTIONS] {repository|package...}

             Commands:
             [update, --repos=[...]]
             [upgrade, --repos=[...]]
             [repo-add [repository name] [URL]]
             [repo-remove [repository]]
             [repo-enable]
             [repo-list]
             [repo-info [repository]]
             [update [slpkg]]
             [health, --silent]
             [deps-status, --tree, --graph=[type]]
             [new-config]
             [clean-tmp]

             Optional arguments:
             [-h] [-v]
             [-a [script] [sources...]]
             [-b [package...] --add, --remove,
                 [list]]
             [-q [package...] --add, --remove,
                 [list, build, install, build-install]]
             [-g [print, edit, reset]]
             [-l [repository], --index, --installed, --name]
             [-c [repository], --upgrade, --rebuild, --skip=[...],
                               --resolve-off, --checklist]
             [-s [repository] [package...], --rebuild, --reinstall,
                                            --resolve-off, --download-only,
                                            --directory-prefix=[dir],
                                            --case-ins, --patches]
             [-t [repository] [package], --check-deps, --graph=[type],
                                         --case-ins]
             [-p [repository] [package], --color=[]]
             [-n [SBo package], --checklist, --case-ins]
             [-F [package...], --case-ins]
             [-f [package...], --case-ins, --third-party]
             [-i [options] [package...]]
             [-u [options] [package...]]
             [-r [options] [package...], --deps, --check-deps, --tag,
                                         --checklist, --third-party]
             [-d [package...]]
             """
    if repo and repo not in _meta_.repositories:
        error_repo = ""
        all_repos = RepoList().all_repos.keys()
        del RepoList().all_repos
        if repo in all_repos:
            error_repo = (f"slpkg: Error: Repository '{repo}' is not activated"
                          "\n")
        else:
            error_repo = (f"slpkg: Error: Repository '{repo}' does not exist"
                          "\n")
        raise SystemExit(f"\n{error_repo}")
    print(usage.__doc__)
    print("For more information try 'slpkg -h, --help' or view manpage\n")
    if stderr == 1:
        raise SystemExit(stderr)
