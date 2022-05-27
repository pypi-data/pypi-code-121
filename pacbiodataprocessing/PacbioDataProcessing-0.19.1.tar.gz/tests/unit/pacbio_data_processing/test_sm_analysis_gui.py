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
#  PacBio data processing is distributed in the hope that it will be useful,
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

from pacbio_data_processing.sm_analysis_gui import main_gui


@patch("pacbio_data_processing.sm_analysis_gui._main")
@patch("pacbio_data_processing.sm_analysis_gui.parse_input_from_gui")
class MainGUIFunctionTestCase(unittest.TestCase):
    def test_parses_cl(
            self, pparse_gui, pmain):
        main_gui()
        pparse_gui.assert_called_once_with()

    def test_calls_main(
            self, pparse_gui, pmain):
        main_gui()
        pmain.assert_called_once_with(pparse_gui.return_value)


class HighLevelErrorsTestCase(unittest.TestCase):
    @patch("pacbio_data_processing.sm_analysis_gui.parse_input_from_gui")
    def test_main_gui_does_not_crashes_if_exception(self, pparse_gui):
        pparse_gui.side_effect = Exception("jo ja")
        with self.assertLogs() as cm:
            main_gui()
        self.assertEqual(cm.output, ["CRITICAL:root:jo ja"])


