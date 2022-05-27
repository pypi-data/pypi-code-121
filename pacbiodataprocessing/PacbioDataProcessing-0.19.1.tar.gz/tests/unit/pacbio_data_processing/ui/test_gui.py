#######################################################################
#
# Copyright (C) 2021 David Palao
#
# This file is part of PacBioDataProcessing.
#
#  PacBioDataProcessing is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PacBioDataProcessing is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PacBioDataProcessing. If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import unittest
from unittest.mock import patch

from pacbio_data_processing.ui.gui import (
    parse_input_sm_analysis, custom_Gooey, guiize_options,
)
from pacbio_data_processing.ui.options import SM_ANALYSIS_OPTS
from pacbio_data_processing.constants import (
    SM_ANALYSIS_GUI_EXE, SM_ANALYSIS_DESC, SHORT_LICENSE
)
from pacbio_data_processing import __version__, __author__


@patch("pacbio_data_processing.ui.gui.guiize_options")
@patch("pacbio_data_processing.ui.gui.Gooey")
@patch("pacbio_data_processing.ui.gui.GooeyParser")
@patch("pacbio_data_processing.ui.gui.parse_user_input")
class ParseInputSmAnalysis(unittest.TestCase):
    def test_calls_parse_cl_program(
            self, pparse_ui, pGooeyParser, pGooey, pguiize):
        result = parse_input_sm_analysis()
        self.assertEqual(result, pparse_ui.return_value)
        pguiize.assert_called_once_with(SM_ANALYSIS_OPTS)
        pparse_ui.assert_called_once_with(
            pGooeyParser,
            SM_ANALYSIS_GUI_EXE,
            SM_ANALYSIS_DESC.split(".")[0],
            pguiize.return_value
        )

    def test_decorated(self, pparse_cl, pGooeyParser, pGooey, pguiize):
        self.assertTrue(
            parse_input_sm_analysis.__qualname__.startswith("Gooey")
        )


@patch("pacbio_data_processing.ui.gui.Gooey")
class CustomGooeyTestCase(unittest.TestCase):
    def test_calls_Gooey(self, pGooey):
        dec = custom_Gooey()
        pGooey.assert_called_once_with(
            menu=[{
                "name": "help",
                "items": [{
                    'type': 'AboutDialog',
                    'menuTitle': 'About',
                    'name': 'sm-analysis (Pacbio Data Processing)',
                    'description': (
                        'Single Molecule Analysis of PacBio BAM files'
                    ),
                    'version': __version__,
                    'copyright': '2020-2022',
                    'website': (
                        'https://gitlab.com/dvelazquez/pacbio-data-processing'
                    ),
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
                    'url': 'https://pacbio-data-processing.readthedocs.io/'
                }]
            }],
            default_size=(1024, 1024)
        )
        self.assertEqual(dec, pGooey.return_value)


