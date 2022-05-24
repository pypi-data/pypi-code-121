#!/usr/bin/python3
# -*- coding: utf-8 -*-

# main.py file is part of slpkg.

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
import sys

from slpkg.clean import clean_tmp
from slpkg.load import Regex
from slpkg.desc import PkgDesc
from slpkg.messages import Msg
from slpkg.config import Config
from slpkg.checks import Updates
from slpkg.repoinfo import RepoInfo
from slpkg.repolist import RepoList
from slpkg.repositories import Repo
from slpkg.blacklist import BlackList
from slpkg.version import prog_version
from slpkg.auto_pkg import AutoInstall
from slpkg.health import PackageHealth
from slpkg.new_config import NewConfig
from slpkg.tracking import TrackingDeps
from slpkg.repoenable import RepoEnable
from slpkg.pkg_find import FindFromRepos
from slpkg.arguments import options, usage
from slpkg.slpkg_update import it_self_update
from slpkg.status_deps import DependenciesStatus

from slpkg.init import (
    Update,
    Upgrade,
    check_exists_repositories
)
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.manager import PackageManager

from slpkg.sbo.queue import QueuePkgs
from slpkg.sbo.check import sbo_upgrade
from slpkg.sbo.network import SBoNetwork
from slpkg.sbo.autobuild import AutoBuild
from slpkg.sbo.slackbuild import SBoInstall

from slpkg.slack.patches import Patches
from slpkg.binary.check import pkg_upgrade
from slpkg.binary.install import BinaryInstall


