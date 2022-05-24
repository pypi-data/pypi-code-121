#!/usr/bin/python3
# -*- coding: utf-8 -*-

# patches.py file is part of slpkg.

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
import shutil
import subprocess
from pkg_resources import parse_version


from slpkg.init import Update
from slpkg.utils import Utils
from slpkg.sizes import units
from slpkg.messages import Msg
from slpkg.url_read import URL
from slpkg.checksum import check_md5
from slpkg.blacklist import BlackList
from slpkg.downloader import Download
from slpkg.remove import delete_package
from slpkg.grep_md5 import pkg_checksum
from slpkg.dialog_box import DialogUtil
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package
from slpkg.pkg.manager import PackageManager
from slpkg.pkg.installed import GetFromInstalled

from slpkg.binary.greps import repo_data

from slpkg.slack.mirrors import mirrors
from slpkg.slack.slack_version import slack_ver


class Patches(BlackList, Utils):
    """Upgrade distribution from official Slackware mirrors
    """
    def __init__(self, skip, flag):
        super().__init__()
        self.skip = skip
        self.flag = flag
        self.meta = _meta_
        self.grey = _meta_.color["GREY"]
        self.yellow = _meta_.color["YELLOW"]
        self.green = _meta_.color["GREEN"]
        self.red = _meta_.color["RED"]
        self.endc = _meta_.color["ENDC"]
        self.msg = Msg()
        self.version = self.meta.slack_rel
        self.patch_path = self.meta.slpkg_tmp_patches
        self.count_added = 0
        self.count_upg = 0
        self.pkg_for_upgrade = []
        self.dwn_links = []
        self.upgrade_all = []
        self.upgraded = []
        self.installed = []
        self.comp_sum = []
        self.uncomp_sum = []
        self.msg.checking()
        if self.version == "stable":
            self.PACKAGES_TXT = URL(mirrors("PACKAGES.TXT",
                                            "patches/")).get_request()
        else:
            self.PACKAGES_TXT = URL(mirrors("PACKAGES.TXT", "")).get_request()

    def start(self):
        """Install new patches from official Slackware mirrors
        """
        self.store()
        self.msg.done()
        if self.upgrade_all:
            if "--checklist" in self.flag:
                self.dialog_checklist()
            print("\nThese packages need upgrading:\n")
            self.msg.template(78)
            print(f"| Package{' ' * 17}New Version{' ' * 8}Arch"
                  f"{' ' * 4}Build{' ' * 2}Repo{' ' * 11}Size")
            self.msg.template(78)
            print("Upgrading:")
            self.views()
            unit, size = units(self.comp_sum, self.uncomp_sum)
            print("\nInstalling summary")
            print("=" * 79)
            print(f"{self.grey}Total {self.count_upg} "
                  f"{self.msg.pkg(len(self.upgrade_all))} will be upgraded and"
                  f" {self.count_added} will be installed.")
            print(f"Need to get {size[0]} {unit[0]} of archives.")
            print(f"After this process, {size[1]} {unit[1]} of additional disk"
                  f" space will be used.{self.endc}")
            print()
            if self.msg.answer() in ["y", "Y"]:
                Download(self.patch_path, self.dwn_links,
                         repo="slack").start()
                self.upgrade_all = list(self.check_downloaded(
                    self.patch_path, self.upgrade_all))
                self.upgrade()
                self.kernel()
                if self.meta.slackpkg_log in ["on", "ON"]:
                    # update the slackpkg ChanheLog.txt file
                    self.slackpkg_update()
                self.msg.reference(self.installed, self.upgraded)
                # delete the downloaded packages
                delete_package(self.patch_path, self.upgrade_all)
                # update the packages lists
                self.update_lists()
        else:
            slack_arch = ""
            if self.meta.arch == "x86_64":
                slack_arch = "64"
            print(f"\nSlackware{slack_arch} '{self.version}' v{slack_ver()}"
                  f" distribution is up to date!\n")

    def store(self):
        """Store and return packages for upgrading
        """
        data = repo_data(self.PACKAGES_TXT, "slack", self.flag)
        black = list(self.get_black())
        for name, loc, comp, uncomp in zip(data[0], data[1], data[2], data[3]):
            repo_pkg_name = split_package(name)[0]
            if self.meta.only_installed in ["on", "ON"]:
                pkg_name = split_package(name)[0]
                pkg_ver = split_package(name)[1]
                if (GetFromInstalled(pkg_name).name() and
                        repo_pkg_name not in black and
                        repo_pkg_name not in self.skip and
                        parse_version(pkg_ver) > parse_version(
                            GetFromInstalled(pkg_name).version())):
                    self.dwn_links.append(f"{mirrors('', '')}{loc}/{name}")
                    self.comp_sum.append(comp)
                    self.uncomp_sum.append(uncomp)
                    self.upgrade_all.append(name)
                    self.count_upg += 1
                    if not find_package(f"{repo_pkg_name}-",
                                        self.meta.pkg_path):
                        self.count_added += 1
                        self.count_upg -= 1
            elif (not os.path.isfile(self.meta.pkg_path + name[:-4]) and
                    repo_pkg_name not in black and
                    repo_pkg_name not in self.skip):
                self.dwn_links.append(f"{mirrors('', '')}{loc}/{name}")
                self.comp_sum.append(comp)
                self.uncomp_sum.append(uncomp)
                self.upgrade_all.append(name)
                self.count_upg += 1
                if not find_package(f"{repo_pkg_name}-", self.meta.pkg_path):
                    self.count_added += 1
                    self.count_upg -= 1
        return self.count_upg

    def dialog_checklist(self):
        """Create checklist to choose packages for upgrade
        """
        data = []
        for upg in self.upgrade_all:
            data.append(upg[:-4])
        text = "Press 'spacebar' to unchoose packages from upgrade"
        title = " Upgrade "
        status = True
        backtitle = f"{self.meta.__all__} {self.meta.__version__}"
        pkgs = DialogUtil(data, text, title, backtitle,
                          status).checklist()
        index = 0
        for pkg, comp, uncomp in zip(self.upgrade_all, self.comp_sum,
                                     self.uncomp_sum):
            if pkg[:-4] not in pkgs:
                self.dwn_links.pop(index)
                self.upgrade_all.pop(index)
                self.comp_sum.pop(index)
                self.uncomp_sum.pop(index)
                self.count_upg -= 1
                del comp, uncomp
                index -= 1
            index += 1
        if not self.upgrade_all:
            raise SystemExit()

    def views(self):
        """Views packages
        """
        for upg, size in sorted(zip(self.upgrade_all, self.comp_sum)):
            pkg_repo = split_package(upg[:-4])
            color = self.red
            pkg_inst = GetFromInstalled(pkg_repo[0]).name()
            if pkg_repo[0] == pkg_inst:
                color = self.yellow
            ver = GetFromInstalled(pkg_repo[0]).version()
            if ver:
                ver = f"-{ver}"
            print(f"  {color}{pkg_repo[0] + ver}{self.endc}"
                  f"{' ' * (23-len(pkg_repo[0] + ver))} {pkg_repo[1]}"
                  f"{' ' * (18-len(pkg_repo[1]))} {pkg_repo[2]}"
                  f"{' ' * (8-len(pkg_repo[2]))}{pkg_repo[3]}"
                  f"{' ' * (7-len(pkg_repo[3]))}Slack{size:>12} K")

    def upgrade(self):
        """Upgrade packages
        """
        for pkg in self.upgrade_all:
            check_md5(pkg_checksum(pkg, "slack_patches"),
                      self.patch_path + pkg)
            pkg_ver = f"{split_package(pkg)[0]}-{split_package(pkg)[1]}"
            if find_package(f"{split_package(pkg)[0]}-",
                            self.meta.pkg_path):
                print(f"[ {self.yellow}upgrading{self.endc} ] --> {pkg[:-4]}")
                PackageManager((self.patch_path + pkg).split()).upgrade(
                    "--install-new")
                self.upgraded.append(pkg_ver)
            else:
                print(f"[ {self.green}installing{self.endc} ] --> {pkg[:-4]}")
                PackageManager((self.patch_path + pkg).split()).upgrade(
                    "--install-new")
                self.installed.append(pkg_ver)

    def kernel(self):
        """Check if kernel upgraded if true
        then reinstall "lilo"
        """
        for core in self.upgrade_all:
            if "kernel" in core:
                if self.meta.default_answer in ["y", "Y"]:
                    answer = self.meta.default_answer
                else:
                    print()
                    self.msg.template(78)
                    print(f"| {self.red}*** HIGHLY recommended reinstall "
                          f"boot loader ***{self.endc}")
                    print("| L=lilo / E=elilo / G=grub")
                    self.msg.template(78)
                    try:
                        answer = input("\nThe kernel has been upgraded, "
                                       "reinstall boot loader [L/E/G]? ")
                    except EOFError:
                        raise SystemExit("\n")
                if answer in ["L"]:
                    subprocess.call("lilo", shell=True)
                    break
                elif answer in ["E"]:
                    subprocess.call("eliloconfig", shell=True)
                    break
                elif answer in ["G"]:
                    subprocess.call("grub-mkconfig -o /boot/grub/grub.cfg",
                                    shell=True)
                    break

    def slackpkg_update(self):
        """This replace slackpkg ChangeLog.txt file with new
        from Slackware official mirrors after update distribution.
        """
        NEW_ChangeLog_txt = URL(mirrors("ChangeLog.txt", "")).get_request()
        if os.path.isfile(f"{self.meta.slackpkg_lib_path}ChangeLog.txt.old"):
            os.remove(f"{self.meta.slackpkg_lib_path}ChangeLog.txt.old")
        if os.path.isfile(f"{self.meta.slackpkg_lib_path}ChangeLog.txt"):
            shutil.copy2(f"{self.meta.slackpkg_lib_path}ChangeLog.txt",
                         f"{self.meta.slackpkg_lib_path}ChangeLog.txt.old")
            os.remove(f"{self.meta.slackpkg_lib_path}ChangeLog.txt")
        with open(f"{self.meta.slackpkg_lib_path}ChangeLog.txt", "w") as log:
            log.write(NEW_ChangeLog_txt)

    def update_lists(self):
        """Update packages list and ChangeLog.txt file after
        upgrade distribution
        """
        print(f"{self.green}Update the package lists ?{self.endc}")
        print("=" * 79)
        if self.msg.answer() in ["y", "Y"]:
            Update().run(["slack"])
