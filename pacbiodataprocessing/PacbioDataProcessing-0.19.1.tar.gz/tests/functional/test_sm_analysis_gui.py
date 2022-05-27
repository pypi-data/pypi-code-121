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

import subprocess

from pacbio_data_processing.constants import SM_ANALYSIS_GUI_EXE

from .utils import killall_later


class TestCaseGUISmoke:
    """This is a smoky suite of tests. The idea behind them is:
    I test the real functionality of sm-analysis in the other FT
    suites and I define some UTs that play the role of
    *subcutaneous tests*, ie, the testing strategy is:

    1. Within this FTs I ensure a minimal expected behavior of a GUI
       (basically: there is a gui program that stays open until killed).
    2. Subcutanous tests: ensure that the gui executable is linked to
       a function that uses Gooey for parsing.
    3. UTs: the GUI functionality is delegated to Gooey. Calls to
       Gooey are fully mocked.

    THIS class is in charge of 1.

    In the future, a better testing strategy could be devised.
    """
    def test_gui_started(self):
        # Nathan is glad to see that there is a GUI version of
        # 'sm-analysis'. It is called 'sm-analysis-gui'.
        # He runs it:
        p = subprocess.Popen([SM_ANALYSIS_GUI_EXE])
        # and indeed the program is running!
        # This version of the program will be very useful
        # for some colleagues that are not big fans of the
        # terminal. For now he quits:
        killall_later(SM_ANALYSIS_GUI_EXE, 1)
