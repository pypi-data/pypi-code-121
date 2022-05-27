#######################################################################
#
# Copyright (C) 2022 David Palao
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
from unittest.mock import MagicMock, call, patch, PropertyMock
from pathlib import Path

from pacbio_data_processing.sentinel import (
    Sentinel, SentinelFileFound, SentinelFileNotFound,
    SLEEP_SECONDS as SENTINEL_SLEEP_SECONDS,
    TOO_OLD_AGE_SECONDS as SENTINEL_TOO_OLD_AGE_SECONDS
)


@patch("pacbio_data_processing.sentinel.time")
class SentinelTestCase(unittest.TestCase):
    def setUp(self):
        with (patch(
                "pacbio_data_processing.sentinel.ThreadPoolExecutor") as pool,
              patch("pacbio_data_processing.sentinel.Sentinel."
                    "is_file_too_old", new_callable=PropertyMock) as is_old
              ):
            is_old.return_value = False
            self.is_old = is_old
            self.s = Sentinel(Path("a"))
            self.s1 = Sentinel(Path("c"))
            self.s2 = Sentinel(Path("c"))
            self.s3 = Sentinel(Path("C"))
        ppath = MagicMock()
        self.s.path = ppath
        self.thpool = pool

    def test_has_deterministic_path_attribute(self, ptime):
        self.assertEqual(self.s1.path, self.s2.path)
        self.assertNotEqual(self.s1.path, self.s3.path)

    def test_has_executor(self, ptime):
        self.assertEqual(self.s._executor, self.thpool.return_value)

    def test_at_enter_creates_file_and_its_removed_at_exit(self, ptime):
        def create(exist_ok=True):
            self.s.path.exists.return_value = True

        def delete():
            self.s.path.exists.return_value = False

        self.s.path.touch.side_effect = create
        self.s.path.unlink.side_effect = delete
        with self.s:
            self.assertTrue(self.s.path.exists())
        self.assertFalse(self.s.path.exists())
        self.s.path.touch.assert_called_once_with(exist_ok=False)
        self.s._executor.submit.assert_called_once_with(self.s._anti_aging)

    def test_raises_if_file_found_at_enter(self, ptime):
        self.s.path.touch.side_effect = FileExistsError
        ptime.time.return_value = 1000
        self.s.path.stat.return_value.st_mtime = 999
        with self.assertRaises(SentinelFileFound):
            with self.s:
                ...
        self.s._executor.submit.assert_not_called()

    def test_raises_if_file_not_found_at_exit(self, ptime):
        self.s.path.unlink.side_effect = FileNotFoundError
        with self.assertRaises(SentinelFileNotFound):
            with self.s:
                ...

    def test_anti_aging(self, ptime):
        self.s.path.exists.side_effect = (True, True, False)
        self.s._anti_aging()
        self.s.path.touch.assert_has_calls([call(), call()])
        ptime.sleep.assert_has_calls(
            [call(SENTINEL_SLEEP_SECONDS),
             call(SENTINEL_SLEEP_SECONDS)
             ]
        )

    def test_normal_behaviour_if_sentinel_file_too_old(self, ptime):
        def create(exist_ok):
            self.s.path.exists.return_value = True
            if exist_ok is False:
                raise FileExistsError()

        def delete():
            self.s.path.exists.return_value = False

        self.s.path.touch.side_effect = create
        self.s.path.unlink.side_effect = delete
        self.is_old.return_value = True
        with patch("pacbio_data_processing.sentinel.Sentinel."
                   "is_file_too_old", new_callable=PropertyMock) as is_old:
            is_old.return_value = True
            with self.assertLogs() as cm:
                with self.s:
                    self.assertTrue(self.s.path.exists())
                self.assertFalse(self.s.path.exists())
        self.s.path.touch.assert_has_calls(
            [call(exist_ok=False),
             call(exist_ok=True)
             ]
        )
        self.s._executor.submit.assert_called_once_with(self.s._anti_aging)
        self.assertEqual(
            cm.output,
            [f"INFO:root:Abandoned sentinel '{self.s.path}' "
             "detected; overwritten."]
        )

    def test_is_file_too_old(self, ptime):
        self.s.path.exists.return_value = True
        baseline = 1200.0
        ptime.time.return_value = baseline
        self.s.path.stat.return_value.st_mtime = (
            baseline-SENTINEL_TOO_OLD_AGE_SECONDS+1)
        self.assertFalse(self.s.is_file_too_old)
        self.s.path.stat.return_value.st_mtime = (
            baseline-SENTINEL_TOO_OLD_AGE_SECONDS-1)
        self.assertTrue(self.s.is_file_too_old)

    def test_is_file_too_old_is_false_if_no_file(self, ptime):
        self.s.path.exists.return_value = False
        self.assertFalse(self.s.is_file_too_old)
