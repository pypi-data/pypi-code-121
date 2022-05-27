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

import unittest
from unittest.mock import patch, Mock
from pathlib import Path
import logging

from pacbio_data_processing.external import Blasr, CCS
from pacbio_data_processing.sentinel import (
    SentinelFileFound, SentinelFileNotFound
)


@patch("pacbio_data_processing.external.Sentinel")
@patch("pacbio_data_processing.external.subprocess.run")
class BlasrTestCase(unittest.TestCase):
    def setUp(self):
        self.blasr = Blasr("myblasr")

    @patch("pacbio_data_processing.external.Path")
    def test_call_to_instance_goes_well(self, pPath, prun, pSentinel):
        outmock = Mock()
        outmock.exists.return_value = True

        def constructor(path):
            if str(path) == "wendol.bam":
                return outmock

        pPath.side_effect = constructor
        prun.return_value.returncode = 0
        with self.assertLogs(level="INFO") as cm:
            blasr_ret = self.blasr(
                "my.bam", Path("my.fasta"), "wendol.bam"
            )
        prun.assert_called_once_with(
            ("myblasr", "my.bam", "my.fasta",
             "--nproc", "1", "--bam", "--out", "wendol.bam",),
            capture_output=True
        )
        self.assertEqual(blasr_ret, 0)
        self.assertEqual(
            cm.output,
            ["INFO:root:[blasr] Aligned file 'wendol.bam' generated"]
        )

    @patch("pacbio_data_processing.external.Path")
    def test_call_to_instance_does_not_err_but_no_output(
            self, pPath, prun, pSentinel):
        outmock = Mock()
        outmock.exists.return_value = False

        def constructor(path):
            if str(path) == "wendol.bam":
                return outmock

        pPath.side_effect = constructor
        prun.return_value.returncode = 0
        with self.assertLogs(level="INFO") as cm:
            # until Python-3.10, this is a workaround:
            logging.warning("dummy output")
            blasr_ret = self.blasr(
                "my.bam", Path("my.fasta"), "wendol.bam"
            )
        prun.assert_called_once_with(
            ("myblasr", "my.bam", "my.fasta",
             "--nproc", "1", "--bam", "--out", "wendol.bam",),
            capture_output=True
        )
        self.assertEqual(blasr_ret, 0)
        self.assertEqual(
            cm.output,
            ["WARNING:root:dummy output"]
        )

    def test_error_logged_if_blasr_didnt_work_well(self, prun, pSentinel):
        prun.return_value.returncode = 1
        prun.return_value.stderr = b"wonderful error"
        with self.assertLogs() as cm:
            res = self.blasr("my.bam", Path("my.fasta"), "wendol.bam")
        self.assertEqual(
            cm.output,
            [
                ("ERROR:root:[blasr] 'myblasr' could not align the input file "
                 "'my.bam'"),
                ("ERROR:root:[blasr] During the execution of 'myblasr' an "
                 "error occurred"),
                "ERROR:root:[blasr] The following command was issued:",
                ("ERROR:root:    'myblasr my.bam my.fasta --nproc 1 --bam "
                 "--out wendol.bam'"),
                ("ERROR:root:[blasr] ...the error message was: "
                 "'wonderful error'")
            ]
        )
        self.assertIs(res, 1)

    def test_blasr_didnt_work_well_but_not_error_msg(self, prun, pSentinel):
        prun.return_value.returncode = 1
        prun.return_value.stderr = b"\n "
        with self.assertLogs() as cm:
            res = self.blasr("my.bam", Path("my.fasta"), "wendol.bam")
        self.assertEqual(
            cm.output,
            [
                ("ERROR:root:[blasr] 'myblasr' could not align the input file "
                 "'my.bam'"),
                ("ERROR:root:[blasr] During the execution of 'myblasr' an "
                 "error occurred"),
                "ERROR:root:[blasr] The following command was issued:",
                ("ERROR:root:    'myblasr my.bam my.fasta --nproc 1 --bam "
                 "--out wendol.bam'"),
                ("ERROR:root:[blasr] ...but the program did not report any "
                 "error message.")
            ]
        )
        self.assertIs(res, 1)

    def test_can_be_called_with_different_number_of_procs(
            self, prun, pSentinel):
        self.blasr(
            "m.bam", Path("m.fasta"), "blasr.m.bam", nprocs=7
        )
        prun.assert_called_once_with(
            ("myblasr", "m.bam", "m.fasta",
             "--nproc", "7", "--bam", "--out", "blasr.m.bam",),
            capture_output=True
        )

    def test_creates_wip_sentinel_while_aligner_runs(self, prun, pSentinel):
        self.blasr("mi.bam", "mi.fasta", "blasr.mi.bam")
        pSentinel.assert_called_once_with(Path("blasr.mi.bam"))
        pSentinel.return_value.__enter__.assert_called_once_with()
        pSentinel.return_value.__exit__.assert_called_once_with(
            None, None, None)

    def test_wip_sentinel_calls_exit_even_if_Exception(self, prun, pSentinel):
        prun.side_effect = RuntimeError("oh-oh!")
        try:
            self.blasr("mi.bam", "mi.fasta", "blasr.mi.bam")
        except RuntimeError:
            pSentinel.return_value.__exit__.assert_called()
        else:
            self.fail("Must raise!")

    def test_sentinel_file_exists_before_running_blasr(self, prun, pSentinel):
        pSentinel.return_value.__enter__.side_effect = SentinelFileFound
        ssentinel = str(pSentinel.return_value.path)
        with self.assertLogs() as cm:
            res = self.blasr("mi.bam", "mi.fasta", "blasr.mi.bam")
        self.assertEqual(
            cm.output,
            [f"WARNING:root:Sentinel file '{ssentinel}' detected! "
             "Delaying blasr computation."]
        )
        self.assertIs(res, None)
        prun.assert_not_called()

    def test_sentinel_file_doesnt_exist_after_blasr(self, prun, pSentinel):
        pSentinel.return_value.__exit__.side_effect = SentinelFileNotFound
        ssentinel = str(pSentinel.return_value.path)
        with self.assertLogs() as cm:
            res = self.blasr("mi.bam", "mi.fasta", "blasr.mi.bam")
        self.assertEqual(
            cm.output,
            [f"WARNING:root:Sentinel file '{ssentinel}' disappeared "
             "before blasr finished its computation!",
             "WARNING:root: ...some other person/process is probably carrying "
             "out a similar computation in the same directory and messing up.",
             ("WARNING:root:    The integrity of the results may be "
              "compromised!")
             ]
        )
        self.assertEqual(res, prun.return_value.returncode)


