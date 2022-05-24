#!/usr/bin/python3
# -*- coding: utf-8 -*-

# install.py file is part of slpkg.

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
from itertools import zip_longest
from pkg_resources import parse_version

from slpkg.utils import Utils
from slpkg.sizes import units
from slpkg.messages import Msg
from slpkg.checksum import check_md5
from slpkg.blacklist import BlackList
from slpkg.downloader import Download
from slpkg.log_deps import write_deps
from slpkg.grep_md5 import pkg_checksum
from slpkg.remove import delete_package
from slpkg.security import pkg_security
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package
from slpkg.pkg.manager import PackageManager
from slpkg.pkg.installed import GetFromInstalled

from slpkg.binary.greps import repo_data
from slpkg.binary.repo_init import RepoInit
from slpkg.binary.dependency import Dependencies


class BinaryInstall(BlackList, Utils):
    """Install binaries packages with all dependencies from
    repository
    """
    def __init__(self, packages, repo, flag):
        super().__init__()
        self.packages = packages
        pkg_security(packages)
        self.repo = repo
        self.flag = flag
        self.meta = _meta_
        self.green = _meta_.color["GREEN"]
        self.red = _meta_.color["RED"]
        self.grey = _meta_.color["GREY"]
        self.yellow = _meta_.color['YELLOW']
        self.endc = _meta_.color["ENDC"]
        self.msg = Msg()
        self.version = self.meta.slack_rel
        self.tmp_path = self.meta.slpkg_tmp_packages
        self.init_flags()
        self.dwn, self.dep_dwn = [], []
        self.install, self.dep_install = [], []
        self.comp_sum, self.dep_comp_sum = [], []
        self.uncomp_sum, self.dep_uncomp_sum = [], []
        self.dependencies = []
        self.deps_dict = {}
        self.answer = ""
        self.msg.reading()
        self.PACKAGES_TXT, self.mirror = RepoInit(self.repo).fetch()
        self.data = repo_data(self.PACKAGES_TXT, self.repo, self.flag)
        self.repo_pkg_names = []
        for name in self.data[0]:
            self.repo_pkg_names.append(split_package(name)[0])
        self.blacklist = list(self.get_black())
        self.matching = False

    def init_flags(self):
        """Flags initiliazation
        """
        for fl in self.flag:
            if fl.startswith("--directory-prefix="):
                self.tmp_path = fl.split("=")[1]
                if not self.tmp_path.endswith("/"):
                    self.tmp_path += "/"

    def start(self, is_upgrade):
        """
        Install packages from official Slackware distribution
        """
        self.case_insensitive()
        # fix if packages is for upgrade
        self.is_upgrade = is_upgrade
        mas_sum = dep_sum = sums = 0, 0, 0, 0
        self.msg.done()
        self.dependencies = self.resolving_deps()
        self.update_deps()
        (self.dep_dwn, self.dep_install, self.dep_comp_sum,
            self.dep_uncomp_sum) = self.store(self.dependencies)
        self.clear_masters()
        (self.dwn, self.install, self.comp_sum,
            self.uncomp_sum) = self.store(self.packages)
        if (self.meta.rsl_deps in ["on", "ON"] and
                "--resolve-off" not in self.flag):
            self.msg.done()
        if self.install:
            if self.matching and [""] != self.packages:
                self.msg.matching(self.packages)
            else:
                print("\nThe following packages will be automatically "
                      "installed or upgraded \nwith new version:\n")
            self.top_view()
            self.msg.upg_inst(self.is_upgrade)
            mas_sum = self.views(self.install, self.comp_sum)
            if self.dependencies:
                print("Installing for dependencies:")
                dep_sum = self.views(self.dep_install, self.dep_comp_sum)
            # sums[0] --> total packages
            # sums[1] --> reinstall
            # sums[2] --> upgraded
            # sums[3] --> uninstall
            sums = [sum(s) for s in zip_longest(mas_sum, dep_sum)]
            unit, size = units(self.comp_sum + self.dep_comp_sum,
                               self.uncomp_sum + self.dep_uncomp_sum)
            if self.matching and [""] != self.packages:
                print("\nMatching summary")
                print("=" * 79)
                raise SystemExit(f"Total {sums[0]} matching packages\n")
            print("\nInstalling summary")
            print("=" * 79)
            print(f"{self.grey}Total {sums[0]} {self.msg.pkg(sums[0])}.")
            print(f"{sums[3]} {self.msg.pkg(sums[3])} will be installed, "
                  f"{sums[2]} will be upgraded and "
                  f"{sums[1]} will be reinstalled.")
            print(f"Need to get {size[0]} {unit[0]} of archives.")
            print(f"After this process, {size[1]} {unit[1]} of additional "
                  f"disk space will be used.{self.endc}")
            print()
            self.if_all_installed()
            if self.msg.answer() in ["y", "Y"]:
                for inst, dwn in zip(self.dep_install + self.install,
                                     self.dep_dwn + self.dwn):
                    if (self.meta.not_downgrade == "on" and
                            self.not_downgrade(inst) is True):
                        continue
                    if (not os.path.isfile(self.meta.pkg_path + inst[:-4]) or
                            "--download-only" in self.flag or
                            "--reinstall" in self.flag):
                        Download(self.tmp_path, dwn.split(), self.repo).start()
                    else:
                        self.msg.template(78)
                        self.msg.pkg_found(inst)
                        self.msg.template(78)
                if "--download-only" in self.flag:
                    raise SystemExit()
                self.dep_install = list(self.check_downloaded(
                    self.tmp_path, self.dep_install))
                self.install = list(self.check_downloaded(
                    self.tmp_path, self.install))
                ins, upg = self.install_packages()
                self.msg.reference(ins, upg)
                write_deps(self.deps_dict)
                delete_package(self.tmp_path, self.dep_install + self.install)
        else:
            self.msg.not_found(self.is_upgrade)
            raise SystemExit(1)

    def if_all_installed(self):
        """Check if all packages is already installed
        """
        count_inst = 0
        for inst in (self.dep_install + self.install):
            if (os.path.isfile(self.meta.pkg_path + inst[:-4]) and
                    "--download-only" not in self.flag):
                count_inst += 1
        if (count_inst == len(self.dep_install + self.install) and
                "--reinstall" not in self.flag):
            raise SystemExit()

    def case_insensitive(self):
        """Matching packages distinguish between uppercase and
        lowercase
        """
        if "--case-ins" in self.flag:
            data = list(self.package_name(self.PACKAGES_TXT))
            data_dict = self.case_sensitive(data)
            for pkg in self.packages:
                index = self.packages.index(pkg)
                for key, value in data_dict.items():
                    if key == pkg.lower():
                        self.packages[index] = value

    def update_deps(self):
        """Update dependencies dictionary with all package
        """
        for dep in self.dependencies:
            deps = self.dimensional_list(Dependencies(
                self.repo, self.blacklist).binary(
                    dep, self.flag))
            self.deps_dict[dep] = deps

    def clear_masters(self):
        """Clear master packages if already exist in dependencies
        or if added to install two or more times
        """
        packages = []
        for mas in self.remove_dbs(self.packages):
            if mas not in self.dependencies:
                packages.append(mas)
        self.packages = packages

    def install_packages(self):
        """Install or upgrade packages
        """
        installs, upgraded = [], []
        for inst in (self.dep_install + self.install):
            package = (self.tmp_path + inst).split()
            pkg_ver = f"{split_package(inst)[0]}-{split_package(inst)[1]}"
            self.checksums(inst)
            if GetFromInstalled(split_package(inst)[0]).name():
                print(f"[ {self.yellow}upgrading{self.endc} ] --> {inst}")
                upgraded.append(pkg_ver)
                if "--reinstall" in self.flag:
                    PackageManager(package).upgrade("--reinstall")
                else:
                    PackageManager(package).upgrade("--install-new")
            else:
                print(f"[ {self.green}installing{self.endc} ] --> {inst}")
                installs.append(pkg_ver)
                PackageManager(package).upgrade("--install-new")
        return [installs, upgraded]

    def not_downgrade(self, package):
        """Don't downgrade packages if repository version is lower than
        installed"""
        name = split_package(package)[0]
        rep_ver = split_package(package)[1]
        ins_ver = GetFromInstalled(name).version()
        if not ins_ver:
            ins_ver = "0"
        if parse_version(rep_ver) < parse_version(ins_ver):
            self.msg.template(78)
            print(f"| Package {name} does not downgrade, setting by user")
            self.msg.template(78)
            return True

    def checksums(self, install):
        """Checksums before install
        """
        check_md5(pkg_checksum(install, self.repo), self.tmp_path + install)

    def resolving_deps(self):
        """Return package dependencies
        """
        requires = []
        if (self.meta.rsl_deps in ["on", "ON"] and
                self.flag != "--resolve-off"):
            self.msg.resolving()
        for dep in self.packages:
            dependencies = []
            dependencies = self.dimensional_list(Dependencies(
                self.repo, self.blacklist).binary(dep, self.flag))
            requires += list(self._fix_deps_repos(dependencies))
            self.deps_dict[dep] = self.remove_dbs(requires)
        return self.remove_dbs(requires)

    def _fix_deps_repos(self, dependencies):
        """Fix store deps include in repository
        """
        for dep in dependencies:
            if dep in self.repo_pkg_names:
                yield dep

    def views(self, install, comp_sum):
        """Views packages
        """
        pkg_sum = uni_sum = upg_sum = res_sum = 0

        # fix repositories align
        repo = self.repo + (" " * (6 - (len(self.repo))))
        for pkg, comp in zip(install, comp_sum):
            pkg_sum += 1
            pkg_repo = split_package(pkg[:-4])
            if find_package(pkg[:-4], self.meta.pkg_path):
                if "--reinstall" in self.flag:
                    res_sum += 1
                COLOR = self.meta.color["GREEN"]
            elif pkg_repo[0] == GetFromInstalled(pkg_repo[0]).name():
                COLOR = self.meta.color["YELLOW"]
                upg_sum += 1
            else:
                COLOR = self.meta.color["RED"]
                uni_sum += 1
            ver = GetFromInstalled(pkg_repo[0]).version()
            if ver:
                ver = f"-{ver}"
            print(f"  {COLOR}{pkg_repo[0] + ver}{self.endc}"
                  f"{' ' * (23-len(pkg_repo[0] + ver))} {pkg_repo[1]}"
                  f"{' ' * (18-len(pkg_repo[1]))} {pkg_repo[2]}"
                  f"{' ' * (8-len(pkg_repo[2]))}{pkg_repo[3]}"
                  f"{' ' * (7-len(pkg_repo[3]))}{repo}{comp:>11}{' K'}")
        return [pkg_sum, res_sum, upg_sum, uni_sum]

    def top_view(self):
        """Print packages status bar
        """
        self.msg.template(78)
        print(f"| Package{' ' * 17}New Version{' ' * 8}Arch{' ' * 4}"
              f"Build{' ' * 2}Repos{' ' * 10}Size")
        self.msg.template(78)

    def store(self, packages):
        """Store and return packages for install
        """
        dwn, install, comp_sum, uncomp_sum = ([] for i in range(4))
        # name = data[0]
        # location = data[1]
        # size = data[2]
        # unsize = data[3]
        for pkg in packages:
            for pk, loc, comp, uncomp in zip(self.data[0], self.data[1],
                                             self.data[2], self.data[3]):
                if (pk and pkg == split_package(pk)[0] and
                        pk not in install and
                        split_package(pk)[0] not in self.blacklist):
                    dwn.append(f"{self.mirror}{loc}/{pk}")
                    install.append(pk)
                    comp_sum.append(comp)
                    uncomp_sum.append(uncomp)

        if not install:
            for pkg in packages:
                for pk, loc, comp, uncomp in zip(self.data[0], self.data[1],
                                                 self.data[2], self.data[3]):
                    name = split_package(pk)[0]
                    if (pk and pkg in name and name not in self.blacklist):
                        self.matching = True
                        dwn.append(f"{self.mirror}{loc}/{pk}")
                        install.append(pk)
                        comp_sum.append(comp)
                        uncomp_sum.append(uncomp)
        dwn.reverse()
        install.reverse()
        comp_sum.reverse()
        uncomp_sum.reverse()

        return [dwn, install, comp_sum, uncomp_sum]
