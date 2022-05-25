#!/usr/bin/python3
# -*- coding: utf-8 -*-

# main.py file is part of sbo-templates.

# Copyright 2015-2022 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# SBo tool for managing templates.

# https://gitlab.com/dslackw/sbo-templates

# sbo-templates is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


from __future__ import unicode_literals
import os
import sys
import pydoc
import locale
import hashlib
import subprocess
from datetime import date
from dialog import Dialog
from sbo_templates.templates import (
    SlackBuilds,
    doinst
)
from sbo_templates.__metadata__ import __version__

locale.setlocale(locale.LC_ALL, '')


class SBoTemplates:
    """SlackBuild Templates Class
    """
    def __init__(self):
        self.year = date.today().year
        self.d = Dialog(dialog="dialog")
        self.d.set_background_title(f"SlackBuild.org Templates {__version__}")
        self.args = sys.argv
        self.args.pop(0)
        self.__cli()
        self.source = ""
        self.chk_md5 = ""
        self.update_md5sum_x86 = False
        self.update_md5sum_x86_64 = False
        self.pwd = os.getcwd() + "/"
        self.slack_desc_text = []
        self.slack_desc_data = []
        # aboname.info
        self._version = '""'
        self._homepage = '""'
        self._download = '""'
        self._md5sum = '""'
        self._download_x86_64 = '""'
        self._md5sum_x86_64 = '""'
        self._requires = '""'
        # sboname.desktop
        self._name = self.args[0]
        self._comment = ""
        self._exec = "/usr/bin/{0}".format(self.args[0])
        self._icon = "/usr/share/pixmaps/{0}.png".format(self.args[0])
        self._terminal = "false"
        self._type = ""
        self._categories = ""
        self._genericname = ""

    def __cli(self):
        """command line interface
        """
        if len(self.args) > 1:
            self.__usage()
        elif len(self.args) == 1 and self.args[0] in ["-h", "--help"]:
            self.__usage()
        elif len(self.args) == 1 and self.args[0] in ["-v", "--version"]:
            self.__version()
        elif len(self.args) < 1:
            self.args = ['sboname']

    def __version(self):
        """version info
        """
        print("Version: {0}".format(__version__))
        sys.exit(0)

    def __usage(self):
        """optional arguments
        """
        args = [
            "Usage: sbotmp <sbo_name>\n",
            "Optional arguments:",
            "  -h, --help           Display this message and exit.",
            "  -v, --version        Show version and exit.",
        ]
        for opt in args:
            print("{0}".format(opt))
        sys.exit(0)

    def __templatesInit(self):
        """Initialiazation templates data
        """
        self.filename = ""
        self.msg = ""
        self.data = []
        self.height = 30
        self.width = 80
        self.app = self.args[0]
        self.handy_ruler = 1
        self.__slackDescComments()
        self.maintainer = '""'
        self.email = '""'
        self.live = ""
        self.editor = "vim"
        self.HOME = os.getenv("HOME") + "/"
        self.filename = "{0}.sbo-maintainer".format(self.HOME)
        self.__maintainerInit()
        self.choises = [
            ("Info", "Edit {0}.info file".format(self.app)),
            ("README", "Edit README file"),
            ("Desktop", "Edit {0}.desktop file".format(self.app)),
            ("Doinst.sh", "Edit doinst.sh script"),
            ("Slack desc", "Edit slack-desc file"),
            ("SlackBuild", "Edit {0}.SlackBuild script".format(
                self.app)),
            ("Chmod", "Permissions -+ {0}.SlackBuild script".format(self.app)),
            ("Download", "Download the sources"),
            ("MD5SUM", "Checksum the sources"),
            ("Maintainer", "Maintainer data"),
            ("Directory", "Change directory"),
            ("Help", "Where to get help"),
            ("Exit", "Exit the program")
        ]

    def __maintainerInit(self):
        """Initialization maintainer data
        """
        if os.path.isfile(self.filename):
            with open(self.filename, "r") as f:
                r = f.read()
                for line in r.splitlines():
                    if line.startswith("MAINTAINER"):
                        self.maintainer = line.split("=")[1]
                    if line.startswith("EMAIL"):
                        self.email = line.split("=")[1]
                    if line.startswith("LIVE"):
                        self.live = line.split("=")[1]
                    if line.startswith("EDITOR"):
                        self.editor = line.split("=")[1]

    def menu(self):
        """Dialog.menu(text, height=None, width=None, menu_height=None,
        choices=[], **kwargs)
        Display a menu dialog box.
        """
        self.__templatesInit()  # reset all data
        code, tag = self.d.menu("Choose an option or press ESC or <Cancel> to "
                                "Exit.", height=20, width=70,
                                menu_height=len(self.choises),
                                choices=self.choises)
        if code == self.d.CANCEL or code == self.d.ESC or tag[0] == "0":
            os.system("clear")
            sys.exit(0)
        case = {
            "Info": self.infoFile,
            "Slack desc": self.slackDesc,
            "Desktop": self.desktopFile,
            "Doinst.sh": self.doinst_sh,
            "SlackBuild": self.SlackBuild,
            "README": self.README,
            "Chmod": self.chmod,
            "Download": self.download,
            "MD5SUM": self.MD5SUM,
            "Maintainer": self.maintainerData,
            "Directory": self.__updateDirectory,
            "Help": self.getHelp,
            "Exit": self.exit,
        }
        case[tag]()

    def exit(self):
        os.system("clear")
        sys.exit(0)

    def getHelp(self):
        """get help from slackbuilds.org
        """
        self.msg = ("For additional assistance, visit: http://www.slackbuilds."
                    "org/guidelines/")
        self.width = len(self.msg) + 4
        self.height = 7
        self.messageBox()
        self.menu()

    def __updateDirectory(self):
        """update working direcroty
        """
        self.height = 10
        self.comments = "Current directory: {0}".format(self.pwd)
        field_length = 90
        input_length = 90
        attributes = '0x0'
        self.elements = [
            ("New path=", 1, 1, "", 1, 10, field_length, input_length,
             attributes),
        ]
        self.mixedform()
        if self.fields:
            if not os.path.isdir(self.fields[0].strip()):
                self.width = 60
                self.height = 6
                self.msg = "Directory {0} is not exist".format(
                    self.fields[0].strip())
                self.messageBox()
                self.menu()
            self.pwd = self.fields[0].strip()
            if self.pwd and not self.pwd.endswith("/"):
                self.pwd = self.pwd + "/"
            self.width = 60
            self.height = 6
            self.msg = "Current directory: {0}".format(self.pwd)
            self.messageBox()
        self.menu()

    def chmod(self):
        """change the permissions on the .SlackBuild script
        """
        self.height = 5
        if not os.path.isfile("{0}.SlackBuild".format(self.app)):
            self.msg = "There is no {0}.SlackBuild script".format(self.app)
            self.messageBox()
            self.menu()
        text = "Change the permissions to the SlackBuild script"
        height = 10
        width = 80
        choices = []
        choices = [
            ("chmod +x", "{0}.SlackBuild".format(self.app), False),
            ("chmod -x", "{0}.Slackbuild".format(self.app), False),
            ]
        code, tag = self.d.radiolist(text, height,
                                     width, list_height=0, choices=choices)
        if code == "cancel":
            self.menu()
        if tag == "chmod +x":
            subprocess.call("chmod +x {0}.SlackBuild".format(self.app),
                            shell=True)
        if tag == "chmod -x":
            subprocess.call("chmod -x {0}.SlackBuild".format(self.app),
                            shell=True)
        self.msg = ("The permissions has been changed in the script "
                    "{0}.SlackBuild".format(self.app))
        self.messageBox()
        self.menu()

    def download(self):
        """Download the sources
        """
        self.filename = "{0}.info".format(self.app)
        text = ["PRGNAM=", "VERSION=", "HOMEPAGE=", "DOWNLOAD=",
                "MD5SUM=", "DOWNLOAD_x86_64=", "MD5SUM_x86_64=",
                "REQUIRES=", "MAINTAINER=", "EMAIL="]
        self.__infoFileRead(text)
        download_x86 = self._download[1:-1]
        download_x86_64 = self._download_x86_64[1:-1]
        if not download_x86 and not download_x86_64:
            self.height = 10
            self.msg = "There are no DOWNLOAD's in the .info file"
            self.messageBox()
            self.menu()
        if download_x86:
            subprocess.call("wget {0}".format(download_x86), shell=True)
        if download_x86_64:
            subprocess.call("wget {0}".format(download_x86_64),
                            shell=True)
        input("Press Enter to continue ...")
        self.menu()

    def MD5SUM(self):
        """update the source checksum
        """
        text1 = "Choose which checksum you want to update"
        text2 = "Select the type of the architecture"
        sources = self.listDir()
        if not sources:
            self.height = 5
            self.msg = "No sources found"
            self.messageBox()
            self.menu()
        height = 20
        width = 80
        choices = []
        for k, v in sources.items():
            choices += [
                (v, k, False)
            ]
        code1, tag1 = self.d.radiolist(text1, height,
                                       width, list_height=0, choices=choices)
        if code1 == "cancel":
            self.menu()
        choices = [
                ("MD5SUM", "For x86 sources", False),
                ("MD5SUM_x86_64", "For x86_64 sources", False),
            ]
        code2, tag2 = self.d.radiolist(text2, height,
                                       width, list_height=0, choices=choices)
        if code2 == "cancel":
            self.menu()
        if tag2 == "MD5SUM":
            self._md5sum = '"{0}"'.format(tag1)
            self.update_md5sum_x86 = True
        elif tag2 == "MD5SUM_x86_64":
            self._md5sum_x86_64 = '"{0}"'.format(tag1)
            self.update_md5sum_x86_64 = True
        self.infoFile()
        self.menu()

    def maintainerData(self):
        """Maintainer data handler
        """
        cache_dir = self.pwd
        self.pwd = ""
        self.height = 15
        self.filename = "{0}.sbo-maintainer".format(self.HOME)
        self.comments = ("Enter the details of the maintainer and change "
                         "editor, \ndefault is 'vim'.")
        self.width = 90
        field_length = 90
        input_length = 90
        attributes = '0x0'
        text = ["MAINTAINER=", "EMAIL=", "LIVE=", "EDITOR="]
        self.elements = [
            (text[0], 1, 1, self.maintainer, 1, 12, field_length, input_length,
             attributes),
            (text[1], 2, 1, self.email, 2, 7, field_length, input_length,
             attributes),
            (text[2], 3, 1, self.live, 3, 6, field_length, input_length,
             attributes),
            (text[3], 4, 1, self.editor, 4, 8, field_length, input_length,
             attributes)
        ]
        self.mixedform()
        if self.fields:
            self.maintainer = self.fields[0]
            self.email = self.fields[1]
            self.live = self.fields[2]
            self.editor = self.fields[3]
            if not self.fields[0].startswith('"'):
                self.fields[0] = '"' + self.fields[0]
            if not self.fields[0].endswith('"'):
                self.fields[0] = self.fields[0] + '"'
            if not self.fields[1].startswith('"'):
                self.fields[1] = '"' + self.fields[1]
            if not self.fields[1].endswith('"'):
                self.fields[1] = self.fields[1] + '"'
        for item, line in zip(text, self.fields):
            self.data.append(item + line)
        self.choose()
        self.pwd = cache_dir

    def __slackDescComments(self):
        """slack-desc file comments
        """
        self.comments = (
            "# HOW TO EDIT THIS FILE:\n"
            '# The "handy ruler" below makes it easier to edit a package '
            'description.\n'
            "# Line up the first '|' above the ':' following the base package "
            "name, and\n"
            "# the '|' on the right side marks the last column you can put a "
            "character in.\n"
            "# You must make exactly 11 lines for the formatting to be correct"
            ".  It's also\n"
            "# customary to leave one space after the ':' except on otherwise "
            "blank lines.\n\n"
            "{0}|-----handy-ruler---------------------------------------------"
            "---------|".format(' ' * (len(self.app) + self.handy_ruler))
        )

    def slackDesc(self):
        """slack-desc file handler
        """
        self.__slackDescComments()
        self.filename = "slack-desc"
        self.width = 80 + len(self.app)
        field_length = 70
        input_length = 70
        attributes = '0x0'
        self.elements = []
        self.slack_desc_data = []
        self.__slackDeskRead()
        if not self.slack_desc_data[0]:     # check description
            self.elements = [
                ("{0}:".format(self.app), 1, 1, ' {0} ()'.format(self.app), 1,
                 len(self.app) + 2, field_length, input_length, attributes)
            ]
        for i, line in zip(range(2, 13), self.slack_desc_data):
            self.elements += [("{0}:".format(self.app), i, 1, line, i,
                               len(self.app) + 2, field_length, input_length,
                               attributes)]
        self.mixedform()
        self.handy_ruler = 0
        self.__slackDescComments()
        for line in self.comments.splitlines():
            self.data.append(line)
        for line in self.fields:
            if line:
                self.slack_desc_text.append("{0}".format(line.strip()))
            self.data.append("{0}:{1}".format(self.app, line))
        self.slack_desc_text = self.slack_desc_text[1:]
        self.choose()

    def __slackDeskRead(self):
        """grab slack-desc text if exist
        """
        line_count = 0
        if os.path.isfile(self.pwd + self.filename):
            with open(self.pwd + self.filename, "r") as info:
                for line in info:
                    line_count += 1
                    if line_count > 8 and line_count < 20:
                        self.slack_desc_data.append(
                            line[len(self.app) + 1:].rstrip())
        else:
            self.slack_desc_data = [""] * 10

    def infoFile(self):
        """<application>.info file handler
        """
        self.filename = "{0}.info".format(self.app)
        self.width = 90
        self.height = 20
        self.comments = self.filename
        field_length = 90
        input_length = 90
        attributes = '0x0'
        if not self.update_md5sum_x86:
            self._md5sum = '""'
        if not self.update_md5sum_x86_64:
            self.update_md5sum_x86_64 = '""'
        text = ["PRGNAM=", "VERSION=", "HOMEPAGE=", "DOWNLOAD=",
                "MD5SUM=", "DOWNLOAD_x86_64=", "MD5SUM_x86_64=",
                "REQUIRES=", "MAINTAINER=", "EMAIL="]
        self.__infoFileRead(text)
        self.elements = [
            (text[0], 1, 1, '"{0}"'.format(self.app), 1, 8,
             field_length, input_length, attributes),
            (text[1], 2, 1, self._version, 2, 9, field_length,
             input_length, attributes),
            (text[2], 3, 1, self._homepage, 3, 10, field_length * 4,
             input_length * 4, attributes),
            (text[3], 4, 1, self._download, 4, 10, field_length * 4,
             input_length * 4, attributes),
            (text[4], 5, 1, self._md5sum, 5, 8, field_length + 8,
             input_length + 8, attributes),
            (text[5], 6, 1, self._download_x86_64, 6, 17,
             field_length * 4, input_length * 4, attributes),
            (text[6], 7, 1, self._md5sum_x86_64, 7, 15,
             field_length * 4, input_length * 4, attributes),
            (text[7], 8, 1, self._requires, 8, 10, field_length * 4,
             input_length * 4, attributes),
            (text[8], 9, 1, self.maintainer, 9, 12,
             field_length, input_length, attributes),
            (text[9], 10, 1, self.email, 10, 7, field_length,
             input_length, attributes)
        ]
        self.mixedform()
        self.__autocorrectQuotationMark()
        if self.fields:
            self._version = self.fields[1]
            self._homepage = self.fields[2]
            self._download = self.fields[3]
            self._md5sum = self.fields[4]
            self.maintainer = self.fields[8]
            self.email = self.fields[9]
            if self._download:
                self.source = self._download[1:-1].split("/")[-1]
                self.chk_md5 = self._md5sum
                self.checksum()
            self._download_x86_64 = self.fields[5]
            self._md5sum_x86_64 = self.fields[6]
            if self._download_x86_64:
                self.source = self._download_x86_64[1:-1].split("/")[-1]
                self.chk_md5 = self._md5sum_x86_64
                self.checksum()
            self._requires = self.fields[7]
        for item, line in zip(text, self.fields):
            self.data.append(item + line)
        self.choose()

    def __autocorrectQuotationMark(self):
        """autocorrect the quotation mark "" in the .info file
        """
        for i, f in enumerate(self.fields):
            if not f.startswith('"'):
                self.fields[i] = '"' + f
            if not f.endswith('"'):
                self.fields[i] = self.fields[i] + '"'
            if f == '' or f == '"':
                self.fields[i] = '""'

    def __infoFileRead(self, text):
        """read data for <application>.info file if exist
        """
        if os.path.isfile(self.pwd + self.filename):
            with open(self.pwd + self.filename, "r") as info:
                for line in info:
                    try:
                        fd = line.split("=")[1].strip()
                        if line.startswith(text[1]):
                            self._version = fd
                        if line.startswith(text[2]):
                            self._homepage = fd
                        if line.startswith(text[3]):
                            self._download = fd
                        if (line.startswith(text[4]) and
                                not self.update_md5sum_x86):
                            self._md5sum = fd
                        if line.startswith(text[5]):
                            self._download_x86_64 = fd
                        if (line.startswith(text[6]) and
                                not self.update_md5sum_x86_64):
                            self._md5sum_x86_64 = fd
                        if line.startswith(text[7]):
                            self._requires = fd
                        if line.startswith(text[8]):
                            self.maintainer = fd
                        if line.startswith(text[9]):
                            self.email = fd
                    except IndexError:
                        self.height = 7
                        self.msg = ("Try to read the .info file failed. "
                                    "Not supported multi lines files.")
                        self.messageBox()
                        self.menu()
        self.update_md5sum_x86 = False
        self.update_md5sum_x86_64 = False

    def desktopFile(self):
        """<application>.desktop file handler
        """
        self.filename = "{0}.desktop".format(self.app)
        self.width = 90
        self.height = 20
        self.comments = self.filename
        field_length = 90
        input_length = 90
        attributes = '0x0'
        text = ["[Desktop Entry]", "Name=", "Comment=", "Exec=", "Icon=",
                "Terminal=", "Type=", "Categories=", "GenericName="]
        self.__desktopFileRead(text)
        self.elements = [
            (text[0], 1, 1, '', 1, 1, field_length, input_length, 0x1),
            (text[1], 2, 1, self._name, 2, 6, field_length,
             input_length, attributes),
            (text[2], 3, 1, self._comment, 3, 9, field_length, input_length,
             attributes),
            (text[3], 4, 1, self._exec, 4, 6, field_length, input_length,
             attributes),
            (text[4], 5, 1, self._icon, 5, 6, field_length, input_length,
             attributes),
            (text[5], 6, 1, self._terminal, 6, 10, field_length, input_length,
             attributes),
            (text[6], 7, 1, self._type, 7, 6, field_length, input_length,
             attributes),
            (text[7], 8, 1, self._categories, 8, 12, field_length,
             input_length, attributes),
            (text[8], 9, 1, self._genericname, 9, 13, field_length,
             input_length, attributes),
        ]
        self.mixedform()
        if self.fields:
            self._name = self.fields[1]
            self._comment = self.fields[2]
            self._exec = self.fields[3]
            self._icon = self.fields[4]
            self._terminal = self.fields[5]
            self._type = self.fields[6]
            self._categories = self.fields[7]
            self._genericname = self.fields[8]
        for item, line in zip(text, self.fields):
            self.data.append(item + line)
        self.choose()

    def __desktopFileRead(self, text):
        """read data for <application>.info file if exist
        """
        if os.path.isfile(self.pwd + self.filename):
            with open(self.pwd + self.filename, "r") as info:
                for line in info:
                    if line.startswith(text[1]):
                        self._name = line.split("=")[1].strip()
                    if line.startswith(text[2]):
                        self._comment = line.split("=")[1].strip()
                    if line.startswith(text[3]):
                        self._exec = line.split("=")[1].strip()
                    if line.startswith(text[4]):
                        self._icon = line.split("=")[1].strip()
                    if line.startswith(text[5]):
                        self._terminal = line.split("=")[1].strip()
                    if line.startswith(text[6]):
                        self._type = line.split("=")[1].strip()
                    if line.startswith(text[7]):
                        self._categories = line.split("=")[1].strip()
                    if line.startswith(text[8]):
                        self._genericname = line.split("=")[1].strip()

    def doinst_sh(self):
        """doinst.sh handler file
        """
        os.system("clear")
        temp = "\n".join(doinst.splitlines())
        pydoc.pipepager(temp, cmd='less -R')
        self.filename = "doinst.sh"
        self.edit()
        self.menu()

    def README(self):
        """README handler file
        """
        self.filename = "README"
        if self.slack_desc_text:
            yesno = self.d.yesno("Import description from <slack-desc> file ?")
            if yesno == "ok":
                self.data = self.slack_desc_text
                self.write()
        self.edit()
        self.menu()

    def SlackBuild(self):
        """SlackBuild handler file
        """
        self.filename = "{0}.info".format(self.app)
        text = ["x", "VERSION="] + (["x"] * 8)
        self.__infoFileRead(text)   # get version for .info file
        self.filename = "{0}.SlackBuild".format(self.app)
        if not os.path.isfile(self.pwd + self.filename):
            version = self._version.replace('"', '')
            height = 20
            width = 80
            choices = [
                ("autotools-template", "autotools-template.SlackBuild", False),
                ("cmake-template", "cmake-template.SlackBuild", False),
                ("perl-template", "perl-template.SlackBuild", False),
                ("python-template", "python-template.SlackBuild", False),
                ("rubygem-template", "rubygem-template.SlackBuild", False),
                ("haskell-template", "haskell-template.SlackBuild", False),
                ("meson-template", "meson-template.SlackBuild", False)
            ]
            code, tag = self.d.radiolist("{0}".format(self.filename), height,
                                         width, list_height=0, choices=choices)
            if code == "cancel":
                self.menu()
            self.msg = "{0} script created.".format(self.filename)
            self.height = 7
            self.width = len(self.msg) + 4
            maintainer = self.maintainer[1:-1]
            if tag == "autotools-template":
                self.data = SlackBuilds(
                    self.app, version, self.year, maintainer,
                    self.live).autotools().splitlines()
                self.write()
                self.messageBox()
            elif tag == "cmake-template":
                self.data = SlackBuilds(
                    self.app, version, self.year, maintainer,
                    self.live).cmake().splitlines()
                self.write()
                self.messageBox()
            elif tag == "perl-template":
                self.data = SlackBuilds(
                    self.app, version, self.year, maintainer,
                    self.live).perl().splitlines()
                self.write()
                self.messageBox()
            elif tag == "python-template":
                self.data = SlackBuilds(
                    self.app, version, self.year, maintainer,
                    self.live).python().splitlines()
                self.write()
                self.messageBox()
            elif tag == "rubygem-template":
                self.data = SlackBuilds(
                    self.app, version, self.year, maintainer,
                    self.live).rubygem().splitlines()
                self.write()
                self.messageBox()
            elif tag == "haskell-template":
                self.data = SlackBuilds(
                    self.app, version, self.year, maintainer,
                    self.live).haskell().splitlines()
                self.write()
                self.messageBox()
            elif tag == "meson-template":
                self.data = SlackBuilds(
                    self.app, version, self.year, maintainer,
                    self.live).meson().splitlines()
                self.write()
                self.messageBox()
        self.edit()
        self.menu()

    def mixedform(self):
        """Dialog.mixedform(text, elements, height=0, width=0, form_height=0,
        **kwargs)
        Display a form consisting of labels and fields.
        """
        self.code, self.fields = self.d.mixedform(self.comments, self.elements,
                                                  self.height, self.width)

    def edit(self):
        """editor handler
        """
        subprocess.call([self.editor, self.pwd + self.filename])

    def messageBox(self):
        """view messages
        """
        self.d.msgbox(self.msg, self.height, self.width)

    def choose(self):
        """Choosing if write to file or exit
        """
        if self.code == self.d.OK:
            self.__ifFileExist()
            self.write()
            self.messageBox()
            self.menu()
        elif self.code == self.d.CANCEL:
            self.menu()
        elif self.code == self.d.ESC:
            self.menu()

    def __ifFileExist(self):
        """check if file exist
        """
        self.width = 60
        self.height = 6
        if os.path.isfile(self.pwd + self.filename):
            self.msg = "File {0} modified.".format(self.filename)
        else:
            self.msg = "File {0} is created.".format(self.filename)

    def listDir(self):
        sources = {}
        suffixes = [".tar", ".gz", ".bz", ".bz2", ".xz", ".zip"]
        list_all_files = os.listdir(os.getcwd())
        for f in list_all_files:
            for s in suffixes:
                if f.endswith(s):
                    sources.update({f: self.sourceCheckSum(f)})
        return sources
        sys.exit()

    def checksum(self):
        """checksum sources
        """
        self.height = 7
        self.width = 90
        self.chk_md5 = "".join(self.chk_md5.replace('"', ''))
        if os.path.isfile(self.pwd + self.source):

            if self.chk_md5 != self.sourceCheckSum(self.source):
                self.msg = "MD5SUM check for {0} FAILED".format(
                    self.source)
                self.messageBox()
                self.infoFile()

    def sourceCheckSum(self, source):
        """md5sum sources
        """
        with open(self.pwd + source, "rb") as f:
            data = f.read()
            return hashlib.md5(data).hexdigest()

    def touch(self):
        """create empty file
        """
        with open(self.pwd + self.filename, "w") as f:
            f.close()

    def write(self):
        """write handler
        """
        with open(self.pwd + self.filename, "w") as f:
            for line in self.data:
                f.write(line + "\n")