@patch("pacbio_data_processing.external.Sentinel")
@patch("pacbio_data_processing.external.subprocess.run")
class CCSTestCase(unittest.TestCase):
    def setUp(self):
        self.ccs = CCS("myccs")

    @patch("pacbio_data_processing.external.Path")
    def test_call_to_instance_goes_well(self, pPath, prun, pSentinel):
        outmock = Mock()
        outmock.exists.return_value = True

        def constructor(path):
            if str(path) == "wendol.bam":
                return outmock

        pPath.side_effect = constructor
        prun.return_value.returncode = 0
        with self.assertLogs(level="INFO") as cm:
            ccs_ret = self.ccs("my.bam", "wendol.bam")
        prun.assert_called_once_with(
            ("myccs", "my.bam", "wendol.bam",),
            capture_output=True
        )
        self.assertEqual(ccs_ret, 0)
        self.assertEqual(
            cm.output,
            ["INFO:root:[ccs] File 'wendol.bam' generated"]
        )

    @patch("pacbio_data_processing.external.Path")
    def test_call_to_instance_does_not_err_but_no_output(
            self, pPath, prun, pSentinel):
        outmock = Mock()
        outmock.exists.return_value = False

        def constructor(path):
            if str(path) == "wendol.bam":
                return outmock

        pPath.side_effect = constructor
        prun.return_value.returncode = 0
        with self.assertLogs(level="INFO") as cm:
            # until Python-3.10, this is a workaround:
            logging.warning("dummy output")
            ccs_ret = self.ccs("my.bam", "wendol.bam")
        prun.assert_called_once_with(
            ("myccs", "my.bam", "wendol.bam",),
            capture_output=True
        )
        self.assertEqual(ccs_ret, 0)
        self.assertEqual(
            cm.output,
            ["WARNING:root:dummy output"]
        )

    def test_error_logged_if_CCS_didnt_work_well(self, prun, pSentinel):
        prun.return_value.returncode = 1
        prun.return_value.stderr = b"wonderful error"
        with self.assertLogs() as cm:
            res = self.ccs("my.bam", "wendol.bam")
        self.assertEqual(
            cm.output,
            [
                ("ERROR:root:[ccs] During the execution of 'myccs' an error "
                 "occurred"),
                "ERROR:root:[ccs] The following command was issued:",
                "ERROR:root:    'myccs my.bam wendol.bam'",
                "ERROR:root:[ccs] ...the error message was: 'wonderful error'"
            ]
        )
        self.assertIs(res, 1)

    def test_CCS_didnt_work_well_but_no_error_msg(self, prun, pSentinel):
        prun.return_value.returncode = 1
        prun.return_value.stderr = b"\n "
        with self.assertLogs() as cm:
            res = self.ccs("my.bam", "wendol.bam")
        self.assertEqual(
            cm.output,
            [
                ("ERROR:root:[ccs] During the execution of 'myccs' an error "
                 "occurred"),
                "ERROR:root:[ccs] The following command was issued:",
                "ERROR:root:    'myccs my.bam wendol.bam'",
                ("ERROR:root:[ccs] ...but the program did not report any "
                 "error message.")
            ]
        )
        self.assertIs(res, 1)

    def test_creates_wip_sentinel_while_ccs_runs(self, prun, pSentinel):
        self.ccs("mi.bam", "ccs.mi.bam")
        pSentinel.assert_called_once_with(Path("ccs.mi.bam"))
        pSentinel.return_value.__enter__.assert_called_once_with()
        pSentinel.return_value.__exit__.assert_called_once_with(
            None, None, None)

    def test_wip_sentinel_calls_exit_even_if_Exception(self, prun, pSentinel):
        prun.side_effect = RuntimeError("oh-oh!")
        try:
            self.ccs("mi.bam", "ccs.mi.bam")
        except RuntimeError:
            pSentinel.return_value.__exit__.assert_called()
        else:
            self.fail("Must raise!")

    def test_sentinel_file_exists_before_running_ccs(self, prun, pSentinel):
        pSentinel.return_value.__enter__.side_effect = SentinelFileFound
        ssentinel = str(pSentinel.return_value.path)
        with self.assertLogs() as cm:
            res = self.ccs("mi.bam", "ccs.mi.bam")
        self.assertEqual(
            cm.output,
            [f"WARNING:root:Sentinel file '{ssentinel}' detected! "
             "Delaying ccs computation."]
        )
        self.assertIs(res, None)
        prun.assert_not_called()

    def test_sentinel_file_doesnt_exist_after_ccs(self, prun, pSentinel):
        pSentinel.return_value.__exit__.side_effect = SentinelFileNotFound
        ssentinel = str(pSentinel.return_value.path)
        with self.assertLogs() as cm:
            res = self.ccs("mi.bam", "ccs.mi.bam")
        self.assertEqual(
            cm.output,
            [f"WARNING:root:Sentinel file '{ssentinel}' disappeared "
             "before ccs finished its computation!",
             "WARNING:root: ...some other person/process is probably carrying "
             "out a similar computation in the same directory and messing up.",
             ("WARNING:root:    The integrity of the results may be "
              "compromised!")
             ]
        )
        self.assertEqual(res, prun.return_value.returncode)
