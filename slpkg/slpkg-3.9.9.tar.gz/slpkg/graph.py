#!/usr/bin/python3
# -*- coding: utf-8 -*-

# graph.py file is part of slpkg.

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
import subprocess


# class ImportErrorGraphEasy(Exception):
#    def __init__(self, GraphEasyImportError):
#        Exception.__init__(self, "graph-easy required")
#        self.GraphEasyImportError = GraphEasyImportError


class Graph:
    """Drawing dependencies diagram
    """
    def __init__(self, image):
        self.image = image
        self.file_format = [
            ".bmp", ".canon", ".cmap", ".cmapx", ".cmapx_np", ".dot",
            ".eps", ".fig", ".gd", ".gd2", ".gif", ".gtk", ".gv", ".ico",
            ".imap", ".imap_np", ".ismap", ".jpe", ".jpeg", ".jpg", ".pdf",
            ".pic", ".plain", ".plain-ext", ".png", ".pov", ".ps", ".ps2",
            ".svg", ".svgz", ".tif", ".tiff", ".tk", ".vml", ".vmlz",
            ".vrml", ".wbmp", ".x11", ".xdot", ".xlib"
        ]

    def dependencies(self, deps_dict):
        """Generate graph file with depenndencies map tree
        """
        try:
            import pygraphviz as pgv
        except ImportError:
            if (self.image == "ascii"
                    and not os.path.isfile("/usr/bin/graph-easy")):
                print("Require 'grap_easy': "
                      "Install with 'slpkg -s sbo graph-easy'")
            else:
                raise SystemExit("Require 'pygraphviz: "
                                 "Install with 'slpkg -s sbo pygraphviz'")
        if self.image != "ascii":
            self.check_file()
        try:
            G = pgv.AGraph(deps_dict)
            G.layout(prog="fdp")
            if self.image == "ascii":
                G.write(f"{self.image}.dot")
                self.graph_easy()
            G.draw(self.image)
        except IOError:
            raise SystemExit(1)
        if os.path.isfile(self.image):
            print(f"Graph image file '{self.image}' created")
        raise SystemExit()

    def check_file(self):
        """Check for file format and type
        """
        try:
            image_type = f".{self.image.split('.')[1]}"
            if image_type not in self.file_format:
                raise SystemExit(f"Format: '{self.image.split('.')[1]}' not "
                                 f"recognized. Use one of them:\n"
                                 f"{', '.join(self.file_format)}")
        except IndexError:
            raise SystemExit("slpkg: Error: Image file suffix missing")

    def graph_easy(self):
        """Draw ascii diagram. graph-easy perl module require
        """
        if not os.path.isfile("/usr/bin/graph-easy"):
            print("Require 'graph-easy': Install with 'slpkg -s sbo"
                  " graph-easy'")
            self.remove_dot()
            raise SystemExit(1)
        subprocess.call(f"graph-easy {self.image}.dot", shell=True)
        self.remove_dot()
        raise SystemExit(1)

    def remove_dot(self):
        """Remove .dot files
        """
        if os.path.isfile(f"{self.image}.dot"):
            os.remove(f"{self.image}.dot")
