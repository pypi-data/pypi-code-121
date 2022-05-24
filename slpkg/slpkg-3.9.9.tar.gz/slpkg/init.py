#!/usr/bin/python3
# -*- coding: utf-8 -*-

# init.py file is part of slpkg.

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

from slpkg.utils import Utils
from slpkg.repositories import Repo
from slpkg.file_size import FileSize
from slpkg.downloader import Download
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.slack.mirrors import mirrors
from slpkg.slack.slack_version import slack_ver


class Initialization(Utils):
    """Slpkg initialization start all from here. Create local
    package lists and update or upgrade these.
    """
    def __init__(self, check):
        self.check = check
        self.meta = _meta_
        self.arch = _meta_.arch
        self.slack_ver = slack_ver()
        self.def_repos_dict = Repo().default_repository()
        self.conf_path = self.meta.conf_path
        self.log_path = self.meta.log_path
        self.lib_path = self.meta.lib_path
        self.tmp_path = self.meta.tmp_path
        self.build_path = self.meta.build_path
        self._SOURCES = self.meta.SBo_SOURCES
        self.slpkg_tmp_packages = self.meta.slpkg_tmp_packages
        self.slpkg_tmp_patches = self.meta.slpkg_tmp_patches
        self.constructing()

    def constructing(self):
        """Creating the all necessary directories
        """
        paths_basic = [
            self.conf_path,
            self.log_path,
            self.lib_path,
            self.tmp_path
        ]

        paths_extra = [
            self.build_path,
            self._SOURCES,
            self.slpkg_tmp_packages,
            self.slpkg_tmp_patches
        ]

        self.make_dir(paths_basic)
        self.make_dirs(paths_extra)

    def make_dir(self, path: list):
        for p in path:
            if not os.path.exists(p):
                os.mkdir(p)

    def make_dirs(self, path: list):
        for p in path:
            if not os.path.exists(p):
                os.makedirs(p)

    def custom(self, name):
        """Creating user select repository local library
        """
        repo = Repo().custom_repository()[name]
        log = self.log_path + name + "/"
        lib = self.lib_path + f"{name}_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        PACKAGES_TXT = f"{repo}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{md5_file}"
        ChangeLog_txt = f"{repo}{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def slack(self):
        """Creating slack local libraries
        """
        log = self.log_path + "slack/"
        lib = self.lib_path + "slack_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        dirs = ["core/", "extra/", "patches/"]
        self.make_dir([log, lib])
        self.make_dir([f"{lib}{dirs[0]}",
                       f"{lib}{dirs[1]}",
                       f"{lib}{dirs[2]}"])
        PACKAGES_TXT = mirrors(lib_file, "")
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = mirrors(md5_file, "")
        self.EXTRA = mirrors(lib_file, dirs[1])
        self.EXT_CHECKSUMS = mirrors(md5_file, dirs[1])
        self.PATCHES = mirrors(lib_file, dirs[2])
        self.PAT_CHECKSUMS = mirrors(md5_file, dirs[2])
        ChangeLog_txt = mirrors(log_file, "")
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib + dirs[0], PACKAGES_TXT, repo_name)
        self.down(lib + dirs[0], CHECKSUMS_MD5, repo_name)
        self.down(lib + dirs[1], self.EXTRA, repo_name)
        self.down(lib + dirs[1], self.EXT_CHECKSUMS, repo_name)
        self.down(lib + dirs[2], self.PATCHES, repo_name)
        self.down(lib + dirs[2], self.PAT_CHECKSUMS, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)
        self.merge(lib, "PACKAGES.TXT", ["core/PACKAGES.TXT",
                                         "extra/PACKAGES.TXT",
                                         "patches/PACKAGES.TXT"])
        self.merge(lib, "CHECKSUMS.md5", ["core/CHECKSUMS.md5",
                                          "extra/CHECKSUMS.md5",
                                          "patches/CHECKSUMS_md5"])

    def sbo(self):
        """Creating sbo local library
        """
        repo = self.def_repos_dict["sbo"]
        log = self.log_path + "sbo/"
        lib = self.lib_path + "sbo_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "SLACKBUILDS.TXT"
        # lst_file = ""
        # md5_file = ""
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        SLACKBUILDS_TXT = f"{repo}{self.slack_ver}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = ""
        ChangeLog_txt = f"{repo}{self.slack_ver}/{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, SLACKBUILDS_TXT, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, SLACKBUILDS_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def rlw(self):
        """Creating rlw local library
        """
        repo = self.def_repos_dict["rlw"]
        log = self.log_path + "rlw/"
        lib = self.lib_path + "rlw_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        PACKAGES_TXT = f"{repo}{self.slack_ver}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{self.slack_ver}/{md5_file}"
        ChangeLog_txt = f"{repo}{self.slack_ver}/{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def alien(self):
        """Creating alien local library
        """
        ar = "x86"
        ver = self.slack_ver
        repo = self.def_repos_dict["alien"]
        log = self.log_path + "alien/"
        lib = self.lib_path + "alien_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = self.arch
        if self.meta.slack_rel == "current":
            ver = self.meta.slack_rel
        PACKAGES_TXT = f"{repo}/{ver}/{ar}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}/{ver}/{ar}/{md5_file}"
        ChangeLog_txt = f"{repo}{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def slacky(self):
        """Creating slacky.eu local library
        """
        ar = ""
        repo = self.def_repos_dict["slacky"]
        log = self.log_path + "slacky/"
        lib = self.lib_path + "slacky_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = "64"
        PACKAGES_TXT = f"{repo}slackware{ar}-{self.slack_ver}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}slackware{ar}-{self.slack_ver}/{md5_file}"

        ChangeLog_txt = f"{repo}slackware{ar}-{self.slack_ver}/{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def conrad(self):
        """Creating slackers local library
        """
        repo = self.def_repos_dict["conrad"]
        log = self.log_path + "conrad/"
        lib = self.lib_path + "conrad_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        PACKAGES_TXT = f"{repo}{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{md5_file}"
        ChangeLog_txt = f"{repo}{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def slonly(self):
        """Creating slackers local library
        """
        ar = f"{self.slack_ver}-x86"
        repo = self.def_repos_dict["slonly"]
        log = self.log_path + "slonly/"
        lib = self.lib_path + "slonly_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = f"{self.slack_ver}-x86_64"
        if self.meta.slack_rel == "current":
            ar = f"{self.meta.slack_rel}-x86"
        if self.meta.slack_rel == "current" and self.arch == "x86_64":
            ar = f"{self.meta.slack_rel}-x86_64"
        PACKAGES_TXT = f"{repo}{ar}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{ar}/{md5_file}"
        ChangeLog_txt = f"{repo}{ar}/{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def ktown(self):
        """Creating alien ktown local library
        """
        repo = self.def_repos_dict["ktown"]
        log = self.log_path + "ktown/"
        lib = self.lib_path + "ktown_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        PACKAGES_TXT = f"{repo}{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{md5_file}"
        ChangeLog_txt = f"{repo}{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def multi(self):
        """Creating alien multilib local library
        """
        ver = self.slack_ver
        repo = self.def_repos_dict["multi"]
        log = self.log_path + "multi/"
        lib = self.lib_path + "multi_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.meta.slack_rel == "current":
            ver = self.meta.slack_rel
        PACKAGES_TXT = f"{repo}{ver}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{ver}/{md5_file}"
        ChangeLog_txt = f"{repo}{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def slacke(self):
        """Creating Slacke local library
        """
        ar = ""
        repo = self.def_repos_dict["slacke"]
        log = self.log_path + "slacke/"
        lib = self.lib_path + "slacke_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = "64"
        version = self.meta.slacke_sub_repo[1:-1]
        PACKAGES_TXT = (f"{repo}slacke{version}/slackware{ar}-"
                        f"{self.slack_ver}/{lib_file}")
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = (f"{repo}slacke{version}/slackware{ar}-"
                         f"{self.slack_ver}/{md5_file}")
        ChangeLog_txt = (f"{repo}slacke{version}/slackware{ar}-"
                         f"{self.slack_ver}/{log_file}")
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def salix(self):
        """Creating SalixOS local library
        """
        ar = "i486"
        repo = self.def_repos_dict["salix"]
        log = self.log_path + "salix/"
        lib = self.lib_path + "salix_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = "x86_64"
        PACKAGES_TXT = f"{repo}{ar}/{self.slack_ver}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{ar}/{self.slack_ver}/{md5_file}"
        ChangeLog_txt = f"{repo}{ar}/{self.slack_ver}/{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def slackl(self):
        """Creating slackel.gr local library
        """
        ar = "i486"
        repo = self.def_repos_dict["slackl"]
        log = self.log_path + "slackl/"
        lib = self.lib_path + "slackl_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = "x86_64"
        PACKAGES_TXT = f"{repo}{ar}/current/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{ar}/current/{md5_file}"
        ChangeLog_txt = f"{repo}{ar}/current/{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def rested(self):
        """Creating alien restricted local library
        """
        repo = self.def_repos_dict["rested"]
        log = self.log_path + "rested/"
        lib = self.lib_path + "rested_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        PACKAGES_TXT = f"{repo}{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{md5_file}"
        ChangeLog_txt = f"{repo}{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def msb(self):
        """Creating MATE local library
        """
        ar = "x86"
        ver_slack = self.slack_ver
        repo = self.def_repos_dict["msb"]
        log = self.log_path + "msb/"
        lib = self.lib_path + "msb_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = "x86_64"
        version = self.meta.msb_sub_repo[1:-1]
        if self.meta.slack_rel == "current":
            ver_slack = self.meta.slack_rel
        PACKAGES_TXT = f"{repo}{ver_slack}/{version}/{ar}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{ver_slack}/{version}/{ar}/{md5_file}"
        ChangeLog_txt = f"{repo}{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def csb(self):
        """Creating Cinnamon local library
        """
        ar = "x86"
        ver_slack = self.slack_ver
        repo = self.def_repos_dict["csb"]
        log = self.log_path + "csb/"
        lib = self.lib_path + "csb_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = "x86_64"
        if self.meta.slack_rel == "current":
            ver_slack = self.meta.slack_rel
        PACKAGES_TXT = f"{repo}{ver_slack}/{ar}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{ver_slack}/{ar}/{md5_file}"
        ChangeLog_txt = f"{repo}{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def connos(self):
        """Creating connochaetos (slack-n-free) local library
        """
        nickname = "slack-n-free"
        ar = ""
        repo = self.def_repos_dict["connos"]
        log = self.log_path + "connos/"
        lib = self.lib_path + "connos_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = "64"
        PACKAGES_TXT = f"{repo}{nickname}{ar}-{self.slack_ver}/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{nickname}{ar}-{self.slack_ver}/{md5_file}"
        ChangeLog_txt = f"{repo}{nickname}{ar}-{self.slack_ver}/{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def mles(self):
        """Creating Microlinux local library
        """
        ar = "32"
        repo = self.def_repos_dict["mles"]
        log = self.log_path + "mles/"
        lib = self.lib_path + "mles_repo/"
        repo_name = log[:-1].split("/")[-1]
        lib_file = "PACKAGES.TXT"
        # lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        self.make_dir([log, lib])
        if self.arch == "x86_64":
            ar = "64"
        version = self.meta.mles_sub_repo[1:-1]
        PACKAGES_TXT = f"{repo}{version}-{self.slack_ver}-{ar}bit/{lib_file}"
        FILELIST_TXT = ""
        CHECKSUMS_MD5 = f"{repo}{version}-{self.slack_ver}-{ar}bit/{md5_file}"
        ChangeLog_txt = f"{repo}{version}-{self.slack_ver}-{ar}bit/{log_file}"
        if self.check:
            return self.checks_logs(log, ChangeLog_txt)
        self.down(lib, PACKAGES_TXT, repo_name)
        self.down(lib, CHECKSUMS_MD5, repo_name)
        self.down(log, ChangeLog_txt, repo_name)
        self.remote(log, ChangeLog_txt, lib, PACKAGES_TXT, CHECKSUMS_MD5,
                    FILELIST_TXT, repo_name)

    def down(self, path, link, repo):
        """Download files
        """
        filename = link.split("/")[-1]
        if not os.path.isfile(path + filename):
            Download(path, link.split(), repo).start()

    def remote(self, *args):
        """Remove and recreate files
        """
        log_path = args[0]
        ChangeLog_txt = args[1]
        lib_path = args[2]
        PACKAGES_TXT = args[3]
        CHECKSUMS_MD5 = args[4]
        FILELIST_TXT = args[5]
        repo = args[6]

        if self.checks_logs(log_path, ChangeLog_txt):
            # remove old files
            self.file_remove(log_path, ChangeLog_txt.split("/")[-1])
            self.file_remove(lib_path, PACKAGES_TXT.split("/")[-1])
            self.file_remove(lib_path, CHECKSUMS_MD5.split("/")[-1])
            self.file_remove(lib_path, FILELIST_TXT.split("/")[-1])
            if repo == "slack":
                dirs = ["core/", "extra/"]
                for d in dirs:
                    self.file_remove(lib_path + d, "PACKAGES.TXT")
                    self.file_remove(lib_path + d, "CHECKSUMS.md5")
                self.down(lib_path + "core/", PACKAGES_TXT, repo)
                self.down(lib_path + "core/", CHECKSUMS_MD5, repo)
                self.down(lib_path + "extra/", self.EXTRA, repo)
                self.down(lib_path + "extra/", self.EXT_CHECKSUMS, repo)
            # download new files
            if repo != "slack":
                self.down(lib_path, PACKAGES_TXT, repo)
                self.down(lib_path, CHECKSUMS_MD5, repo)
            self.down(lib_path, FILELIST_TXT, repo)
            self.down(log_path, ChangeLog_txt, repo)

    def merge(self, path, outfile, infiles):
        """Merge files
        """
        code = "utf-8"
        with open(path + outfile, 'w', encoding=code) as out_f:
            for f in infiles:
                if os.path.isfile(f"{path}{f}"):
                    # checking the encoding before read the file
                    code = self.check_encoding(path, f)
                    with open(path + f, "r", encoding=code) as in_f:
                        for line in in_f:
                            out_f.write(line)

    def file_remove(self, path, filename):
        """Check if filename exists and remove
        """
        if os.path.isfile(path + filename):
            os.remove(path + filename)

    def checks_logs(self, log_path, url):
        """Checks ChangeLog.txt for changes
        """
        local = ""
        filename = url.split("/")[-1]
        server = FileSize(url).server()
        if os.path.isfile(log_path + filename):
            local = FileSize(log_path + filename).local()
        if server != local:
            return True
        return False


class Upgrade:

    def __init__(self):
        self.meta = _meta_
        self.log_path = self.meta.log_path
        self.lib_path = self.meta.lib_path

    def run(self, repos):
        """Removing and creating the packages lists
        """
        repositories = self.meta.repositories

        # Replace the enabled repositories from user defined
        if repos:
            repositories = repos

        for repo in repositories:
            changelogs = f"{self.log_path}{repo}/ChangeLog.txt"
            if os.path.isfile(changelogs):
                os.remove(changelogs)

            if os.path.isdir(f"{self.lib_path}{repo}_repo/"):
                for f in os.listdir(f"{self.lib_path}{repo}_repo/"):
                    files = f"{self.lib_path}{repo}_repo/{f}"
                    if os.path.isfile(files):
                        os.remove(files)
                    elif os.path.isdir(files):
                        shutil.rmtree(files)
        update = Update()
        update.run(repos)


class Update:

    def __init__(self):
        self.meta = _meta_
        self.grey = _meta_.color["GREY"]
        self.green = _meta_.color["GREEN"]
        self.red = _meta_.color["RED"]
        self.cyan = _meta_.color["CYAN"]
        self.endc = _meta_.color["ENDC"]
        self.done = f"{self.green}Done{self.endc}\n"
        self.error = f"{self.red}Error{self.endc}\n"

    def run(self, repos):
        """Update repositories lists
        """
        print("\nCheck and update repositories:\n")
        default = self.meta.default_repositories
        enabled = self.meta.repositories
        custom = Repo().custom_repository()

        # Replace the enabled repositories from user defined
        if repos:
            enabled = repos

        for repo in enabled:
            if check_for_local_repos(repo) is True:
                continue
            self.done_msg(repo)
            if repo in default:
                getattr(Initialization(False), repo)()
                print(self.done, end="")
            elif repo in custom:
                Initialization(False).custom(repo)
                print(self.done, end="")
            else:
                print(self.error, end="")
        print()   # new line at end
        raise SystemExit()

    def done_msg(self, repo):
        print(f"{self.grey}Check repository "
              f"[{self.cyan}{repo}{self.grey}] ... "
              f"{self.endc}", end="", flush=True)


def check_exists_repositories(repo):
    """Checking if repositories exists by PACKAGES.TXT file
    """
    pkg_list = "PACKAGES.TXT"
    if repo == "sbo":
        pkg_list = "SLACKBUILDS.TXT"
    elif check_for_local_repos(repo) is True:
        pkg_list = "PACKAGES.TXT"
    if not os.path.isfile(f"{_meta_.lib_path}{repo}_repo/{pkg_list}"):
        return False


def check_for_local_repos(repo):
    """Check if repository is local
    """
    repos_dict = Repo().default_repository()
    if repo in repos_dict:
        repo_url = repos_dict[repo]
        if repo_url.startswith("file:///"):
            return True