class GuuizeOptionsTestCase(unittest.TestCase):
    def test_adds_widget_to_file_arguments(self):
        in_opts = [
            (("some",), {"metavar": "MY-FILE"}),
            (("another",), {"metavar": "PATH"}),
            (("hj",), {}),
        ]
        out_opts = guiize_options(in_opts)
        for opt in out_opts[:2]:
            self.assertEqual(opt[1]["widget"], "FileChooser")

    def test_replaces_metavars(self):
        in_opts = [
            (("-b", "--blasr-path"),
                 {"metavar": "PATH", "default": "blasr"}),
            (("-p", "--pbindex-path"),
                 {"metavar": "PATH", "default": "pbindex"}),
            (("-i", "--ipdsummary-path"),
                 {"metavar": "PATH", "default": "ipdSummary"}),
            (("hj",), {}),
            (("-C", "--aligned-CCS-bam-file"), dict(metavar="BAM-FILE")),
            (("-c", "--CCS-bam-file"), dict(metavar="BAM-FILE")),

        ]
        out_opts = guiize_options(in_opts)
        self.assertEqual(out_opts[0][1]["metavar"], "blasr program")
        self.assertEqual(out_opts[1][1]["metavar"], "pbindex program")
        self.assertEqual(out_opts[2][1]["metavar"], "ipdSummary program")
        self.assertEqual(out_opts[3][1]["metavar"], "hj")
        self.assertEqual(out_opts[4][1]["metavar"], "aligned CCS bam file")
        self.assertEqual(out_opts[5][1]["metavar"], "CCS bam file")

    def test_default_refs_in_help_str_removed(self):
        in_opts = [
            (("some",), {"help": "Yes (default: '%(default)s')"}),
            (("another",), {"help": "No without default"}),
            (("more",), {"help": "dd (default: %(default)s)"}),
            (("helpless",), {}),
        ]
        expected_values = ["Yes", "No without default", "dd"]
        out_opts = guiize_options(in_opts)
        for opt, expected in zip(out_opts, expected_values):
            self.assertEqual(opt[1]["help"], expected)

    def test_metavar_refs_in_help_str_removed(self):
        in_opts = [
            (("some",), {"help": "Yes %(metavar)s", "metavar": "MK"}),
            (("another",), {"help": "without metavars"}),
            (("metavarless",), {}),
        ]
        expected_values = ["Yes MK", "without metavars"]
        out_opts = guiize_options(in_opts)
        for opt, expected in zip(out_opts, expected_values):
            self.assertEqual(opt[1]["help"], expected)

    def test_metavar_adjusted_to_be_title(self):
        in_opts = [
            (("-s", "--some-num"), {"metavar": "INT"}),
            (("another",), {"metavar": "FLOAT"}),
            (("onemore",), {"metavar": "NUM"}),
            (("metavarless",), {}),
        ]
        expected_values = ["some num", "another", "onemore"]
        out_opts = guiize_options(in_opts)
        for opt, expected in zip(out_opts, expected_values):
            self.assertEqual(opt[1]["metavar"], expected)

    def test_int_gets_custom_widget(self):
        in_opts = [
            (("-s", "--some-num"), {"metavar": "INT"}),
            (("another",), {"metavar": "FLOAT"}),
            (("onemore",), {"metavar": "NUM"}),
            (("metavarless",), {}),
        ]
        out_opts = guiize_options(in_opts)
        for idx in (0, 2):
            self.assertEqual(out_opts[idx][1]["widget"], "IntegerField")

    def test_NUM_has_min_1(self):
        in_opts = [
            (("-s", "--some-num"), {"metavar": "INT"}),
            (("another",), {"metavar": "FLOAT"}),
            (("onemore",), {"metavar": "NUM"}),
            (("metavarless",), {}),
        ]
        out_opts = guiize_options(in_opts)
        self.assertEqual(out_opts[2][1]["gooey_options"], {"min": 1})
        with self.assertRaises(KeyError):
            for idx in (0, 1, 3):
                out_opts[idx][1]["gooey_options"]

    def test_mod_types_with_Listbox_widget(self):
        in_opts = [
            (("-m", "--modification-types"),
                 {"metavar": "MOD-TYPE", "default": ["X32"], "nargs": "+"})
        ]
        out_opts = guiize_options(in_opts)
        self.assertEqual(out_opts[0][1]["metavar"], "modification types")
        self.assertEqual(out_opts[0][1]["widget"], "Listbox")
        self.assertEqual(out_opts[0][1]["choices"], ["X32"])

    def test_dashes_not_in_title(self):
        in_opts = [(("--only-produce-methylation-report",),
            dict(action="store_true"))
        ]
        out_opts = guiize_options(in_opts)
        self.assertEqual(
            out_opts[0][1]["metavar"],
            "only produce methylation report"
        )

    def test_partition_title_and_help(self):
        in_opts = [(("-P", "--partition"),
                    dict(metavar="PARTITION:NUMBER-OF-PARTITIONS",
                         help=(
                             "this option instructs the program to only analyze"
                             " a fraction (partition) of the molecules present "
                             "in the input bam file. The file is divided in "
                             "`NUMBER OF PARTITIONS` (almost) equal pieces "
                             "but ONLY the PARTITION-th partition (fraction) "
                             "is analyzed. For instance, `--partition 3:7` "
                             "means that the bam file is divided in seven "
                             "pieces but only the third piece is analyzed "
                             "(by default all the file is analyzed)"
                         )
                    )
            )
        ]
        out_opts = guiize_options(in_opts)
        self.assertEqual(out_opts[0][1]["metavar"], "partition")
        self.assertNotIn("--partition", out_opts[0][1]["help"])
        self.assertIn(
            "(Syntax: PARTITION:NUMBER-OF-PARTITIONS)", out_opts[0][1]["help"])

    def test_version_not_there(self):
        in_opts = [
            (("--version",), {"action": "version"}),
            (("another",), {"metavar": "FLOAT"}),
            (("onemore",), {"metavar": "NUM"}),
            (("metavarless",), {}),
        ]
        out_opts = guiize_options(in_opts)
        self.assertEqual(len(out_opts), 3)
        for opt in out_opts:
            with self.assertRaises(KeyError):
                opt[1]["action"]

    def test_verbose_moved_to_verbose_level(self):
        in_opts = [
            (("-v", "--verbose"), {"action": "count"}),
            (("--verbosity",), {})
        ]
        out_opts = guiize_options(in_opts)
        for idx, opt in enumerate(out_opts):
            expected = in_opts[idx][0][-1].replace("-", "")+ " level"
            self.assertEqual(opt[1]["metavar"], expected)
