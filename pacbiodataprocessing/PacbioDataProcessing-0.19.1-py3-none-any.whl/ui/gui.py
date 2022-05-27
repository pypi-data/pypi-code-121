#######################################################################
#
# Copyright (C) 2021, 2022 David Palao
#
# This file is part of PacBioDataProcessing.
#
#  PacBioDataProcessing is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PacBio data processing is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PacBioDataProcessing. If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import re

from gooey import Gooey, GooeyParser

from .common import parse_user_input
from ..constants import (
    SM_ANALYSIS_GUI_EXE, SM_ANALYSIS_DESC, SHORT_LICENSE, PROJECT_WEBSITE_URL,
    PROJECT_DOCUMENTATION_URL
)
from .options import SM_ANALYSIS_OPTS
from .. import __version__, __author__, __years_copyright__

DEFAULT_IN_HELP_RE = re.compile(r"([(]default: [']?%[(]default[)]s[']?[)])")
METAVAR_IN_HELP_RE = re.compile(r"(%[(]metavar[)]s)")


def custom_Gooey(func=None, **other):
    return Gooey(
        menu=[{
            "name": "help",
            "items": [{
                'type': 'AboutDialog',
                'menuTitle': 'About',
                'name': 'sm-analysis (Pacbio Data Processing)',
                'description': 'Single Molecule Analysis of PacBio BAM files',
                'version': __version__,
                'copyright': __years_copyright__,
                'website': PROJECT_WEBSITE_URL,
                'developer': __author__,
                'license': SHORT_LICENSE
            },
            {
                'type': 'MessageDialog',
                'menuTitle': 'Description',
                'message': SM_ANALYSIS_DESC,
                'caption': 'sm-analysis-gui'
            },
            {
                'type': 'Link',
                'menuTitle': 'Documentation',
                'url': PROJECT_DOCUMENTATION_URL,
            }]
        }],
        default_size=(1024, 1024)
    )


def guiize_options(in_opts):
    """This functions takes a list of CL options and transforms
    them into a list suitable for sm-analysis-gui (with Gooey).
    """
    out_opts = []
    for opt in in_opts:
        kwords = opt[1].copy()
        metavar = kwords.get("metavar", "")
        help = kwords.get("help", "")
        name_or_flags = opt[0]

        version = (kwords.get("action") == "version")
        if version:
            continue

        if "FILE" in metavar or "PATH" in metavar:
            kwords["widget"] = "FileChooser"

        if metavar == "PATH":
            program = kwords.get("default", "")
            if program != "":
                kwords["metavar"] = f"{program} program"

        if help:
            help = DEFAULT_IN_HELP_RE.sub("", help).strip()
            help = METAVAR_IN_HELP_RE.sub(metavar, help).strip()
            kwords["help"] = help

        if metavar == "MOD-TYPE":
            kwords["widget"] = "Listbox"
            kwords["choices"] = kwords["default"]

        if metavar == "PARTITION:NUMBER-OF-PARTITIONS":
            help = f"(Syntax: {metavar})\n"+help.replace("--partition ", "")
            kwords["help"] = help
            metavar = ""

        if metavar in ("INT", "NUM"):
            kwords["widget"] = "IntegerField"
            if metavar == "NUM":
                kwords["gooey_options"] = {"min": 1}

        if ((metavar in ("INT", "FLOAT", "NUM", "MOD-TYPE", "")) or (
            name_or_flags[-1] in (
                "--aligned-CCS-bam-file", "--CCS-bam-file"))):
            kwords["metavar"] = name_or_flags[-1].replace("-", " ").strip()

        if kwords["metavar"] in ("verbose", "verbosity"):
            kwords["metavar"] += " level"

        out_opts.append((name_or_flags, kwords))
    return out_opts


@custom_Gooey()
def parse_input_sm_analysis():
    options = guiize_options(SM_ANALYSIS_OPTS)
    return parse_user_input(
        GooeyParser,
        SM_ANALYSIS_GUI_EXE, SM_ANALYSIS_DESC.split(".")[0], options
    )
