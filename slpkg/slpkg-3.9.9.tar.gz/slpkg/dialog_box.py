#!/usr/bin/python3
# -*- coding: utf-8 -*-

# dialog_box.py file is part of slpkg.

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


from __future__ import unicode_literals

import os


class DialogUtil:
    """Create dialog checklist
    """
    def __init__(self, *args):
        self.imp_dialog()
        self.data = args[0]
        self.text = args[1]
        self.title = args[2]
        self.backtitle = args[3]
        self.status = args[4]
        self.ununicode = []
        self.tags = []

    def imp_dialog(self):
        try:
            from dialog import Dialog
        except ImportError as er:
            raise SystemExit(er)
        self.d = Dialog(dialog="dialog", autowidgetsize=True)

    def checklist(self):
        """Run dialog checklist
        """
        choice = []
        for item in self.data:
            choice.append((item, "", self.status))
        code, self.tags = self.d.checklist(
            text=self.text, height=20, width=65, list_height=13,
            choices=choice, title=self.title, backtitle=self.backtitle)
        if code == "ok":
            self.unicode_to_string()
            return self.ununicode
        if code in ["cancel", "esc"]:
            self.exit()

    def buildlist(self, enabled):
        """Run dialog buildlist
        """
        choice = []
        for item in self.data:
            choice.append((item, False))
        for item in enabled:
            choice.append((item, True))
        items = [(tag, tag, sta) for (tag, sta) in choice]
        code, self.tags = self.d.buildlist(
            text=self.text, items=items, visit_items=True, item_help=False,
            title=self.title)
        if code == "ok":
            self.unicode_to_string()
            return self.ununicode
        if code in ["cancel", "esc"]:
            self.exit()

    def exit(self):
        """Exit from dialog
        """
        self.clear_screen()
        raise SystemExit()

    def clear_screen(self):
        """Clear screen
        """
        os.system("clear")

    def unicode_to_string(self):
        """Convert unicode in string
        """
        for tag in self.tags:
            self.ununicode.append(str(tag))
