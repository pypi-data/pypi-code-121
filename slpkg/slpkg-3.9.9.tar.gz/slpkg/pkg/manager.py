#!/usr/bin/python3
# -*- coding: utf-8 -*-

# manager.py file is part of slpkg.

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
import re
import subprocess


from slpkg.pkg.find import find_package
from slpkg.pkg.installed import GetFromInstalled

from slpkg.utils import Utils
from slpkg.messages import Msg
from slpkg.dialog_box import DialogUtil
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.slack.slackware_repo import slackware_repository


class PackageManager(Utils):
    """Package manager class for install, upgrade,
    reinstall, remove, find and display packages"""
    def __init__(self, binary):
        self.binary = binary
        self.meta = _meta_
        self.green = _meta_.color["GREEN"]
        self.red = _meta_.color["RED"]
        self.yellow = _meta_.color["YELLOW"]
        self.cyan = _meta_.color["CYAN"]
        self.grey = _meta_.color["GREY"]
        self.endc = _meta_.color["ENDC"]
        self.msg = Msg()
        self.skip = []
        self.size = 0
        self.file_size = 0
        self.unit = "Kb"

    def install(self, flag):
        """Install Slackware binary packages
        """
        for pkg in self.binary:
            try:
                subprocess.call(f"installpkg {flag} {pkg}", shell=True)
                check = pkg[:-4].split("/")[-1]
                if os.path.isfile(self.meta.pkg_path + check):
                    print("Completed!\n")
                else:
                    raise SystemExit(1)
            except subprocess.CalledProcessError:
                self._not_found("Can't install", self.binary, pkg)
                raise SystemExit(1)

    def upgrade(self, flag):
        """Upgrade Slackware binary packages with new
        """
        for pkg in self.binary:
            try:
                subprocess.call(f"upgradepkg {flag} {pkg}", shell=True)
                check = pkg[:-4].split("/")[-1]
                if os.path.isfile(self.meta.pkg_path + check):
                    print("Completed!\n")
                else:
                    raise SystemExit(1)
            except subprocess.CalledProcessError:
                self._not_found("Can't upgrade", self.binary, pkg)
                raise SystemExit(1)

    def _not_found(self, message, binary, pkg):
        if len(binary) > 1:
            bol = eol = ""
        else:
            bol = eol = "\n"
        self.msg.pkg_not_found(bol, pkg, message, eol)

    def remove(self, flag, extra):
        """Remove Slackware binary packages
        """
        self.flag = flag
        self.extra = extra
        self.dep_path = self.meta.log_path + "dep/"
        dependencies, rmv_list = [], []
        self.removed = self._view_removed()
        if not self.removed:
            print()   # new line at end
        else:
            msg = "package"
            if len(self.removed) > 1:
                msg = msg + "s"
            try:
                if self.meta.default_answer in ["y", "Y"]:
                    remove_pkg = self.meta.default_answer
                else:
                    remove_pkg = input(
                        "\nAre you sure to remove {0} {1} [y/N]? ".format(
                            str(len(self.removed)), msg))
            except EOFError:
                raise SystemExit(1)
            if remove_pkg in ["y", "Y"]:
                self._check_if_used(self.binary)
                for rmv in self.removed:
                    '''
                    If package build and install with "slpkg -s sbo <package>"
                    then look log file for dependencies in /var/log/slpkg/dep,
                    read and remove all else remove only the package.
                    '''
                    if (os.path.isfile(self.dep_path + rmv) and
                            self.meta.del_deps in ["on", "ON"] or
                            os.path.isfile(self.dep_path + rmv) and
                            "--deps" in self.extra):
                        dependencies = self._view_deps(self.dep_path, rmv)
                        if dependencies and self._rmv_deps_answer() in ["y",
                                                                        "Y"]:
                            rmv_list += self._rmv_deps(dependencies, rmv)
                        else:
                            rmv_list += self._rmv_pkg(rmv)
                    else:
                        rmv_list += self._rmv_pkg(rmv)
                # Prints all removed packages
                self._reference_rmvs(rmv_list)

    def _rmv_deps_answer(self):
        """Remove dependencies answer
        """
        if self.meta.remove_deps_answer in ["y", "Y"]:
            remove_dep = self.meta.remove_deps_answer
        else:
            try:
                remove_dep = input(
                    "\nRemove dependencies (maybe used by "
                    "other packages) [y/N]? ")
                print()
            except EOFError:
                raise SystemExit("\n")
        return remove_dep

    def _get_removed(self):
        """Manage removed packages by extra options
        """
        extra = self.extra
        removed, packages, pkg = [], [], ""
        if "--tag" in extra:
            for pkg in find_package("", self.meta.pkg_path):
                for tag in self.binary:
                    if pkg.endswith(tag):
                        removed.append(split_package(pkg)[0])
                        packages.append(pkg)
            pkg = ""
            extra = ""
        elif "--third-party" in extra:
            slack_packages, slack_names = slackware_repository()
            slpkg_pkg = self.meta.__all__ + "-" + self.meta.__version__
            binary = self.binary
            for pkg in find_package("", self.meta.pkg_path):
                slack_name = split_package(pkg)[0]
                for tag in binary:
                    if (slack_name not in slack_names and
                            slpkg_pkg not in pkg and tag in pkg):
                        removed.append(split_package(pkg)[0])
                        packages.append(pkg)
            pkg = ""
            extra = ""
        else:
            for pkg in self.binary:
                name = GetFromInstalled(pkg).name()
                ver = GetFromInstalled(pkg).version()
                package = find_package(f"{name}-{ver}-", self.meta.pkg_path)
                if pkg and name == pkg:
                    removed.append(pkg)
                    packages.append(package[0])
        if not removed:
            self.msg.pkg_not_found("", pkg, "Can't remove", "\n")
            raise SystemExit(1)
        return removed, packages

    def _view_removed(self):
        """View packages before removed
        """
        print("Packages with name matching [ {0}{1}{2} ]\n".format(
            self.cyan, ", ".join(self.binary), self.endc))
        removed, packages = self._get_removed()
        if packages and "--checklist" in self.extra:
            removed = []
            text = "Press 'spacebar' to unchoose packages from the remove"
            backtitle = f"{self.meta.__all__} {self.meta.__version__}"
            status = True
            pkgs = DialogUtil(packages, text, " Remove ", backtitle,
                              status).checklist()
            if pkgs:
                for rmv in pkgs:
                    removed.append(split_package(rmv)[0])
                self.meta.default_answer = "y"
        else:
            for rmv, pkg in zip(removed, packages):
                self._sizes(pkg)
                print(f"[ {self.red}delete{self.endc} ] --> "
                      f"[ {self.file_size} ] - {pkg}")
            self._calc_sizes()
            self._remove_summary()
        if "--third-party" in self.extra:
            print()
            self.msg.template(78)
            print(f"| {' ' * 27}{self.red}*** WARNING ***{self.endc}")
            print("| Before you use third-party option, be sure you have"
                  " updated the packages \n| lists. Run the command"
                  " 'slpkg update' and 'slpkg -c slack --upgrade'")
            self.msg.template(78)
        return removed

    def _calc_sizes(self):
        """Package size calculation
        """
        if self.size > 1024:
            self.unit = "Mb"
            self.size = (self.size / 1024)
        if self.size > 1024:
            self.unit = "Gb"
            self.size = (self.size / 1024)

    def _remove_summary(self):
        """Removed packge size summary
        """
        if self.size > 0:
            print("\nRemoved summary")
            print("=" * 79)
            print("{0}Size of removed packages {1} {2}.{3}".format(
                self.grey, round(self.size, 2), self.unit, self.endc))

    def _view_deps(self, path, package):
        """View dependencies before remove
        """
        self.size = 0
        packages = []
        dependencies = (self.read_file(path + package)).splitlines()
        for dep in dependencies:
            if GetFromInstalled(dep).name():
                ver = GetFromInstalled(dep).version()
                packages.append(f"{dep}-{ver}")
            else:
                dependencies.remove(dep)
        if packages:
            if "--checklist" in self.extra:
                deps, dependencies = [], []
                text = "Found dependencies for the package {0}".format(package)
                backtitle = f"{self.meta.__all__} {self.meta.__version__}"
                status = True
                deps = DialogUtil(packages, text, " Remove ", backtitle,
                                  status).checklist()
                for d in deps:
                    dependencies.append("-".join(d.split("-")[:-1]))
                self.meta.remove_deps_answer = "y"
            else:
                print()   # new line at start
                self.msg.template(78)
                print(f"| Found dependencies for the package {package}:")
                self.msg.template(78)
                for pkg in packages:
                    find = find_package(f"{pkg}-", self.meta.pkg_path)
                    self._sizes(find[0])
                    print(f"| {self.red}{pkg}{self.endc}")
                self.msg.template(78)
                self._calc_sizes()
                print("| {0}Size of removed dependencies {1} {2}{3}".format(
                    self.grey, round(self.size, 2), self.unit, self.endc))
                self.msg.template(78)
        return dependencies

    def _removepkg(self, package):
        """removepkg Slackware command
        """
        try:
            subprocess.call(f"removepkg {self.flag} {package}", shell=True)
            if os.path.isfile(self.dep_path + package):
                os.remove(self.dep_path + package)  # remove log
        except subprocess.CalledProcessError as er:
            raise SystemExit(er)

    def _rmv_deps(self, dependencies, package):
        """Remove dependencies
        """
        removes = []
        dependencies.append(package)
        self._check_if_used(dependencies)
        for dep in dependencies:
            if dep not in self.skip and GetFromInstalled(dep).name():
                ver = GetFromInstalled(dep).version()
                removes.append(f"{dep}-{ver}")
                self._removepkg(dep)
        return removes

    def _rmv_pkg(self, package):
        """Remove one signle package
        """
        removes = []
        if GetFromInstalled(package).name() and package not in self.skip:
            ver = GetFromInstalled(package).version()
            removes.append(f"{package}-{ver}")
            self._removepkg(package)
        return removes

    def _skip_remove(self):
        """Skip packages from remove
        """
        if "--checklist" not in self.extra:
            self.msg.template(78)
            print("| Insert packages to exception remove:")
            self.msg.template(78)
            try:
                self.skip = input(" > ").split()
            except EOFError:
                raise SystemExit("\n")
        for s in self.skip:
            if s in self.removed:
                self.removed.remove(s)

    def _check_if_used(self, removes):
        """Check package if dependencies for another package
        before removed"""
        if "--check-deps" in self.extra:
            package, dependency, pkg_dep = [], [], []
            for pkg in find_package("", self.dep_path):
                deps = self.read_file(self.dep_path + pkg)
                for rmv in removes:
                    if GetFromInstalled(rmv).name() and rmv in deps.split():
                        pkg_dep.append(f"{rmv} is dependency of the "
                                       f"package --> {pkg}")
                        package.append(pkg)
                        dependency.append(rmv)
            if package:
                if "--checklist" in self.extra:
                    text = ("Press 'spacebar' to choose packages for the"
                            " remove exception")
                    backtitle = f"{self.meta.__all__} {self.meta.__version__}"
                    status = False
                    choose = DialogUtil(pkg_dep, text, " !!! WARNING !!! ",
                                        backtitle, status).checklist()
                    for pkg in choose:
                        self.skip.append(pkg.split()[0])
                else:
                    self.msg.template(78)
                    print("| {0}{1}{2}".format(
                        self.red, " " * 30 + "!!! WARNING !!!", self.endc))
                    self.msg.template(78)
                    for p, d in zip(package, dependency):
                        print(f"| {self.yellow}{d}{self.endc} is dependency "
                              f"of the package --> {self.green}{p}{self.endc}")
                    self.msg.template(78)
                    self._skip_remove()

    def _reference_rmvs(self, removes):
        """Prints all removed packages
        """
        print()
        self.msg.template(78)
        msg_pkg = "package"
        if len(removes) > 1:
            msg_pkg = "packages"
        print(f"| Total {len(removes)} {msg_pkg} removed")
        self.msg.template(78)
        for pkg in removes:
            if not GetFromInstalled(pkg).name():
                print(f"| Package {pkg} removed")
            else:
                print(f"| Package {pkg} not found")
        self.msg.template(78)
        print()   # new line at end

    def find(self, flag):
        """Find installed Slackware packages
        """
        matching, packages = 0, []
        pkg_cache, match_cache = "", ""
        slack_packages, slack_names = slackware_repository()
        print("Packages with matching name [ {0}{1}{2} ]\n".format(
            self.cyan, ", ".join(self.binary), self.endc))
        for pkg in self.binary:
            for match in find_package("", self.meta.pkg_path):
                pkg_cache = pkg
                match_cache = match
                split_name = split_package(match)[0]
                if "--case-ins" in flag:
                    pkg_cache = pkg.lower()
                    match_cache = match.lower()
                if ("--third-party" in flag and not self.binary and
                        split_name not in slack_names):
                    packages.append(match)
                if ("--third-party" in flag and pkg_cache in match_cache and
                        split_name not in slack_names):
                    packages.append(match)
                if pkg_cache in match_cache and not flag:
                    packages.append(match)
                if ("--case-ins" in flag and "--third-party" not in flag and
                        pkg_cache in match_cache):
                    packages.append(match)
        for pkgs in packages:
            matching += 1
            self._sizes(pkgs)
            print(f"[ {self.green}installed{self.endc} ] "
                  f"[ {self.file_size} ] - {pkgs}")
        if matching == 0:
            message = "Can't find"
            self.msg.pkg_not_found("", ", ".join(self.binary), message, "\n")
            raise SystemExit(1)
        else:
            self._calc_sizes()
            print("\nFound summary")
            print("=" * 79)
            print("{0}Total found {1} matching packages.{2}".format(
                self.grey, matching, self.endc))
            print("{0}Size of installed packages {1} {2}.{3}\n".format(
                self.grey, round(self.size, 2), self.unit, self.endc))

    def _sizes(self, package):
        """Package size summary
        """
        data = self.read_file(self.meta.pkg_path + package)
        for line in data.splitlines():
            if line.startswith("UNCOMPRESSED PACKAGE SIZE:"):
                digit = float((''.join(re.findall(
                    r"[-+]?\d+[\.]?\d*[eE]?[-+]?\d*", line[26:]))))
                self.file_size = line[26:].strip()
                if "M" in line[26:]:
                    self.size += digit * 1024
                else:
                    self.size += digit
                    break

    def display(self):
        """Print the Slackware packages contents
        """
        for pkg in self.binary:
            name = GetFromInstalled(pkg).name()
            ver = GetFromInstalled(pkg).version()
            find = find_package(f"{name}-{ver}-", self.meta.pkg_path)
            if find:
                package = self.read_file(
                    self.meta.pkg_path + "".join(find))
                print(package)
            else:
                message = "Can't dislpay"
                if len(self.binary) > 1:
                    bol = eol = ""
                else:
                    bol = eol = "\n"
                self.msg.pkg_not_found(bol, pkg, message, eol)
                raise SystemExit(1)

    def package_list(self, repo, name, INDEX, installed):
        """List with the installed packages
        """
        tty_size = os.popen("stty size", "r").read().split()
        row = int(tty_size[0]) - 2
        try:
            all_installed_names = []
            index, page, pkg_list = 0, row, []
            r = self.list_lib(repo)
            pkg_list = self.list_greps(repo, r)[0]
            all_installed_names = self.list_of_installed(repo, name)
            print()
            for pkg in sorted(pkg_list):
                pkg = self._splitting_packages(pkg, repo, name)
                if installed and repo:
                    if pkg in all_installed_names:
                        pkg = f"{self.green}{pkg}{self.endc}"

                if INDEX:
                    index += 1
                    pkg = self.list_color_tag(pkg)
                    print(f"{self.grey}{index}:{self.endc} {pkg}")
                    if index == page:
                        read = input(f"\nPress {self.cyan}Enter{self.endc} to "
                                     f"continue... ")
                        if read in ["Q", "q"]:
                            break
                        print()   # new line after page
                        page += row
                else:
                    print(pkg)
            print()   # new line at end
        except (EOFError, KeyboardInterrupt, BrokenPipeError, IOError):
            raise SystemExit(1)

    def _splitting_packages(self, pkg, repo, name):
        """Return package name from repositories
        """
        if name and repo != "sbo":
            pkg = split_package(pkg)[0]
        elif not name and repo != "sbo":
            pkg = pkg[:-4]
        return pkg

    def list_greps(self, repo, packages):
        """Grep packages
        """
        pkg_list, pkg_size = [], []
        for line in packages.splitlines():
            if repo == "sbo":
                if line.startswith("SLACKBUILD NAME: "):
                    pkg_list.append(line[17:].strip())
                    pkg_size.append("0 K")
            else:
                if line.startswith("PACKAGE NAME: "):
                    pkg_list.append(line[15:].strip())
                if line.startswith("PACKAGE SIZE (compressed): "):
                    pkg_size.append(line[26:].strip())
        if repo == "alien" or repo == "ktown":
            return alien_filter(pkg_list, pkg_size)
        return pkg_list, pkg_size

    def list_lib(self, repo):
        """Return package lists
        """
        packages = ""
        if repo == "sbo":
            if (os.path.isfile(
                    self.meta.lib_path + "sbo_repo/SLACKBUILDS.TXT")):
                packages = self.read_file(f"{self.meta.lib_path}"
                                          "sbo_repo/SLACKBUILDS.TXT")
        else:
            if (os.path.isfile(
                    self.meta.lib_path + f"{repo}_repo/PACKAGES.TXT")):
                packages = self.read_file(f"{self.meta.lib_path}"
                                          f"{repo}_repo/PACKAGES.TXT")
        return packages

    def list_color_tag(self, pkg):
        """Tag with color installed packages
        """
        name = GetFromInstalled(pkg).name()
        find = f"{name}-"
        if pkg.endswith(".txz") or pkg.endswith(".tgz"):
            find = pkg[:-4]
        if find_package(find, self.meta.pkg_path):
            pkg = f"{self.green}{pkg}{self.endc}"
        return pkg

    def list_of_installed(self, repo, name):
        """Return installed packages
        """
        all_installed_names = []
        all_installed_packages = find_package("", self.meta.pkg_path)
        for inst in all_installed_packages:
            if repo == "sbo" and inst.endswith("_SBo"):
                name = split_package(inst)[0]
                all_installed_names.append(name)
            else:
                if name:
                    all_installed_names.append(split_package(inst)[0])
                else:
                    all_installed_names.append(inst)
        return all_installed_names


def alien_filter(packages, sizes):
    """This filter avoid list double packages from
    alien repository
    """
    cache, npkg, nsize = [], [], []
    for p, s in zip(packages, sizes):
        name = split_package(p)[0]
        if name not in cache:
            cache.append(name)
            npkg.append(p)
            nsize.append(s)
    return npkg, nsize
