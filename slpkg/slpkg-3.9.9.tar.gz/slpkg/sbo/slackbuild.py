#!/usr/bin/python3
# -*- coding: utf-8 -*-

# slackbuild.py file is part of slpkg.

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
from pkg_resources import parse_version

from slpkg.utils import Utils
from slpkg.messages import Msg
from slpkg.log_deps import write_deps
from slpkg.blacklist import BlackList
from slpkg.downloader import Download
from slpkg.remove import delete_folder
from slpkg.security import pkg_security
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package
from slpkg.pkg.build import BuildPackage
from slpkg.pkg.manager import PackageManager
from slpkg.pkg.installed import GetFromInstalled

from slpkg.sbo.greps import SBoGrep
from slpkg.sbo.sbo_arch import SBoArch
from slpkg.sbo.compressed import SBoLink
from slpkg.sbo.dependency import Requires
from slpkg.sbo.search import sbo_search_pkg
from slpkg.sbo.slack_find import slack_package


class SBoInstall(BlackList, Utils):
    """Build and install SBo packages with all dependencies
    """
    def __init__(self, slackbuilds, flag):
        super().__init__()
        self.slackbuilds = slackbuilds
        pkg_security(self.slackbuilds)
        self.flag = flag
        self.meta = _meta_
        self.green = _meta_.color["GREEN"]
        self.red = _meta_.color["RED"]
        self.yellow = _meta_.color["YELLOW"]
        self.grey = _meta_.color["GREY"]
        self.endc = _meta_.color["ENDC"]
        self.msg = Msg()
        self.arch = SBoArch().get()
        self.build_folder = self.meta.build_path
        self._SOURCES = self.meta.SBo_SOURCES
        self.init_flags()
        self.unst = ["UNSUPPORTED", "UNTESTED"]
        self.master_packages = []
        self.deps = []
        self.dependencies = []
        self.package_not_found = []
        self.package_found = []
        self.deps_dict = {}
        self.answer = ""
        self.match = False
        self.count_ins = 0
        self.count_upg = 0
        self.count_uni = 0
        self.msg.reading()
        self.data = SBoGrep(name="").names()
        self.blacklist = list(self.get_black())

    def init_flags(self):
        """Flags initialization
        """
        for fl in self.flag:
            if fl.startswith("--directory-prefix="):
                self.build_folder = fl.split("=")[1]
                if not self.build_folder.endswith("/"):
                    self.build_folder += "/"

    def start(self, is_upgrade):
        """Start view, build and install SBo packages
        """
        tagc = ""
        self.is_upgrade = is_upgrade
        self.case_insensitive()
        for _sbo in self.slackbuilds:
            if _sbo in self.data and _sbo not in self.blacklist:
                sbo_deps = Requires(self.flag).sbo(_sbo)
                self.deps += sbo_deps
                self.deps_dict[_sbo] = self.one_for_all(sbo_deps)
                self.package_found.append(_sbo)
            else:
                self.package_not_found.append(_sbo)
        self.update_deps()

        if not self.package_found:
            self.match = True
            self.matching()

        self.master_packages, mas_src = self.sbo_version_source(
            self.package_found)
        self.msg.done()
        if (self.meta.rsl_deps in ["on", "ON"] and
                self.flag != "--resolve-off" and not self.match):
            self.msg.resolving()
        self.dependencies, dep_src = self.sbo_version_source(
            self.one_for_all(self.deps))
        if (self.meta.rsl_deps in ["on", "ON"] and
                self.flag != "--resolve-off" and not self.match):
            self.msg.done()
        self.clear_masters()

        if self.package_found:
            if self.match and [""] != self.slackbuilds:
                self.msg.matching(self.slackbuilds)
            else:
                print("\nThe following packages will be automatically "
                      "installed or upgraded \nwith new version:\n")
            self.top_view()
            self.msg.upg_inst(self.is_upgrade)

            # view master packages
            for sbo, arch in zip(self.master_packages, mas_src):
                tagc = self.tag(sbo)
                name = "-".join(sbo.split("-")[:-1])
                self.view_packages(tagc, name, sbo.split("-")[-1],
                                   self.select_arch(arch))
            self.view_installing_for_deps()

            # view dependencies
            for dep, arch in zip(self.dependencies, dep_src):
                tagc = self.tag(dep)
                name = "-".join(dep.split("-")[:-1])
                self.view_packages(tagc, name, dep.split("-")[-1],
                                   self.select_arch(arch))

            count_total = sum([self.count_ins, self.count_upg,
                               self.count_uni])
            if self.match and [""] != self.slackbuilds:
                print("\nMatching summary")
                print("=" * 79)
                raise SystemExit(f"Total {count_total} matching packages\n")
            print("\nInstalling summary")
            print("=" * 79)
            print(f"{self.grey}Total {count_total} "
                  f"{self.msg.pkg(count_total)}.")
            print(f"{self.count_uni} {self.msg.pkg(self.count_uni)} "
                  f"will be installed, "
                  f"{self.count_ins} already installed and "
                  f"{self.count_upg} {self.msg.pkg(self.count_upg)}")
            print(f"will be upgraded.{self.endc}\n")
            self.continue_to_install()
        else:
            self.msg.not_found(self.is_upgrade)
            raise SystemExit()

    def case_insensitive(self):
        """Matching packages distinguish between uppercase and
        lowercase
        """
        if "--case-ins" in self.flag:
            data_dict = self.case_sensitive(self.data)
            for name in self.slackbuilds:
                index = self.slackbuilds.index(name)
                for key, value in data_dict.items():
                    if key == name.lower():
                        self.slackbuilds[index] = value

    def update_deps(self):
        """Update dependencies dictionary with all package
        """
        onelist, dependencies = [], []
        onelist = self.dimensional_list(self.deps)
        dependencies = self.remove_dbs(onelist)
        for dep in dependencies:
            deps = Requires(self.flag).sbo(dep)
            self.deps_dict[dep] = self.one_for_all(deps)

    def continue_to_install(self):
        """Continue to install ?
        """
        if (self.count_uni > 0 or self.count_upg > 0 or
                "--download-only" in self.flag or "--rebuild" in self.flag):
            if self.master_packages and self.msg.answer() in ["y", "Y"]:
                installs, upgraded = self.build_install()
                if "--download-only" in self.flag:
                    raise SystemExit()
                self.msg.reference(installs, upgraded)
                write_deps(self.deps_dict)
                delete_folder(self.build_folder)

    def view_installing_for_deps(self):
        """View installing message for dependencies
        """
        if not self.match and self.dependencies:
            print("Installing for dependencies:")

    def clear_masters(self):
        """Clear master slackbuilds if already exist in dependencies
        or if added to install two or more times
        """
        self.master_packages = self.remove_dbs(self.master_packages)
        for mas in self.master_packages:
            if mas in self.dependencies:
                self.master_packages.remove(mas)

    def matching(self):
        """Return found matching SBo packages
        """
        for sbo in self.package_not_found:
            for pkg in self.data:
                if sbo in pkg and pkg not in self.blacklist:
                    self.package_found.append(pkg)

    def sbo_version_source(self, slackbuilds):
        """Create sbo name with version
        """
        sbo_versions, sources = [], []
        for sbo in slackbuilds:
            sbo_ver = f"{sbo}-{SBoGrep(sbo).version()}"
            sbo_versions.append(sbo_ver)
            sources.append(SBoGrep(sbo).source())
        return [sbo_versions, sources]

    def one_for_all(self, deps):
        """Because there are dependencies that depend on other
        dependencies are created lists into other lists.
        Thus creating this loop create one-dimensional list and
        remove double packages from dependencies.
        """
        requires, dependencies = [], []
        deps.reverse()
        # Inverting the list brings the
        # dependencies in order to be installed.
        requires = self.dimensional_list(deps)
        dependencies = self.remove_dbs(requires)
        return dependencies

    def top_view(self):
        """View top template
        """
        self.msg.template(78)
        print(f"| Packages{' ' * 16}"
              f"New version{' ' * 8}"
              f"Arch{' ' * 4}"
              f"Build{' ' * 2}"
              f"Repos{' ' * 10}"
              f"Size")
        self.msg.template(78)

    def view_packages(self, *args):
        """:View slackbuild packages with version and arch
        args[0] package color
        args[1] package
        args[2] version
        args[3] arch
        """
        ver = GetFromInstalled(args[1]).version()
        if ver:
            ver = f"-{ver}"
        print(f" {args[0]}{args[1] + ver} {self.endc}"
              f"{' ' * (24-len(args[1] + ver))}{args[2]}"
              f"{' ' * (18-len(args[2]))} {args[3]}"
              f"{' ' * (15-len(args[3]))}{''}"
              f"{''}SBo{''}{'':>11}{''}")

    def tag(self, sbo):
        """Tag with color green if package already installed,
        color yellow for packages to upgrade and color red
        if not installed.
        """
        # split sbo name with version and get name
        sbo_name = "-".join(sbo.split("-")[:-1])
        find = GetFromInstalled(sbo_name).name()
        if find_package(sbo, self.meta.pkg_path):
            paint = self.meta.color["GREEN"]
            self.count_ins += 1
            if "--rebuild" in self.flag:
                self.count_upg += 1
        elif sbo_name == find:
            paint = self.meta.color["YELLOW"]
            self.count_upg += 1
        else:
            paint = self.meta.color["RED"]
            self.count_uni += 1
        return paint

    def select_arch(self, src):
        """Looks if sources unsupported or untested
        from arch else select arch.
        """
        arch = self.arch
        for item in self.unst:
            if item in src:
                arch = item
        return arch

    def filenames(self, sources):
        """Return filenames from sources links
        """
        for src in sources:
            yield src.split("/")[-1]

    def build_install(self):
        """Build and install packages if not already installed
        """
        slackbuilds = self.dependencies + self.master_packages
        installs, upgraded, = [], []
        if not os.path.exists(self.build_folder):
            os.makedirs(self.build_folder)
        if not os.path.exists(self._SOURCES):
            os.makedirs(self._SOURCES)
        os.chdir(self.build_folder)
        for prgnam in slackbuilds:
            if (self.meta.not_downgrade == "on" and
                    self.not_downgrade(prgnam) is True):
                continue
            pkg = "-".join(prgnam.split("-")[:-1])
            installed = "".join(find_package(prgnam, self.meta.pkg_path))
            src_link = SBoGrep(pkg).source().split()
            if (installed and "--download-only" not in self.flag and
                    "--rebuild" not in self.flag):
                self.msg.template(78)
                self.msg.pkg_found(prgnam)
                self.msg.template(78)
            elif self.unst[0] in src_link or self.unst[1] in src_link:
                self.msg.template(78)
                print(f"| Package {prgnam} {self.red}"
                      f"{''.join(src_link)}{self.endc}")
                self.msg.template(78)
            else:
                sbo_url = sbo_search_pkg(pkg)
                sbo_link = SBoLink(sbo_url).tar_gz()
                script = sbo_link.split("/")[-1]
                if self.meta.sbosrcarch in ["on", "ON"]:
                    src_link = list(self.sbosrcarsh(prgnam, sbo_link,
                                                    src_link))
                Download(self.build_folder, sbo_link.split(),
                         repo="sbo").start()
                Download(self._SOURCES, src_link, repo="sbo").start()
                if "--download-only" in self.flag:
                    continue
                sources = list(self.filenames(src_link))
                BuildPackage(script, sources, self.build_folder,
                             auto=False).build()
                binary = slack_package(prgnam)
                if os.path.isfile("".join(binary)):
                    if GetFromInstalled(pkg).name() == pkg:
                        print(f"[ {self.yellow}Upgrading{self.endc} ] --> "
                              f"{prgnam}")
                        upgraded.append(prgnam)
                    else:
                        print(f"[ {self.green}Installing{self.endc} ] --> "
                              f"{prgnam}")
                        installs.append(prgnam)
                    if ("--rebuild" in self.flag and
                            GetFromInstalled(pkg).name() == pkg):
                        PackageManager(binary).upgrade(flag="--reinstall")
                    else:
                        PackageManager(binary).upgrade(flag="--install-new")
        return installs, upgraded

    def not_downgrade(self, prgnam):
        """Don't downgrade packages if sbo version is lower than
        installed"""
        name = "-".join(prgnam.split("-")[:-1])
        sbo_ver = prgnam.split("-")[-1]
        ins_ver = GetFromInstalled(name).version()
        if not ins_ver:
            ins_ver = "0"
        if parse_version(sbo_ver) < parse_version(ins_ver):
            self.msg.template(78)
            print(f"| Package {name} does not downgrade, "
                  f"setting by user")
            self.msg.template(78)
            return True

    def sbosrcarsh(self, prgnam, sbo_link, src_link):
        """Alternative repository for sbo sources"""
        name = "-".join(prgnam.split("-")[:-1])
        category = f"{sbo_link.split('/')[-2]}/{name}/"
        for link in src_link:
            source = link.split("/")[-1]
            yield f"{self.meta.sbosrcarch_link}{category}{source}"
