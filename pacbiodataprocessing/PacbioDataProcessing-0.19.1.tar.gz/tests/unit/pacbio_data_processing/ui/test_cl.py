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
from pathlib import Path
from io import StringIO
import sys
import re

from pacbio_data_processing.ui.cl import (
    parse_cl_sm_analysis, parse_cl_bam_filter,
)
from pacbio_data_processing.ui.options import (
    BAM_FILE_METAVAR, INPUT_BAM_FILE_HELP,
    ALIGNMENT_FILE_METAVAR, FASTA_FILE_HELP,
)
from pacbio_data_processing.constants import SM_ANALYSIS_DESC, BAM_FILTER_DESC
from pacbio_data_processing import __version__


class ParseCLMixIn:
    @patch('sys.stdout', new_callable=StringIO)
    def test_help_message(self, pstdout):
        with patch.object(sys, "argv", [self.program_name, "-h"]):
            with self.assertRaises(SystemExit):
                self.parse_cl()
        output = pstdout.getvalue()
        output = re.sub(r"\s+", " ", output)
        self.assertIn(self.desc_msg, output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mandatory_arguments(self, pstderr):
        with patch.object(sys, "argv", [self.program_name]):
            with self.assertRaises(SystemExit):
                self.parse_cl()
        output = pstderr.getvalue()
        self.assertIn("error: the following arguments are required:", output)
        for arg in self.mandatory_args:
            self.assertIn(arg, output)

    def test_verbose_argument(self):
        clos = [self.program_name] + self.dummy_mandatory_args
        for numv in range(len(self.mandatory_args)+1):
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.verbose, numv)
            clos.append("-v")

    def test_version_argument(self):
        clos = [self.program_name, "--version"]
        with patch('sys.stdout', new_callable=StringIO) as pstdout:
            with patch.object(sys, "argv", clos):
                with self.assertRaises(SystemExit):
                    self.parse_cl()
            output = pstdout.getvalue()
            self.assertEqual(output.strip(), __version__)


class ParseCLSMAnalysisTestCase(ParseCLMixIn, unittest.TestCase):
    program_name = "sm-analysis"
    desc_msg = SM_ANALYSIS_DESC
    mandatory_args = (BAM_FILE_METAVAR, ALIGNMENT_FILE_METAVAR)
    dummy_mandatory_args = ["a", "b"]

    @staticmethod
    def parse_cl():
        return parse_cl_sm_analysis()

    def test_mandatory_input_files_are_Path_instances(self):
        with patch.object(
                sys, "argv", [self.program_name, "junacho", "asnother"]):
            args = self.parse_cl()
        self.assertEqual(args.input_bam_file, Path("junacho"))
        self.assertEqual(args.fasta, Path("asnother"))

    @patch('sys.stdout', new_callable=StringIO)
    def test_help_on_options(self, pstdout):
        # I think this test is irrelevant if FTs check this...
        with patch.object(sys, "argv", [self.program_name, "-h"]):
            with self.assertRaises(SystemExit):
                self.parse_cl()
        output = pstdout.getvalue()
        output = re.sub(r"\s+", " ", output)
        self.assertIn(BAM_FILE_METAVAR, output)
        self.assertIn(INPUT_BAM_FILE_HELP, output)
        self.assertIn(
            FASTA_FILE_HELP % {"metavar": ALIGNMENT_FILE_METAVAR}, output)

    def test_ipd_model_argument(self):
        for flag in ("-M", "--ipd-model"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "what/cuncho"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.ipd_model, Path("what/cuncho"))

    def test_blasr_argument(self):
        for flag in ("-b", "--blasr-path"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "what/cuncho"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.blasr_path, "what/cuncho")

    def test_pbindex_argument(self):
        for flag in ("-p", "--pbindex-path"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "what/cuncho"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.pbindex_path, Path("what/cuncho"))

    def test_ipdsummary_argument(self):
        for flag in ("-i", "--ipdsummary-path"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "what/cuncho"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.ipdsummary_path, Path("what/cuncho"))

    def test_num_simultaneous_ipdsummarys_argument(self):
        for flag in ("-N", "--num-simultaneous-ipdsummarys"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "7"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.num_simultaneous_ipdsummarys, 7)

    def test_num_workers_per_ipdsummary_argument(self):
        for flag in ("-n", "--num-workers-per-ipdsummary"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "5"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.num_workers_per_ipdsummary, 5)

    def test_nprocs_blasr_argument(self):
        clos = [
            self.program_name] + self.dummy_mandatory_args + [
            "--nprocs-blasr", "3"
        ]
        with patch.object(sys, "argv", clos):
            args = self.parse_cl()
        self.assertEqual(args.nprocs_blasr, 3)

    def test_partition_argument(self):
        for flag in ("-P", "--partition"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "5:23"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.partition, "5:23")

    def test_aligned_CCS_bam_file_argument(self):
        for flag in ("-C", "--aligned-CCS-bam-file"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "cuate"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.aligned_CCS_bam_file, Path("cuate"))

    def test_keep_temp_dir_argument(self):
        flags = (["--keep-temp-dir"], [])
        results = (True, False)
        for flag, result in zip(flags, results):
            clos = [
                self.program_name] + self.dummy_mandatory_args + flag
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.keep_temp_dir, result)

    def test_modification_types_argument(self):
        for flag in ("-m", "--modification-types"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "x", "ssd", "HDD"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.modification_types, ["x", "ssd", "HDD"])

    def test_only_produce_methlation_report(self):
        flags = (["--only-produce-methylation-report"], [])
        results = (True, False)
        for flag, result in zip(flags, results):
            clos = [
                self.program_name] + self.dummy_mandatory_args + flag
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.only_produce_methylation_report, result)

    def test_CCS_bam_file_argument(self):
        for flag in ("-c", "--CCS-bam-file"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "tomate"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.CCS_bam_file, Path("tomate"))


