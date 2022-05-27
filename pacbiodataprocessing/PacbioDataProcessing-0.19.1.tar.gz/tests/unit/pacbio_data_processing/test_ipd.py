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
from unittest.mock import patch, call
from pathlib import Path
from subprocess import CompletedProcess

from pacbio_data_processing.ipd import (
    ipd_summary, multi_ipd_summary_direct, multi_ipd_summary_threads,
    multi_ipd_summary,
)
from pacbio_data_processing.bam_utils import Molecule
from pacbio_data_processing.constants import DEFAULT_IPDSUMMARY_PROGRAM


@patch("pacbio_data_processing.ipd.subprocess.run")
class IdpSummaryTestCase(unittest.TestCase):
    def test_calls_run(self, prun):
        for model in (None, "some"):
            ipd_summary(
                (4, Molecule(4, Path("/a/b.bam"))), Path("/tmp/x.fasta"),
                Path(DEFAULT_IPDSUMMARY_PROGRAM), 7,
                "7/,ñ,=", model, False
            )
            signature = (
                DEFAULT_IPDSUMMARY_PROGRAM, Path("/a/b.bam"),
                "--reference", Path("/tmp/x.fasta"), "--identify", "7/,ñ,=",
                "--numWorkers", "7", "--gff", Path("/a/b.gff")
            )
            if model:
                signature = signature + ("--ipdModel", "some")
            prun.assert_called_once_with(signature, capture_output=True)
            prun.reset_mock()

    def test_ipd_summary_ok(self, prun):
        self.maxDiff = None
        program = "a"/Path(DEFAULT_IPDSUMMARY_PROGRAM)
        molecule = Molecule(6, Path("/tmp/ss.killme"))
        in_params = (
            ((6, molecule), "f.asta", program, 3, "a,v,b", "P55", False)
        )
        ipdsummary_output = b"many, many ugly things"
        expected_ipd_output = ipdsummary_output.decode()
        prun.return_value = CompletedProcess(
            (program,)+in_params, 0, stdout=ipdsummary_output)
        with self.assertLogs(level="DEBUG") as cm:
            result = ipd_summary(*in_params)
        self.assertEqual(result, (6, molecule))
        self.assertEqual(
            molecule.gff_path,
            molecule.src_bam_path.with_suffix(".gff")
        )
        expected_clos = (
            f"{program} /tmp/ss.killme --reference f.asta --identify a,v,b "
            "--numWorkers 3 --gff /tmp/ss.gff --ipdModel P55"
        )
        self.assertEqual(
            [f"DEBUG:root:[{program.name}] Called as follows:",
             f"DEBUG:root:[{program.name}] '{expected_clos}'",
             f"DEBUG:root:[{program.name}] Output:",
             f"DEBUG:root:[{program.name}] {expected_ipd_output}"],
            cm.output
        )

    def test_ipd_summary_gives_error(self, prun):
        program = "/tmp"/Path(DEFAULT_IPDSUMMARY_PROGRAM)
        molecule = Molecule(6, Path("/tmp/ss.killme"))
        in_params = (
            ((6, molecule), "f.asta", program, 3, "a,v,b", "P55", False)
        )
        errmsg = b" Crack!\n"
        prun.return_value = CompletedProcess(
            (program,)+in_params, 1, stderr=errmsg)
        with self.assertLogs(level="DEBUG") as cm:
            result = ipd_summary(*in_params)
        self.assertIs(result, None)
        self.assertIs(molecule.gff_path, None)
        self.assertEqual(
            [f"ERROR:root:[{program.name}] Molecule 6 could not be processed",
             f"DEBUG:root:[{program.name}] The reported error was:",
             f"DEBUG:root:[{program.name}]     'Crack!'"],
            cm.output
        )
        self.assertTrue(molecule.had_processing_problems)


@patch("pacbio_data_processing.ipd.ipd_summary")
class MultiIpdSummaryTestCase(unittest.TestCase):
    IMPLEMENTATIONS = (multi_ipd_summary_direct, multi_ipd_summary_threads)

    def setUp(self):
        self.molecules = [
            (i, Molecule(i, Path(f"{bam}.bam"))) for i, bam in enumerate("abc")
        ]
        self.args = (
            self.molecules, Path("/tmp/x.fasta"),
            DEFAULT_IPDSUMMARY_PROGRAM, 1, 1,
            ["7/", "ñ", "="], None, False
        )

    def test_calls_ipd_summary(self, pipd_summary):
        for imulti_ipd_summary in self.IMPLEMENTATIONS:
            expected_calls = [
                call(
                    m, fasta=Path("/tmp/x.fasta"),
                    program=DEFAULT_IPDSUMMARY_PROGRAM,
                    nprocs=1, mod_types_comma_sep="7/,ñ,=",
                    ipd_model=None, skip_if_present=False)
                for m in self.molecules
            ]
            list(imulti_ipd_summary(*self.args))
            pipd_summary.assert_has_calls(expected_calls, any_order=True)
            pipd_summary.reset_mock()

    def test_returns_an_iterable(self, pipd_summary):
        for imulti_ipd_summary in self.IMPLEMENTATIONS:
            pipd_summary.side_effect = [8 for _ in self.molecules]
            result = imulti_ipd_summary(*self.args)
            self.assertEqual(list(result), [8 for _ in self.molecules])

    def test_default_implementation(self, pipd_summary):
        self.assertEqual(multi_ipd_summary, multi_ipd_summary_threads)

    def test_Nones_are_not_yielded(self, pipd_summary):
        last_mol = self.molecules.pop()
        # I want to have None *not* as the last element:
        self.molecules.append(None)
        self.molecules.append(last_mol)
        for imulti_ipd_summary in self.IMPLEMENTATIONS:
            pipd_summary.side_effect = self.molecules
            result = list(imulti_ipd_summary(*self.args))
            self.assertNotIn(None, result)
            for item in result:
                self.assertIn(item, self.molecules)
            self.assertEqual(len(result), len(self.molecules)-1)