class ArgParse(BlackList):

    def __init__(self, args):
        super().__init__()
        self.args = args
        self.meta = _meta_
        self.msg = Msg()
        self.commands = [
            "update",
            "upgrade",
            "repo-add",
            "repo-remove",
            "repo-enable",
            "repo-list",
            "repo-info",
            "update-slpkg",
            "health",
            "deps-status",
            "new-config",
            "clean"
        ]

        options = [
            "-c", "--check",
            "-l", "--list",
            "-c", "--check",
            "-s", "--sync",
            "-t", "--tracking",
            "-p", "--desc",
            "-F", "--FIND",
            "-f", "--find"
        ]

        # checking if repositories exists
        enabled_repos = _meta_.repositories
        if len(self.args) > 1:
            repo = self.args[1]
            check = check_exists_repositories(repo)
        if (len(self.args) > 1 and self.args[0] in options
                and check is False and repo in enabled_repos):
            print("\n  Please update the packages lists. Run 'slpkg update'.\n"
                  "  This command should be used to synchronize the packages\n"
                  "  lists from the repositories that are enabled.\n")
            raise SystemExit(1)

    def help_version(self):
        """Help and version info
        """
        if (len(self.args) == 1 and self.args[0] in ["-h", "--help"] and
                self.args[1:] == []):
            options()
        elif (len(self.args) == 1 and self.args[0] in ["-v", "--version"] and
                self.args[1:] == []):
            prog_version()
        else:
            usage("", 1)

    def command_update(self):
        """Update package lists repositories
        """
        update = Update()
        if len(self.args) == 1 and self.args[0] == "update":
            update.run(repos="")
        elif (len(self.args) == 2 and self.args[0] == "update" and
                self.args[1].startswith("--repos=")):
            repos = self.args[1].split("=")[-1].split(",")
            for rp in repos:
                if rp not in self.meta.repositories:
                    usage(rp, 1)
            update.run(repos)
        else:
            usage("", 1)

    def command_upgrade(self):
        """Recreate repositories package lists
        """
        upgrade = Upgrade()
        if len(self.args) == 1 and self.args[0] == "upgrade":
            upgrade.run(repos="")
        elif (len(self.args) == 2 and self.args[0] == "upgrade" and
                self.args[1].startswith("--repos=")):
            repos = self.args[1].split("=")[-1].split(",")
            for rp in repos:
                if rp not in self.meta.repositories:
                    usage(rp, 1)
            upgrade.run(repos)
        else:
            usage("", 1)

    def command_update_slpkg(self):
        """Slpkg it self update
        """
        if len(self.args) == 2 and self.args[0] == "update-slpkg":
            it_self_update()
        else:
            usage("", 1)

    def command_repo_enable(self):
        """Repositories enable/disable
        """
        self.if_checklist()
        if len(self.args) == 1 and self.args[0] == "repo-enable":
            RepoEnable().choose()
        else:
            usage("", 1)

    def command_repo_list(self):
        """Repositories list
        """
        if len(self.args) == 1 and self.args[0] == "repo-list":
            RepoList().repos()
        else:
            usage("", 1)

    def command_repo_add(self):
        """Add custom repositories
        """
        if len(self.args) == 3 and self.args[0] == "repo-add":
            Repo().add(self.args[1], self.args[2])
        else:
            usage("", 1)

    def command_repo_remove(self):
        """Remove custom repositories
        """
        if len(self.args) == 2 and self.args[0] == "repo-remove":
            Repo().remove(self.args[1])
        else:
            usage("", 1)

    def command_repo_info(self):
        """Repositories informations
        """
        if (len(self.args) == 2 and self.args[0] == "repo-info" and
                self.args[1] in RepoList().all_repos):
            del RepoList().all_repos
            RepoInfo().view(self.args[1])
        elif (len(self.args) > 1 and self.args[0] == "repo-info" and
                self.args[1] not in RepoList().all_repos):
            usage(self.args[1], 1)
        else:
            usage("", 1)

    def command_health(self):
        """Check package health
        """
        if len(self.args) == 1 and self.args[0] == "health":
            PackageHealth(mode="").test()
        elif (len(self.args) == 2 and self.args[0] == "health" and
                self.args[1] == "--silent"):
            PackageHealth(mode=self.args[1]).test()
        else:
            usage("", 1)

    def command_deps_status(self):
        """Print dependencies status
        """
        image = ""
        for arg in self.args:
            if arg.startswith("--graph="):
                image = arg.split("=")[1]
        if len(self.args) == 1 and self.args[0] == "deps-status":
            DependenciesStatus(image).show()
        elif len(self.args) == 2 and self.args[0] == "deps-status" and image:
            DependenciesStatus(image).show()
        elif (len(self.args) == 2 and self.args[0] == "deps-status" and
                "--tree" in self.args):
            DependenciesStatus(image).tree()
        elif (len(self.args) == 3 and self.args[0] == "deps-status" and
                "--tree" in self.args and image):
            DependenciesStatus(image).tree()
        else:
            usage("", 1)

    def command_new_config(self):
        """Manage .new configuration files
        """
        if len(self.args) == 1 and self.args[0] == "new-config":
            NewConfig().run()
        else:
            usage("", 1)

    def command_clean_tmp(self):
        """Clean all downloaded packages and sources"""
        if len(self.args) == 1 and self.args[0] == "clean-tmp":
            clean_tmp()
        else:
            usage("", 1)

    def auto_build(self):
        """Auto built tool
        """
        options = [
            "-a",
            "--autobuild"
        ]
        if len(self.args) >= 3 and self.args[0] in options:
            AutoBuild(self.args[1], self.args[2:], self.meta.path).run()
        else:
            usage("", 1)

    def pkg_list(self):
        """List of packages by repository
        """
        options = [
            "-l",
            "--list"
        ]
        flag = ["--index", "--installed", "--name"]
        name = INDEX = installed = False
        for arg in self.args[2:]:
            if flag[0] == arg:
                INDEX = True
            if flag[1] in arg:
                installed = True
            if flag[2] == arg:
                name = True
            if arg not in flag:
                usage("", 1)
        if (len(self.args) > 1 and len(self.args) <= 5 and
                self.args[0] in options):
            if self.args[1] in self.meta.repositories:
                PackageManager(binary=None).package_list(self.args[1],
                                                         name,
                                                         INDEX,
                                                         installed)
            else:
                usage(self.args[1], 1)
        else:
            usage("", 1)

    def pkg_upgrade(self):
        """Check and upgrade packages by repository
        """
        options = [
            "-c",
            "--check"
        ]
        flags = [
            "--upgrade",
            "--skip=",
            "--resolve-off",
            "--checklist",
            "--rebuild"
        ]
        flag, skip = self.__pkg_upgrade_flags(flags)

        # Remove --checklist flag from args so that works with
        # both conditions
        # if flags[3] in self.args:
        #    self.args.remove(flags[3])

        if (len(self.args) >= 3 and self.args[0] in options and
                self.args[2] == flags[0] and
                self.args[1] in self.meta.repositories):
            if self.args[1] not in ["slack", "sbo"]:
                BinaryInstall(pkg_upgrade(self.args[1], skip, flag),
                              self.args[1], flag).start(is_upgrade=True)
            elif self.args[1] == "slack":
                Patches(skip, flag).start()
            elif self.args[1] == "sbo":
                SBoInstall(sbo_upgrade(skip, flag), flag).start(
                    is_upgrade=True)
            else:
                usage(self.args[1], 1)
        elif len(self.args) == 1 and self.args[0] in options:
            Updates(repo="").ALL()
        elif len(self.args) == 2 and self.args[0] in options:
            Updates(self.args[1]).run()
        elif (len(self.args) >= 2 and self.args[0] in options and
              self.args[1] not in self.meta.repositories):
            usage(self.args[1], 1)
        else:
            usage("", 1)

    def __pkg_upgrade_flags(self, flags):
        """Manage flags for package upgrade option
        """
        # Check for typos or unssuported flags
        for arg in self.args[2:]:
            if arg not in flags:
                usage("", 1)

        flag, skip = [], ""
        if flags[0] in self.args:
            for arg in self.args:
                if arg.startswith(flags[1]):
                    skip = Regex(arg.split("=")[1]).get()
                    self.args.remove(arg)
                if arg in flags:
                    flag.append(arg)
                    if arg not in self.args:
                        self.args.remove(arg)
        if "--checklist" in flag:
            self.if_checklist()
        return flag, skip

    def pkg_install(self):
        """Install packages by repository
        """
        flag = []
        options = [
            "-s",
            "--sync"
        ]
        additional_options = [
            "--resolve-off",
            "--download-only",
            "--directory-prefix=",
            "--case-ins",
            "--rebuild",
            "--reinstall",
            "--patches"
        ]
        for arg in self.args:
            if arg.startswith(additional_options[2]):
                flag.append(arg)
                arg = ""
            if arg in additional_options:
                flag.append(arg)
        # clean from flags
        for ar in flag:
            if ar in self.args:
                self.args.remove(ar)
        if len(self.args) >= 3 and self.args[0] in options:
            if (self.args[1] in self.meta.repositories and
                    self.args[1] not in ["sbo"]):
                BinaryInstall(self.args[2:], self.args[1], flag).start(
                    is_upgrade=False)
            elif (self.args[1] == "sbo" and
                    self.args[1] in self.meta.repositories):
                SBoInstall(self.args[2:], flag).start(is_upgrade=False)
            else:
                usage(self.args[1], 1)
        else:
            usage("", 1)

    def pkg_tracking(self):
        """Tracking package dependencies
        """
        flag = []
        options = [
            "-t",
            "--tracking"
        ]
        additional_options = [
            "--check-deps",
            "--graph=",
            "--case-ins"
        ]
        for arg in self.args[2:]:
            if arg.startswith(additional_options[1]):
                flag.append(arg)
                self.args.remove(arg)
            if arg in additional_options:
                flag.append(arg)
        # clean additional options from args
        for f in flag:
            if f in self.args:
                self.args.remove(f)
        # print usage message if wrong additional option
        for arg in self.args:
            if arg.startswith("--"):
                if arg not in additional_options:
                    usage("", 1)
        if (len(self.args) >= 3 and len(self.args) <= 3 and
                self.args[0] in options and
                self.args[1] in self.meta.repositories):
            TrackingDeps(self.args[2], self.args[1], flag).run()
        elif (len(self.args) >= 2 and
                self.args[1] not in self.meta.repositories):
            usage(self.args[1], 1)
        else:
            usage("", 1)

    def sbo_network(self):
        """View slackbuilds packages
        """
        flag = []
        options = [
            "-n",
            "--network"
        ]
        additional_options = [
            "--checklist",
            "--case-ins"
        ]
        for add in additional_options:
            if add in self.args:
                flag.append(add)
                self.args.remove(add)
        if "--checklist" in flag:
            self.if_checklist()
        if (len(self.args) == 2 and self.args[0] in options and
                "sbo" in self.meta.repositories):
            SBoNetwork(self.args[1], flag).view()
        elif (len(self.args) == 1 and self.args[0] in options and
                "sbo" in self.meta.repositories and
                additional_options[0] in flag):
            SBoNetwork("", flag).view()
        else:
            usage("sbo", 1)

    def pkg_blacklist(self):
        """Manage blacklist packages
        """
        options = [
            "-b",
            "--blacklist"
        ]
        flag = [
            "--add",
            "--remove"
        ]
        command = ["list"]
        if (len(self.args) == 2 and self.args[0] in options and
                self.args[1] == command[0]):
            self.black_listed()
        elif (len(self.args) > 2 and self.args[0] in options and
                flag[0] in self.args):
            self.args.remove(flag[0])
            self.black_add(self.args[1:])
        elif (len(self.args) == 2 and self.args[0] in options and
                flag[1] in self.args):
            self.args.remove(flag[1])
            self.black_remove(list(self.get_black()))
        elif (len(self.args) > 2 and self.args[0] in options and
                flag[1] in self.args):
            self.args.remove(flag[1])
            self.black_remove(self.args[1:])
        else:
            usage("", 1)

    def pkg_queue(self):
        """Manage packages in queue
        """
        queue = QueuePkgs()
        options = [
            "-q",
            "--queue"
        ]
        flag = [
            "--add",
            "--remove"
        ]
        command = [
            "list",
            "build",
            "install",
            "build-install"
        ]
        if (len(self.args) > 2 and self.args[0] in options and
                flag[0] in self.args):
            self.args.remove(flag[0])
            queue.add(self.args[1:])
        elif (len(self.args) == 2 and self.args[0] in options and
                flag[1] in self.args):
            self.args.remove(flag[1])
            queue.remove(queue.packages())
        elif (len(self.args) > 2 and self.args[0] in options and
                flag[1] in self.args):
            self.args.remove(flag[1])
            queue.remove(self.args[1:])
        elif (len(self.args) == 2 and self.args[0] in options and
                self.args[1] == command[0]):
            queue.listed()
        elif (len(self.args) == 2 and self.args[0] in options and
                self.args[1] == command[1]):
            queue.build()
        elif (len(self.args) == 2 and self.args[0] in options and
                self.args[1] == command[2]):
            queue.install()
        elif (len(self.args) == 2 and self.args[0] in options and
                self.args[1] == command[3]):
            queue.build()
            queue.install()
        else:
            usage("", 1)

    def bin_install(self):
        """Install Slackware binary packages
        """
        packages = self.args[1:]
        options = [
            "-i",
            "--installpkg"
        ]
        flag = ""
        flags = [
            "--warn",
            "--md5sum",
            "--root",
            "--infobox",
            "--menu",
            "--terse",
            "--ask",
            "--priority",
            "--tagfile"
        ]
        if len(self.args) > 1 and self.args[0] in options:
            if self.args[1] in flags:
                flag = self.args[1]
                packages = self.args[2:]
            PackageManager(packages).install(flag)
        else:
            usage("", 1)

    def bin_upgrade(self):
        """Install-upgrade Slackware binary packages
        """
        packages = self.args[1:]
        options = [
            "-u",
            "--upgradepkg"
        ]
        flag = ""
        flags = [
            "--dry-run",
            "--install-new",
            "--reinstall",
            "--verbose"
        ]
        if len(self.args) > 1 and self.args[0] in options:
            if self.args[1] in flags:
                flag = self.args[1]
                packages = self.args[2:]
            PackageManager(packages).upgrade(flag)
        else:
            usage("", 1)

    def bin_remove(self):
        """Remove Slackware packages
        """
        packages = self.args[1:]
        options = [
            "-r",
            "--removepkg"
        ]
        additional_options = [
            "--deps",
            "--check-deps",
            "--tag",
            "--checklist",
            "--third-party"
        ]
        flag, extra = "", []
        flags = [
            "-warn",
            "-preserve",
            "-copy",
            "-keep"
        ]
        # merge --check-deps and --deps options
        if (additional_options[1] in self.args and
                additional_options[0] not in self.args):
            self.args.append(additional_options[0])
        if len(self.args) > 1 and self.args[0] in options:
            for additional in additional_options:
                if additional in self.args:
                    extra.append(additional)
                    self.args.remove(additional)
                packages = self.args[1:]
            for fl in flags:
                if fl in self.args:
                    flag = self.args[1]
                    packages = self.args[2:]
            if "--checklist" in extra:
                self.if_checklist()
            if not packages:
                packages = [""]
            PackageManager(packages).remove(flag, extra)
        else:
            usage("", 1)

    def bin_find(self):
        """Find installed packages
        """
        flag = []
        options = [
            "-f",
            "--find"
        ]
        additional_options = [
            "--case-ins",
            "--third-party"
        ]
        for add in additional_options:
            if add in self.args:
                flag.append(add)
                self.args.remove(add)
        packages = self.args[1:]
        if not packages:
            packages = [""]
        if len(self.args) == 1 and self.args[0] in options:
            PackageManager(packages).find(flag)
        elif len(self.args) > 1 and self.args[0] in options:
            PackageManager(packages).find(flag)
        else:
            usage("", 1)

    def pkg_desc(self):
        """Print slack-desc by repository
        """
        options = [
            "-p",
            "--desc"
        ]
        flag = ["--color="]
        colors = [
            "red",
            "green",
            "yellow",
            "cyan",
            "grey"
        ]
        tag = ""
        for arg in self.args:
            if arg.startswith(flag[0]):
                tag = arg[len(flag[0]):]
                self.args.remove(arg)
                break
        if tag and tag not in colors:
            raise SystemExit(f"\nslpkg: Error: Available colors {colors}\n")
        if (len(self.args) == 3 and self.args[0] in options and
                self.args[1] in self.meta.repositories and tag in colors):
            PkgDesc(self.args[2], self.args[1], tag).view()
        elif (len(self.args) == 3 and self.args[0] in options and
                self.args[1] in self.meta.repositories):
            PkgDesc(self.args[2], self.args[1], paint="").view()
        elif (len(self.args) > 1 and self.args[0] in options and
                self.args[1] not in self.meta.repositories):
            usage(self.args[1], 1)
        else:
            usage("", 1)

    def pkg_find(self):
        """Find packages from all enabled repositories
        """
        flag = []
        options = [
            "-F",
            "--FIND"
        ]
        additional_options = ["--case-ins"]
        for arg in self.args:
            if arg in additional_options:
                flag.append(arg)
                self.args.remove(arg)
        packages = self.args[1:]
        if len(self.args) > 1 and self.args[0] in options:
            FindFromRepos().find(packages, flag)
        else:
            usage("", 1)

    def pkg_contents(self):
        """Print packages contents
        """
        packages = self.args[1:]
        options = [
            "-d",
            "--display"
        ]
        if len(self.args) > 1 and self.args[0] in options:
            PackageManager(packages).display()
        else:
            usage("", 1)

    def congiguration(self):
        """Manage slpkg configuration file
        """
        options = [
            "-g",
            "--config"
        ]
        command = [
            "print",
            "edit",
            "reset"
        ]
        conf = Config()
        if (len(self.args) == 2 and self.args[0] in options and
                self.args[1] == command[1]):
            conf.edit()
        elif (len(self.args) == 2 and self.args[0] in options and
                self.args[1] == (command[0])):
            conf.view()
        elif (len(self.args) == 2 and self.args[0] in options and
                self.args[1] == (command[2])):
            conf.reset()
        else:
            usage("", 1)

    def auto_detect(self, args):
        """Check for already Slackware binary packages exist
        """
        suffixes = [
            ".tgz",
            ".txz",
            ".tbz",
            ".tlz"
        ]
        if (not args[0].startswith("-") and args[0] not in self.commands and
                args[0].endswith(tuple(suffixes))):
            packages, not_found = [], []
            for pkg in args:
                if pkg.endswith(tuple(suffixes)):
                    if os.path.isfile(pkg):
                        packages.append(pkg)
                    else:
                        not_found.append(pkg)
            if packages:
                AutoInstall(packages).select()
            if not_found:
                for ntf in not_found:
                    self.msg.pkg_not_found("", ntf, "Not installed", "")
            raise SystemExit(0)

    def if_checklist(self):
        try:
            from dialog import Dialog
        except ImportError:
            raise SystemExit("Require 'pythondialog': Install with 'slpkg "
                             "-s sbo python3-pythondialog'")