class ParseCLBamFilterTestCase(ParseCLMixIn, unittest.TestCase):
    program_name = "bam-filter"
    desc_msg = BAM_FILTER_DESC
    mandatory_args = (BAM_FILE_METAVAR,)
    dummy_mandatory_args = ["a"]

    @staticmethod
    def parse_cl():
        return parse_cl_bam_filter()

    def test_mandatory_input_file_is_a_Path_instance(self):
        with patch.object(sys, "argv", [self.program_name, "jasnother"]):
            args = self.parse_cl()
        self.assertEqual(args.input_bam_file, Path("jasnother"))

    def test_min_dna_seq_len_argument(self):
        for flag in ("-l", "--min-dna-seq-length"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "32"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.min_dna_seq_length, 32)

    def test_min_reps_per_molecule_argument(self):
        for flag in ("-r", "--min-subreads-per-molecule"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "21"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.min_subreads_per_molecule, 21)

    def test_quality_threshold_argument(self):
        for flag in ("-q", "--quality-threshold"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "255"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.quality_threshold, 255)

    def test_quality_threshold_is_bounded(self):
        for val in ("-1", "256"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + ["-q", val]
            with patch.object(sys, "argv", clos):
                with self.assertRaises(SystemExit):
                    self.parse_cl()

    def test_mappings_argument(self):
        for flag in ("-m", "--mappings"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "25", "45"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.mappings, ["25", "45"])

    def test_mappings_argument_has_default(self):
        clos = [
            self.program_name] + self.dummy_mandatory_args
        with patch.object(sys, "argv", clos):
            args = self.parse_cl()
        self.assertEqual(args.mappings, "all")

    def test_min_relative_mapping_ratio_argument(self):
        for flag in ("-R", "--min-relative-mapping-ratio"):
            clos = [
                self.program_name] + self.dummy_mandatory_args + [
                    flag, "0.2"]
            with patch.object(sys, "argv", clos):
                args = self.parse_cl()
            self.assertEqual(args.min_relative_mapping_ratio, 0.2)
