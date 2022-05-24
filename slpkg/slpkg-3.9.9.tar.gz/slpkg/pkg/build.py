#!/usr/bin/python3
# -*- coding: utf-8 -*-

# build.py file is part of slpkg.

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
import sys
import time
import shutil
import tarfile
import itertools
import subprocess
import multiprocessing

from slpkg.utils import Utils
from slpkg.messages import Msg
from slpkg.checksum import check_md5
from slpkg.__metadata__ import MetaData as _meta_

from slpkg.sbo.greps import SBoGrep


class BuildPackage(Utils):
    """Build SBo packages from source
    """
    def __init__(self, script, sources, path, auto):
        self.script = script
        self.sources = sources
        self._check_sources()
        self.path = path
        self.auto = auto
        self.meta = _meta_
        self.msg = Msg()
        self._SOURCES = self.meta.SBo_SOURCES
        self.prgnam = self.script[:-7]
        self.log_file = f"build_{self.prgnam}_log"
        self.sbo_logs = self.meta.log_path + "sbo/"
        self.build_logs = self.sbo_logs + "build_logs/"
        self.start_log_time = time.strftime("%H:%M:%S")
        self.start_time = time.time()
        if not os.path.exists(self.meta.log_path):
            os.mkdir(self.meta.log_path)
        if not os.path.exists(self.sbo_logs):
            os.mkdir(self.sbo_logs)
        if not os.path.exists(self.build_logs):
            os.mkdir(self.build_logs)

    def build(self):
        """
        Build package from source and create log
        file in path /var/log/slpkg/sbo/build_logs/.
        Also check md5sum calculates.
        """
        try:
            self._delete_dir()
            try:
                tar = tarfile.open(self.script)
            except Exception as err:
                raise SystemExit(err)
            tar.extractall()
            tar.close()
            self._makeflags()
            self._delete_sbo_tar_gz()
            self._create_md5_dict()
            if not self.auto:
                os.chdir(self._SOURCES)
            for src in self.sources:
                if not os.path.isfile(src):
                    continue
                # fix build sources with spaces
                src = src.replace("%20", " ")
                check_md5(self.sbo_md5[src], src)
                # copy source and fix passing char '+' from file name
                shutil.copy2(src, self.path + self.prgnam)
            os.chdir(self.path + self.prgnam)
            # change permissions
            subprocess.call(f"chmod +x {self.prgnam}.SlackBuild", shell=True)
            pass_var = self._pass_variable()
            if self.meta.sbo_build_log in ["on", "ON"]:
                if os.path.isfile(self.build_logs + self.log_file):
                    os.remove(self.build_logs + self.log_file)
                # start log write
                log_head(self.build_logs, self.log_file, self.start_log_time)
                subprocess.Popen(f"{' '.join(pass_var)} ./{self.prgnam}.SlackBuild 2>&1 | tee -a "
                                 f"{self.build_logs}{self.log_file}", shell=True, stdout=sys.stdout).communicate()
                sum_time = build_time(self.start_time)
                # write end in log file
                log_end(self.build_logs, self.log_file, sum_time)
                print(f"Total build time for the package {self.prgnam} : {sum_time}\n")
            else:
                subprocess.call(f"{' '.join(pass_var)} ./{self.prgnam}.SlackBuild", shell=True)
            os.chdir(self.path)
        except (KeyboardInterrupt, KeyError) as e:
            print(e)   # (OSError, IOError, KeyError):
            self.msg.pkg_not_found("\n", self.prgnam, "Wrong file", "\n")

    def _check_sources(self):
        """Fix filenames with char +
        """
        new_sources = []
        for src in self.sources:
            new_sources.append(self.fix_file_name(src))
        self.sources = new_sources

    def _create_md5_dict(self):
        """Create md5 dictionary per source
        """
        self.sbo_md5 = {}
        md5_lists = SBoGrep(self.prgnam).checksum()
        for src, md5 in itertools.zip_longest(self.sources, md5_lists):
            self.sbo_md5[src] = md5

    def _makeflags(self):
        """Set variable MAKEFLAGS with the numbers of
        processors
        """
        if self.meta.makeflags in ["on", "ON"]:
            cpus = multiprocessing.cpu_count()
            os.environ["MAKEFLAGS"] = f"-j{cpus}"

    def _pass_variable(self):
        """Return enviroment variables
        """
        pass_var = []
        for var in os.environ.keys():
            expVAR = var.split("_")
            if expVAR[0] == self.prgnam.upper() and expVAR[1] != "PATH":
                pass_var.append(f"{expVAR[1]}={os.environ[var]}")
        return pass_var

    def _delete_sbo_tar_gz(self):
        """Delete slackbuild tar.gz file after untar
        """
        if not self.auto and os.path.isfile(self.meta.build_path + self.script):
            os.remove(self.meta.build_path + self.script)

    def _delete_dir(self):
        """Delete old folder if exists before start build
        """
        if not self.auto and os.path.isdir(self.meta.build_path + self.prgnam):
            shutil.rmtree(self.meta.build_path + self.prgnam)


def log_head(path, log_file, log_time):
    """
    write headers to log file
    """
    with open(path + log_file, "w") as log:
        log.write("#" * 79 + "\n\n")
        log.write("File : " + log_file + "\n")
        log.write("Path : " + path + "\n")
        log.write("Date : " + time.strftime("%d/%m/%Y") + "\n")
        log.write("Time : " + log_time + "\n\n")
        log.write("#" * 79 + "\n\n")


def log_end(path, log_file, sum_time):
    """
    append END tag to a log file
    """
    with open(path + log_file, "a") as log:
        log.seek(2)
        log.write("#" * 79 + "\n\n")
        log.write("Time : " + time.strftime("%H:%M:%S") + "\n")
        log.write(f"Total build time : {sum_time}\n")
        log.write(" " * 38 + "E N D\n\n")
        log.write("#" * 79 + "\n\n")


def build_time(start_time):
    """
    Calculate build time per package
    """
    diff_time = round(time.time() - start_time, 2)
    if diff_time <= 59.99:
        sum_time = str(diff_time) + " Sec"
    elif diff_time > 59.99 and diff_time <= 3599.99:
        sum_time = round(diff_time / 60, 2)
        sum_time_list = re.findall(r"\d+", str(sum_time))
        sum_time = (f"{sum_time_list[0]} Min {sum_time_list[1]} Sec")
    elif diff_time > 3599.99:
        sum_time = round(diff_time / 3600, 2)
        sum_time_list = re.findall(r"\d+", str(sum_time))
        sum_time = (f"{sum_time_list[0]} Hours {sum_time_list[1]} Min")
    return sum_time