def main():

    args = sys.argv
    args.pop(0)

    argparse = ArgParse(args)

    if len(args) == 0:
        usage("", 1)

    argparse.auto_detect(args)

    if len(args) == 2 and args[0] == "update" and args[1] == "slpkg":
        args[0] = "update-slpkg"

    arguments = {
        "-h": argparse.help_version,
        "--help": argparse.help_version,
        "-v": argparse.help_version,
        "--version": argparse.help_version,
        "update": argparse.command_update,
        "upgrade": argparse.command_upgrade,
        "update-slpkg": argparse.command_update_slpkg,
        "repo-enable": argparse.command_repo_enable,
        "repo-list": argparse.command_repo_list,
        "repo-add": argparse.command_repo_add,
        "repo-remove": argparse.command_repo_remove,
        "repo-info": argparse.command_repo_info,
        "health": argparse.command_health,
        "deps-status": argparse.command_deps_status,
        "new-config": argparse.command_new_config,
        "clean-tmp": argparse.command_clean_tmp,
        "-a": argparse.auto_build,
        "--autobuild": argparse.auto_build,
        "-l": argparse.pkg_list,
        "--list": argparse.pkg_list,
        "-c": argparse.pkg_upgrade,
        "--check": argparse.pkg_upgrade,
        "-s": argparse.pkg_install,
        "--sync": argparse.pkg_install,
        "-t": argparse.pkg_tracking,
        "--tracking": argparse.pkg_tracking,
        "-n": argparse.sbo_network,
        "--netwotk": argparse.sbo_network,
        "-b": argparse.pkg_blacklist,
        "--blacklist": argparse.pkg_blacklist,
        "-q": argparse.pkg_queue,
        "--queue": argparse.pkg_queue,
        "-i": argparse.bin_install,
        "--installpkg": argparse.bin_install,
        "-u": argparse.bin_upgrade,
        "--upgradepkg": argparse.bin_upgrade,
        "-r": argparse.bin_remove,
        "--removepkg": argparse.bin_remove,
        "-f": argparse.bin_find,
        "--find": argparse.bin_find,
        "-F": argparse.pkg_find,
        "--FIND": argparse.pkg_find,
        "-p": argparse.pkg_desc,
        "--desc": argparse.pkg_desc,
        "-d": argparse.pkg_contents,
        "--display": argparse.pkg_contents,
        "-g": argparse.congiguration,
        "--config": argparse.congiguration
    }
    try:
        arguments[args[0]]()
    except KeyError:
        usage("", 1)


if __name__ == "__main__":
    main()
