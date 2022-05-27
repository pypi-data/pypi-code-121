#######################################################################
#
# Copyright (C) 2021, 2022 David Palao
#
# This file is part of PacBio data processing.
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
import logging

from pacbio_data_processing.logs import config_logging
from pacbio_data_processing.utils import AlmostUUID


@patch("pacbio_data_processing.logs.logging.basicConfig")
class ConfigLoggingTestCase(unittest.TestCase):
    def test_calls_basic_config_with_no_verbosity(self, pbasicConfig):
        with patch.object(AlmostUUID, "_short_str", "abcd6"):
            config_logging(0)
        pbasicConfig.assert_called_once_with(
            level=logging.INFO,
            format="[%(asctime)-15s][abcd6][%(levelname)s] %(message)s"
        )

    def test_calls_basic_config_with_verbosity(self, pbasicConfig):
        with patch.object(AlmostUUID, "_short_str", "57a7b"):
            config_logging(1)
        pbasicConfig.assert_called_once_with(
            level=logging.DEBUG,
            format="[%(asctime)-15s][57a7b][%(levelname)s] %(message)s"
        )
