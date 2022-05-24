#!/usr/bin/python3
# -*- coding: utf-8 -*-

# network.py file is part of slpkg.

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
import pydoc

from slpkg.utils import Utils
from slpkg.messages import Msg
from slpkg.blacklist import BlackList
from slpkg.downloader import Download
from slpkg.remove import delete_folder
from slpkg.dialog_box import DialogUtil
from slpkg.security import pkg_security
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.pkg.find import find_package
from slpkg.pkg.build import BuildPackage
from slpkg.pkg.manager import PackageManager

from slpkg.sbo.read import ReadSBo
from slpkg.sbo.greps import SBoGrep
from slpkg.sbo.sbo_arch import SBoArch
from slpkg.sbo.compressed import SBoLink
from slpkg.sbo.search import sbo_search_pkg
from slpkg.sbo.slack_find import slack_package

from slpkg.slack.slack_version import slack_ver


class SBoNetwork(BlackList, Utils):
    """View SBo site in terminal and also read, build or
    install packages
    """
    def __init__(self, name, flag):
        super().__init__()
        self.name = name
        self.flag = flag
        self.meta = _meta_
        self.msg = Msg()
        self.arch = SBoArch().get()
        self.comp_tar = ".tar.gz"
        self.choice = ""
        self.FAULT = ""
        self.green = self.meta.color["GREEN"]
        self.red = self.meta.color["RED"]
        self.yellow = self.meta.color["YELLOW"]
        self.cyan = self.meta.color["CYAN"]
        self.grey = self.meta.color["GREY"]
        self.endc = self.meta.color["ENDC"]
        self.build_folder = self.meta.build_path
        self._SOURCES = self.meta.SBo_SOURCES
        self.msg.reading()
        self.data = SBoGrep(name="").names()
        self.case_insensitive()
        if "--checklist" in self.flag:
            self.with_checklist()
        grep = SBoGrep(self.name)
        self.sbo_files = grep.files()
        self.sbo_url = sbo_search_pkg(self.name)
        if self.sbo_url:
            self.sbo_desc = grep.description()[len(self.name) + 2:-1]
            self.source_dwn = grep.source().split()
            self.sbo_req = grep.requires()
            self.sbo_dwn = SBoLink(self.sbo_url).tar_gz()
            self.sbo_version = grep.version()
            self.dwn_srcs = self.sbo_dwn.split() + self.source_dwn
        if "--checklist" not in self.flag or not self.sbo_url and self.name:
            self.msg.done()

    def view(self):
        """View SlackBuild package, read or install them
        from slackbuilds.org
        """
        if self.sbo_url and self.name not in self.get_black():
            self.prgnam = f"{self.name}-{self.sbo_version}"
            self.view_sbo()
            while True:
                self.read_choice()
                choice = {
                    "r": self.choice_README,
                    "R": self.choice_README,
                    "s": self.choice_SlackBuild,
                    "S": self.choice_SlackBuild,
                    "f": self.choice_info,
                    "F": self.choice_info,
                    "o": self.choice_doinst,
                    "O": self.choice_doinst,
                    "d": self.choice_download,
                    "D": self.choice_download,
                    "download": self.choice_download,
                    "b": self.choice_build,
                    "B": self.choice_build,
                    "build": self.choice_build,
                    "i": self.choice_install,
                    "I": self.choice_install,
                    "install": self.choice_install,
                    "c": self.choice_clear_screen,
                    "C": self.choice_clear_screen,
                    "clear": self.choice_clear_screen,
                    "q": self.choice_quit,
                    "quit": self.choice_quit,
                    "Q": self.choice_quit
                }
                try:
                    choice[self.choice]()
                except KeyError:
                    pass
        else:
            self.msg.pkg_not_found("\n", self.name, "Can't view", "\n")
            raise SystemExit(1)

    def case_insensitive(self):
        """Matching packages distinguish between uppercase and
        lowercase
        """
        if "--case-ins" in self.flag:
            data_dict = self.case_sensitive(self.data)
            for key, value in data_dict.items():
                if key == self.name.lower():
                    self.name = value

    def read_choice(self):
        """Return choice
        """
        commands = {
            "r": "README",
            "R": "README",
            "s": f"{self.name}.SlackBuild",
            "S": f"{self.name}.SlackBuild",
            "f": f"{self.name}.info",
            "F": f"{self.name}.info",
            "o": "doinst.sh",
            "O": "doinst.sh",
            "d": "download",
            "D": "download",
            "download": "download",
            "b": "build",
            "B": "build",
            "build": "build",
            "i": "install",
            "I": "install",
            "install": "install",
            "c": "clear",
            "C": "clear",
            "clear": "clear",
            "q": "quit",
            "quit": "quit",
            "Q": "quit"
        }
        try:
            message = "  Choose an option > "
            self.choice = input(f"{self.grey}{message}{self.endc}")
        except EOFError:
            raise SystemExit('\n')
        try:
            print("{0}\x1b[1A{1}{2}{3}\n".format(
                " " * len(message), self.cyan, commands[self.choice],
                self.endc), end="")
            print(end="", flush=True)
        except KeyError:
            pass

    def choice_README(self):
        """View README file
        """
        README = ReadSBo(self.sbo_url).readme("README")
        fill = self.fill_pager(README)
        self.pager(README + fill)

    def choice_SlackBuild(self):
        """View .SlackBuild file
        """
        SlackBuild = ReadSBo(self.sbo_url).slackbuild(self.name, ".SlackBuild")
        fill = self.fill_pager(SlackBuild)
        self.pager(SlackBuild + fill)

    def choice_info(self):
        """View .info file
        """
        info = ReadSBo(self.sbo_url).info(self.name, ".info")
        fill = self.fill_pager(info)
        self.pager(info + fill)

    def choice_doinst(self):
        """View doinst.sh file
        """
        if "doinst.sh" in self.sbo_files.split():
            doinst_sh = ReadSBo(self.sbo_url).doinst("doinst.sh")
            fill = self.fill_pager(doinst_sh)
            self.pager(doinst_sh + fill)

    def choice_download(self):
        """Download script.tar.gz and sources
        """
        Download(path="", url=self.dwn_srcs, repo="sbo").start()
        raise SystemExit()

    def choice_build(self):
        """Build package
        """
        self.build()
        delete_folder(self.build_folder)
        raise SystemExit()

    def choice_install(self):
        """Download, build and install package
        """
        pkg_security([self.name])
        if not find_package(self.prgnam, self.meta.pkg_path):
            self.build()
            self.install()
            delete_folder(self.build_folder)
            raise SystemExit()
        else:
            self.msg.template(78)
            self.msg.pkg_found(self.prgnam)
            self.msg.template(78)
            raise SystemExit()

    def choice_clear_screen(self):
        """Clear screen
        """
        os.system("clear")
        self.view()

    def choice_quit(self):
        """Quit from choices
        """
        raise SystemExit()

    def view_sbo(self):
        """View slackbuild.org
        """
        sbo_url = self.sbo_url.replace("/slackbuilds/", "/repository/")
        br1, br2, fix_sp = "", "", " "
        if self.meta.use_colors in ["off", "OFF"]:
            br1 = "("
            br2 = ")"
            fix_sp = ""
        print()   # new line at start
        self.msg.template(78)
        print(f"| {' ' * 28}{self.grey}SlackBuilds Repository{self.endc}")
        self.msg.template(78)
        print(f"| {slack_ver()} > {sbo_url.split('/')[-3].title()} > {self.cyan}{self.name}{self.endc}")
        self.msg.template(78)
        print(f"| {self.green}Package url{self.endc}: {sbo_url}")
        self.msg.template(78)
        print(f"| {self.green}Description: {self.endc}{self.sbo_desc}")
        print(f"| {self.green}SlackBuild: {self.endc}{self.sbo_dwn.split('/')[-1]}")
        print(f"| {self.green}Sources: {self.endc}{', '.join([src.split('/')[-1] for src in self.source_dwn])}")
        print(f"| {self.yellow}Requirements: {self.endc}{', '.join(self.sbo_req)}")
        self.msg.template(78)
        print(f"| {self.red}R{self.endc}{br2}EADME               View the README file")
        print(f"| {self.red}S{self.endc}{br2}lackBuild           View the .SlackBuild file")
        print(f"| In{br1}{self.red}f{self.endc}{br2}o{fix_sp}                View the .info file")
        if "doinst.sh" in self.sbo_files.split():
            print(f"| D{br1}{self.red}o{self.endc}{br2}inst.sh{fix_sp}           View the doinst.sh file")
        print(f"| {self.red}D{self.endc}{br2}ownload             Download this package")
        print(f"| {self.red}B{self.endc}{br2}uild                Download and build")
        print(f"| {self.red}I{self.endc}{br2}nstall              Download/Build/Install")
        print(f"| {self.red}C{self.endc}{br2}lear                Clear screen")
        print(f"| {self.red}Q{self.endc}{br2}uit                 Quit")
        self.msg.template(78)

    def with_checklist(self):
        """Using dialog and checklist option
        """
        data = []
        if not self.name:
            data = self.data
        else:
            for name in self.data:
                if self.name in name:
                    data.append(name)
        if data:
            text = "Press 'spacebar' to choose SlackBuild for view"
            title = " SlackBuilds.org "
            backtitle = f"{_meta_.__all__} {_meta_.__version__}"
            status = False
            pkg = DialogUtil(data, text, title, backtitle, status).checklist()
            if pkg and len(pkg) > 1:
                os.system("clear")
                raise SystemExit("\nslpkg: Error: Choose only one package\n")
            if pkg is None:
                raise SystemExit(1)
            self.name = "".join(pkg)
            os.system("clear")

    def pager(self, text):
        """Read text
        """
        pydoc.pager(text)

    def fill_pager(self, page):
        """Fix pager spaces
        """
        tty_size = os.popen("stty size", "r").read().split()
        rows = int(tty_size[0]) - 1
        lines = sum(1 for line in page.splitlines())
        diff = rows - lines
        fill = "\n" * diff
        if diff > 0:
            return fill
        else:
            return ""

    def error_uns(self):
        """Check if package supported by arch
        before proceed to install
        """
        self.FAULT = ""
        UNST = ["UNSUPPORTED", "UNTESTED"]
        if "".join(self.source_dwn) in UNST:
            self.FAULT = "".join(self.source_dwn)

    def build(self):
        """Only build and create Slackware package
        """
        pkg_security([self.name])
        self.error_uns()
        if self.FAULT:
            print()
            self.msg.template(78)
            print(f"| Package {self.prgnam} {self.red} {self.FAULT} "
                  f"{self.endc}")
            self.msg.template(78)
        else:
            sources = []
            if not os.path.exists(self.meta.build_path):
                os.makedirs(self.meta.build_path)
            if not os.path.exists(self._SOURCES):
                os.makedirs(self._SOURCES)
            os.chdir(self.meta.build_path)
            Download(self.meta.build_path, self.sbo_dwn.split(),
                     repo="sbo").start()
            Download(self._SOURCES, self.source_dwn, repo="sbo").start()
            script = self.sbo_dwn.split("/")[-1]
            for src in self.source_dwn:
                sources.append(src.split("/")[-1])
            BuildPackage(script, sources, self.meta.build_path,
                         auto=False).build()
            slack_package(self.prgnam)  # check if build

    def install(self):
        """Install SBo package found in /tmp directory.
        """
        binary = slack_package(self.prgnam)
        print(f"[ {self.green}Installing{self.endc} ] --> {self.name}")
        PackageManager(binary).upgrade(flag="--install-new")
