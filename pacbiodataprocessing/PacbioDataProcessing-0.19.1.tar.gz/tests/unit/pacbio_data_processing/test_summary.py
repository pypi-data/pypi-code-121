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
from unittest.mock import patch, mock_open, MagicMock, call
from datetime import datetime
import sys
import socket
from pathlib import Path
from dataclasses import dataclass
from collections import namedtuple, defaultdict
import random

from pacbio_data_processing.summary import (
    SummaryReport, DEFAULT_STYLE, BarsPlotAttribute, HistoryPlotAttribute,
    PositionCoverageHistory, MoleculeLenHistogram, PercAttribute,
    InputReferenceAttribute,
)
from pacbio_data_processing.templates import SUMMARY_REPORT_HTML_TEMPLATE
from pacbio_data_processing import __version__ as VERSION
from pacbio_data_processing.constants import (
    SM_ANALYSIS_EXE, STRAIGHT_VARIANT, PI_SHIFTED_VARIANT,
)
from pacbio_data_processing.utils import DNASeq
from pacbio_data_processing.sm_analysis import METHYLATION_REPORT_HEADER


@dataclass
class FakeMolecule:
    molecule_id: bytes

    def __getitem__(self, item):
        return ""


FakeSubread = namedtuple(
    "FakeSubread",
    ("desc", "where", "name", "pos", "qual", "cigar", "a", "b", "c",
        "seq", "molecule_id")
)


REFERENCE = (
    "AAACCCTGCACGGCACGTAGTCTCGGAACTAATTCTAGCATTGACTCGTACCCACGAGTCGCCCCC"
    "ATCGACTTCTGCTTgatcTCGCCCTTCGCCCTCGATCTCGAACTCGTGGCCCTCCATGTGCAC"
    "TTTTTAATTGATCTCGCCCTTCGCCCTCGATCTCGAACTCGTGGATCTGTGCACGGATC"
)

METH_REPORT_TEST_ROWS = [
    METHYLATION_REPORT_HEADER,
    ['100', 'ACGGCACGTAGTCTCGGAACTAATTCTAGCATTGACTCGTACCCACGAGTCGCCCCC',
    '10', '66', '57', '28', '28', '64.8','93.0', '1', '0', '', '',
    '', '', '', '', '', '', '', ''],
    ['600', 'CTGCTTGATCTCGCCCTTCGCCCTCGATCTCGAACTCGTGGCCCTCCATGTGCAC',
    '75', '129', '55', '30', '30', '64.3', '93.0', '1', '2', '81,100',
    '2', 'f,f', '49.4', '60.0', '3.61', '7.41', '6.0', '43.0', '28'],
    ['610', 'GCTTGATCTCGCCCTTCGCCCTCGATCTCGAACTCGTGGCCCTCCATGTGCAC',
    '77', '129', '53', '20', '21', '34.3', '83.0', '1', '2', '81,100',
    '2', 'f,+', '49.3', '61.1', '4.31', '6.77', '5.4', '41.0', '26'],
    ['700', 'AATTGATCTCGCCCTTCGCCCTCGATCTCGAACTCGTGGATCTGTGCAC',
    '135', '183', '49', '22', '22', '43.3', '92.0', '1', '3', '139,158,173',
    '2', '0,+,-', '35.3', '51.5', '5.35', '5.75', '6.6', '46.3', '37'],
]

ALIGNED_CCS_BAM_LINES = (
    FakeSubread(
        b"", b"", b"", b"1", b"",
        b"129=", b"", b"", b"",
        (b"AAACCCTGCACGGCACGTAGTCTCGGAACTAATTCTAGCATTGACTCGTACCCACGAGTCGCCCCC"
        b"ATCGACTTCTGCTTGATCTCGCCCTTCGCCCTCGATCTCGAACTCGTGGCCCTCCATGTGCAC"),
        b"514"),
    FakeSubread(
        b"", b"", b"", b"1", b"",
        b"128=1X", b"", b"", b"",
        (b"AAACCCTGCACGGCACGTAGTCTCGGAACTAATTCTAGCATTGACTCGTACCCACGAGTCGCCCCC"
        b"ATCGACTTCTGCTTGATCTCGCCCTTCGCCCTCGATCTCGAACTCGTGGCCCTCCATGTGCAA"),
        b"514"),
    FakeSubread(
        b"", b"", b"", b"130", b"",
        b"2=3X53=", b"", b"", b"",
        b"TTGGGAATTGATCTCGCCCTTCGCCCTCGATCTCGAACTCGTGGATCTGTGCACGGAT",
        b"1514"),
)

PI_SHIFTED_ALIGNED_CCS_BAM_LINES = (
    FakeSubread(
        b"", b"", b"", b"95", b"",
        b"128=1X", b"", b"", b"",
        (b"AAACCCTGCACGGCACGTAGTCTCGGAACTAATTCTAGCATTGACTCGTACCCACGAGTCGCCCCC"
        b"ATCGACTTCTGCTTGATCTCGCCCTTCGCCCTCGATCTCGAACTCGTGGCCCTCCATGTGCAA"),
        b"514"),
    FakeSubread(
        b"", b"", b"", b"36", b"",
        b"58=", b"", b"", b"",
        b"TTTTTAATTGATCTCGCCCTTCGCCCTCGATCTCGAACTCGTGGATCTGTGCACGGAT",
        b"1514"),
    FakeSubread(
        b"", b"", b"", b"144", b"",
        b"30=2X20=", b"", b"", b"",
        b"ACCCACGAGTCGCCCCCATCGACTTCTGCTCCATCTCGCCCTTCGCCCTCGA",
        b"11111"),
)

PI_SHIFTED_ALIGNED_CCS_BAM_LINES_ISSUE_62 = (
    FakeSubread(
        b"", b"", b"", b"90", b"",
        b"95=", b"", b"", b"",
        (b"GGATCAAACCCTGCACGGCACGTAGTCTCGGAACTAATTCTAGCATTGACTCGTACCCACGAGTC"
         b"GCCCCCATCGACTTCTGCTTgatcTCGCCC"),
        b"23455"), # This FakeSubread ensures that issue #62 is fixed
)


@patch("pacbio_data_processing.summary.pandas")
@patch("pacbio_data_processing.summary.make_barsplot")
@patch("pacbio_data_processing.summary.make_multi_histogram")
@patch("pacbio_data_processing.summary.make_rolling_history")
@patch("pacbio_data_processing.summary.BamFile")
class SummaryReportTestCase(unittest.TestCase):
    def setUp(self):
        self.reference = DNASeq(
            REFERENCE, name="U096.3",
            description="U096.3 complete genome",
        )
        self.expected_data = {
            "style": DEFAULT_STYLE,
            "version": VERSION,
            "when": datetime.now().isoformat(timespec="minutes"),
            "program": SM_ANALYSIS_EXE,
            "clos": " ".join(sys.argv[1:]),
            "hostname": socket.gethostname(),
            "methylation_report": "a/b.c",
            "raw_detections": "q",
            "gff_result": "h.gff",
            "input_bam": "my.bam",
            "input_bam_size": 526039,
            "full_md5sum": "1634e047cda4cd3d547dde4e0a974181",
            "body_md5sum": "93a7f9bcb673053ab874e80d47fae941",
            "input_reference": "myc.fasta",
            "reference_name": "U096.3 complete genome",
            "reference_base_pairs": 188,
            "reference_md5sum": "24d9a40bc45db50ef74fabdd34e04b8b",
            "mols_ini": 123,
            "subreads_ini": 1235,
            "mols_dna_mismatches": 3,
            "perc_mols_dna_mismatches": "2.44",
            "subreads_dna_mismatches": 229,
            "perc_subreads_dna_mismatches": "18.54",
            "filtered_out_mols": 2,
            "perc_filtered_out_mols": "1.63",
            "filtered_out_subreads": 62,
            "perc_filtered_out_subreads": "5.02",
            "mols_in_meth_report": 4,
            "perc_mols_in_meth_report": "3.25",
            "subreads_in_meth_report": 201,
            "perc_subreads_in_meth_report": "16.28",
            "mols_in_meth_report_with_gatcs": 3,
            "perc_mols_in_meth_report_with_gatcs": "2.44",
            "subreads_in_meth_report_with_gatcs": 145,
            "perc_subreads_in_meth_report_with_gatcs": "11.74",
            "mols_in_meth_report_without_gatcs": 1,
            "perc_mols_in_meth_report_without_gatcs": "0.81",
            "subreads_in_meth_report_without_gatcs": 56,
            "perc_subreads_in_meth_report_without_gatcs": "4.53",
            "molecule_type_bars": "figures/molecule_type_bars.png",
            "molecule_len_histogram": "figures/molecule_length_histogram.png",
            "mols_used_in_aligned_ccs": 118,
            "perc_mols_used_in_aligned_ccs": "95.93",
            "subreads_used_in_aligned_ccs": 944,
            "perc_subreads_used_in_aligned_ccs": "76.44",
            "all_positions_in_bam": 187,
            "perc_all_positions_in_bam": "99.47",
            "all_positions_not_in_bam": 1,
            "perc_all_positions_not_in_bam": "0.53",
            "all_positions_in_meth": 161,
            "perc_all_positions_in_meth": "85.64",
            "all_positions_not_in_meth": 27,
            "perc_all_positions_not_in_meth": "14.36",
            "position_coverage_bars": "figures/position_coverage_bars.png",
            "position_coverage_history": (
                "figures/position_coverage_history.png"),
            "total_gatcs_in_ref": 6,
            "all_gatcs_identified_in_bam": 5,
            "perc_all_gatcs_identified_in_bam": "83.33",
            "all_gatcs_not_identified_in_bam": 1,
            "perc_all_gatcs_not_identified_in_bam": "16.67",
            "all_gatcs_in_meth": 5,
            "perc_all_gatcs_in_meth": "83.33",
            "all_gatcs_not_in_meth": 1,
            "perc_all_gatcs_not_in_meth": "16.67",
            "gatc_coverage_bars": "figures/gatc_coverage_bars.png",
            "max_possible_methylations": 7,
            "fully_methylated_gatcs": 3,
            "fully_methylated_gatcs_wrt_meth": "42.86",
            "fully_unmethylated_gatcs": 1,
            "fully_unmethylated_gatcs_wrt_meth": "14.29",
            "hemi_methylated_gatcs": 3,
            "hemi_methylated_gatcs_wrt_meth": "42.86",
            "hemi_plus_methylated_gatcs": 2,
            "hemi_plus_methylated_gatcs_wrt_meth": "28.57",
            "hemi_minus_methylated_gatcs": 1,
            "hemi_minus_methylated_gatcs_wrt_meth": "14.29",
            "meth_type_bars": "figures/meth_type_bars.png",
        }
        self.all_aligned_ccs_bam_files = {
            STRAIGHT_VARIANT: "blsr_ccs.bam",
            PI_SHIFTED_VARIANT: "pi-shifted_blsr_ccs.bam"
        }
        self.only_straight_expected_data = self.expected_data.copy()
        self.only_straight_expected_data.update(
            {
                "all_positions_in_bam": 129,
                "perc_all_positions_in_bam": "68.62",
                "all_positions_not_in_bam": 59,
                "perc_all_positions_not_in_bam": "31.38",
                "all_gatcs_identified_in_bam": 2,
                "perc_all_gatcs_identified_in_bam": "33.33",
                "all_gatcs_not_identified_in_bam": 4,
                "perc_all_gatcs_not_identified_in_bam": "66.67",
            }
        )
        self.only_straight_aligned_ccs_bam_files = {
            STRAIGHT_VARIANT: "blsr_ccs.bam",
            PI_SHIFTED_VARIANT: None
        }
        self.expected_data_issue_62 = self.expected_data.copy()
        self.expected_data_issue_62.update(
            {
                "all_gatcs_identified_in_bam": 6,
                "perc_all_gatcs_identified_in_bam": "100.00",
                "all_gatcs_not_identified_in_bam": 0,
                "perc_all_gatcs_not_identified_in_bam": "0.00",
                "all_positions_in_bam": 188,
                "perc_all_positions_in_bam": "100.00",
                "all_positions_not_in_bam": 0,
                "perc_all_positions_not_in_bam": "0.00",
            }
        )

    def create_summary_report(
            self, pBamFile,
            pi_shifted_lines_extra=()
            ):
        fake_bam = MagicMock()
        ccs_bam = MagicMock()
        ccs_bam.__iter__.side_effect = lambda: iter(ALIGNED_CCS_BAM_LINES)
        pi_shifted_ccs_bam = MagicMock()
        pi_shifted_ccs_bam.__iter__.side_effect = (
            lambda: iter(
                PI_SHIFTED_ALIGNED_CCS_BAM_LINES+pi_shifted_lines_extra
            )
        )
        def make_bam(name):
            if name == "my.bam":
                bam = fake_bam
            elif name == "blsr_ccs.bam":
                bam = ccs_bam
            elif name == "pi-shifted_blsr_ccs.bam":
                bam = pi_shifted_ccs_bam
            elif name is None:
                bam = None
            else:
                bam = MagicMock()
            return bam
        pBamFile.side_effect = make_bam
        fake_bam.size_in_bytes = 526039
        fake_bam.full_md5sum = "1634e047cda4cd3d547dde4e0a974181"
        fake_bam.md5sum_body = "93a7f9bcb673053ab874e80d47fae941"
        fake_bam.num_molecules = 123
        fake_bam.num_subreads = 1235
        fake_molecules = (
            [FakeMolecule(molecule_id=b"2")]*104+
            [FakeMolecule(molecule_id=b"22")]*63+
            [FakeMolecule(molecule_id=b"202")]*62+
            [FakeMolecule(molecule_id=b"324")]*32+
            [FakeMolecule(molecule_id=b"567")]*30+
            [FakeMolecule(
                molecule_id=str(i).encode()
                ) for i in range(1000,1118) for j in range(8)]
        )
        fake_bam.__iter__.side_effect = lambda: iter(fake_molecules)
        self.reference.fasta_name = "myc.fasta"
        return SummaryReport("my.bam", self.reference)

    def test_figures_dir_created(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        with patch("pacbio_data_processing.summary.Path") as pPath:
            s = SummaryReport("my.bam", self.reference)
        pPath.assert_called_once_with("figures")
        pPath.return_value.mkdir.assert_called_once_with(exist_ok=True)

    def test_save_writes_rendered_template(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        s = self.create_summary_report(pBamFile)
        s._data["mols_ini"] = 123
        s._data["subreads_ini"] = 1235
        mopen = mock_open()
        with patch("pacbio_data_processing.summary.open", mopen):
            with patch("pacbio_data_processing.summary.csv.reader") as preader:
                preader.return_value = iter(METH_REPORT_TEST_ROWS)
                s.methylation_report = Path("w")
        s.raw_detections = Path("q")
        s.gff_result = Path("h.gff")
        placeholders_needed = (
            "perc_mols_dna_mismatches",
            "perc_subreads_dna_mismatches",
            "perc_filtered_out_mols",
            "perc_filtered_out_subreads",
            "perc_all_gatcs_identified_in_bam",
            "perc_all_gatcs_not_identified_in_bam",
            "perc_mols_used_in_aligned_ccs",
            "perc_subreads_used_in_aligned_ccs",
            "perc_all_positions_in_bam",
            "perc_all_positions_not_in_bam",
        )
        attrs_needed = {
            "mols_used_in_aligned_ccs": 23,
            "subreads_used_in_aligned_ccs": 241,
            "mols_dna_mismatches": 4,
            "subreads_dna_mismatches": 45,
            "filtered_out_mols": 3,
            "filtered_out_subreads": 31,
            "all_positions_in_bam": 456,
            "all_positions_not_in_bam": 24,
            "all_gatcs_identified_in_bam": 31,
            "all_gatcs_not_identified_in_bam": 22,
        }
        for attr in attrs_needed:
            s._data[attr] = None
        for attr, value in attrs_needed.items():
            s._data[attr] = value
        mopen = mock_open()
        s.aligned_ccs_bam_files = {
            STRAIGHT_VARIANT: "blsr_ccs.bam",
            PI_SHIFTED_VARIANT: "pi-shifted_blsr_ccs.bam"
        }
        with (
                patch("pacbio_data_processing.summary.open", mopen),
                patch(
                    "pacbio_data_processing.summary.SummaryReport"
                    ".ready_to_go") as pready_to_go):
            pready_to_go.return_value = True
            s.save("my_file_name.html")
        mopen.assert_called_once_with("my_file_name.html", "w")
        handle = mopen()
        handle.write.assert_called_once_with(s.as_html)

    def test_as_html(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        self.maxDiff = None
        s = self.create_summary_report(pBamFile)
        pBamFile.assert_called_once_with("my.bam")
        mopen = mock_open()
        with patch("pacbio_data_processing.summary.open", mopen):
            with patch("pacbio_data_processing.summary.csv.reader") as preader:
                preader.return_value = iter(METH_REPORT_TEST_ROWS)
                s.methylation_report = Path("a/b.c")
        s.raw_detections = Path("q")
        s.gff_result = Path("h.gff")
        s.mols_dna_mismatches = {2, 22, 202}
        s.filtered_out_mols = {324, 567}
        s.mols_used_in_aligned_ccs = set(range(1000, 1118))
        s.aligned_ccs_bam_files = self.all_aligned_ccs_bam_files
        self.assertEqual(
            s.as_html,
            SUMMARY_REPORT_HTML_TEMPLATE.format(**self.expected_data)
        )
        s.aligned_ccs_bam_files = self.only_straight_aligned_ccs_bam_files
        self.assertEqual(
            s.as_html,
            SUMMARY_REPORT_HTML_TEMPLATE.format(
                **self.only_straight_expected_data)
        )

    def test_as_html_issue_62(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        self.maxDiff = None
        s = self.create_summary_report(
            pBamFile,
            pi_shifted_lines_extra=PI_SHIFTED_ALIGNED_CCS_BAM_LINES_ISSUE_62
        )
        pBamFile.assert_called_once_with("my.bam")
        mopen = mock_open()
        with patch("pacbio_data_processing.summary.open", mopen):
            with patch("pacbio_data_processing.summary.csv.reader") as preader:
                preader.return_value = iter(METH_REPORT_TEST_ROWS)
                s.methylation_report = Path("a/b.c")
        s.raw_detections = Path("q")
        s.gff_result = Path("h.gff")
        s.mols_dna_mismatches = {2, 22, 202}
        s.filtered_out_mols = {324, 567}
        s.mols_used_in_aligned_ccs = set(range(1000, 1118))
        s.aligned_ccs_bam_files = self.all_aligned_ccs_bam_files
        self.assertEqual(
            s.as_html,
            SUMMARY_REPORT_HTML_TEMPLATE.format(**self.expected_data_issue_62)
        )

    def test_read_only_attributes(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        fake_bam = pBamFile.return_value
        fake_bam.size_in_bytes = 526
        fake_bam.num_subreads = 1235
        fake_bam.full_md5sum = "1634e047cda4cd3d547dde4e0a974181"
        fake_bam.md5sum_body = "93a7f9bcb673053ab874e80d47fae941"
        fake_bam.num_molecules = 123
        fake_bam.num_subreads = 1235
        s = SummaryReport("my.bam", self.reference)
        self.assertEqual(s.input_bam_size, 526)
        self.assertEqual(s.full_md5sum, "1634e047cda4cd3d547dde4e0a974181")
        self.assertEqual(s.body_md5sum, "93a7f9bcb673053ab874e80d47fae941")
        self.assertEqual(s.reference_name, "U096.3 complete genome")
        self.assertEqual(s.reference_base_pairs, 188)
        self.assertEqual(
            s.reference_md5sum, "24d9a40bc45db50ef74fabdd34e04b8b")
        self.assertEqual(s.mols_ini, 123)
        self.assertEqual(s.subreads_ini, 1235)
        trials = {
            "input_bam_size": 4,
            "full_md5sum": "ddd",
            "body_md5sum": "222",
            "reference_name": "hu",
            "reference_base_pairs": 5,
            "reference_md5sum": "636362",
            "mols_ini": 2,
            "subreads_ini": 39,
            "perc_mols_dna_mismatches": "3.42",
            "subreads_dna_mismatches": 2209,
            "perc_subreads_dna_mismatches": "6.22",
            "perc_filtered_out_mols": "23.63",
            "filtered_out_subreads": 246,
            "perc_filtered_out_subreads": "23.72",
            "mols_in_meth_report": 3,
            "perc_mols_in_meth_report": "23.25",
            "subreads_in_meth_report": 21,
            "perc_subreads_in_meth_report": "6.28",
            "mols_in_meth_report_with_gatcs": 5,
            "perc_mols_in_meth_report_with_gatcs": "7.84",
            "subreads_in_meth_report_with_gatcs": 15,
            "perc_subreads_in_meth_report_with_gatcs": "81.74",
            "mols_in_meth_report_without_gatcs": 61,
            "perc_mols_in_meth_report_without_gatcs": "60.81",
            "subreads_in_meth_report_without_gatcs": 59,
            "perc_subreads_in_meth_report_without_gatcs": "74.53",
            "perc_mols_used_in_aligned_ccs": "5.21",
            "subreads_used_in_aligned_ccs": 68,
            "perc_subreads_used_in_aligned_ccs": "5.22",
            "all_positions_in_bam": 17,
            "perc_all_positions_in_bam": "29.47",
            "all_positions_not_in_bam": 12,
            "perc_all_positions_not_in_bam": "2.53",
            "all_positions_in_meth": 162,
            "perc_all_positions_in_meth": "85.34",
            "all_positions_not_in_meth": 25,
            "perc_all_positions_not_in_meth": "16.36",
            "molecule_type_bars": "figures/molecule_type_bars2.png",
            "molecule_len_histogram": "figures/molecule_l_histogram.png",
            "position_coverage_bars": "figures/position_coverage_bars.jpeg",
            "position_coverage_history": "figures/beautiful_flower.png",
            "total_gatcs_in_ref": 8,
            "all_gatcs_identified_in_bam": 4,
            "perc_all_gatcs_identified_in_bam": "83.34",
            "all_gatcs_not_identified_in_bam": 14,
            "perc_all_gatcs_not_identified_in_bam": "46.67",
            "all_gatcs_in_meth": 8,
            "perc_all_gatcs_in_meth": "83.43",
            "all_gatcs_not_in_meth": 15,
            "perc_all_gatcs_not_in_meth": "15.67",
            "gatc_coverage_bars": "figures/gatc_coverage_hist.png",
            "max_possible_methylations": 73,
            "fully_methylated_gatcs": 33,
            "fully_methylated_gatcs_wrt_meth": "43.86",
            "fully_unmethylated_gatcs": 13,
            "fully_unmethylated_gatcs_wrt_meth": "34.29",
            "hemi_methylated_gatcs": 6,
            "hemi_methylated_gatcs_wrt_meth": "62.86",
            "hemi_plus_methylated_gatcs": 26,
            "hemi_plus_methylated_gatcs_wrt_meth": "26.57",
            "hemi_minus_methylated_gatcs": 16,
            "hemi_minus_methylated_gatcs_wrt_meth": "14.49",
            "meth_type_bars": None,
        }
        for attr, value in trials.items():
            with self.assertRaises(AttributeError) as cm:
                setattr(s, attr, value)
            self.assertEqual(
                str(cm.exception),
                f"attribute '{attr}' cannot be set directly"
            )

    def test_plots_generated(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        s = self.create_summary_report(pBamFile)
        pBamFile.assert_called_once_with("my.bam")
        mopen = mock_open()
        with patch("pacbio_data_processing.summary.open", mopen):
            with patch("pacbio_data_processing.summary.csv.reader") as preader:
                preader.return_value = iter(METH_REPORT_TEST_ROWS)
                s.methylation_report = Path("a/b.c")
        s.raw_detections = Path("q")
        s.gff_result = Path("h.gff")
        s.mols_dna_mismatches = {2, 22, 202}
        s.filtered_out_mols = {324, 567}
        s.mols_used_in_aligned_ccs = set(range(1000, 1118))
        s.aligned_ccs_bam_files = {
            STRAIGHT_VARIANT: "blsr_ccs.bam",
            PI_SHIFTED_VARIANT: "pi-shifted_blsr_ccs.bam"
        }
        with patch("pacbio_data_processing.summary.open", mopen):
            s.save("whatever.html")
        pbars.assert_has_calls(
            [
                call(
                    pd.DataFrame.return_value,
                    "Processed molecules and subreads",
                    "figures/molecule_type_bars.png"
                ),
                call(
                    pd.DataFrame.return_value,
                    "Position coverage in BAM file and Methylation report",
                    "figures/position_coverage_bars.png"
                ),
                call(
                    pd.DataFrame.return_value,
                    "GATCs in BAM file and Methylation report",
                    "figures/gatc_coverage_bars.png"
                ),
                call(
                    pd.DataFrame.return_value,
                    "Methylation types in methylation report",
                    "figures/meth_type_bars.png"
                ),
            ]
        )
        pmultihist.assert_called_once_with(
            {
                "Initial subreads": pd.Series.return_value,
                "Analyzed molecules": (
                    pd.read_csv.return_value.__getitem__.return_value)
            },
            "Initial subreads and analyzed molecule length histogram",
            "figures/molecule_length_histogram.png", True,
        )
        prolling.assert_called_once_with(
            {i: 0 for i in range(
                1, self.expected_data["reference_base_pairs"]+1)},
            "Sequencing positions covered by analyzed molecules",
            "figures/position_coverage_history.png", False,
        )

    def test_switch_on_method(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        s = self.create_summary_report(pBamFile)
        self.assertFalse(s._primary_attributes["Iloveyou"])
        s.switch_on("Iloveyou")
        self.assertTrue(s._primary_attributes["Iloveyou"])

    def test_ready_to_go(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        s = self.create_summary_report(pBamFile)
        self.assertFalse(s.ready_to_go("data1", "data5"))
        s.switch_on("data1")
        self.assertFalse(s.ready_to_go("data1", "data5"))
        self.assertTrue(s.ready_to_go("data1"))
        s.switch_on("wah")
        self.assertFalse(s.ready_to_go("data1", "data5"))
        self.assertTrue(s.ready_to_go("data1"))
        self.assertTrue(s.ready_to_go("wah"))
        s.switch_on("data5")
        self.assertTrue(s.ready_to_go("data1", "data5"))
        self.assertTrue(s.ready_to_go("data1", "data5", "wah"))
        self.assertTrue(s.ready_to_go("data1"))
        self.assertTrue(s.ready_to_go("data5"))
        self.assertTrue(s.ready_to_go("data1"))

    def test_getitem(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        s = self.create_summary_report(pBamFile)
        with self.assertRaises(KeyError):
            s["incredible"]
        s.incredible = 8
        self.assertEqual(s["incredible"], 8)
        s._data ["incredible"] = 2348
        self.assertEqual(s["incredible"], 2348)

    def test_keys(
            self, pBamFile, prolling, pmultihist, pbars, pd):
        s = self.create_summary_report(pBamFile)
        pBamFile.return_value.side_effect = TypeError
        s.bam = pBamFile.return_value
        s.gff_result = "ssh"
        s.raw_detections = "xk"
        s._data["methylation_report"] = "moqui"
        numeric_keys = [
            "all_gatcs_in_meth", "filtered_out_mols",
            "mols_used_in_aligned_ccs", "subreads_in_meth_report_with_gatcs",
            "hemi_plus_methylated_gatcs", "all_positions_in_meth",
            "subreads_dna_mismatches", "mols_in_meth_report",
            "mols_dna_mismatches", "fully_unmethylated_gatcs",
            "hemi_methylated_gatcs", "mols_in_meth_report_with_gatcs",
            "subreads_in_meth_report", "filtered_out_subreads",
            "hemi_minus_methylated_gatcs", "max_possible_methylations",
            "subreads_in_meth_report_without_gatcs",
            "subreads_used_in_aligned_ccs", "all_positions_not_in_meth",
            "all_gatcs_identified_in_bam", "all_gatcs_not_in_meth",
            "fully_methylated_gatcs", "all_gatcs_not_identified_in_bam",
            "mols_in_meth_report_without_gatcs", "all_positions_in_bam",
            "all_positions_not_in_bam", "aligned_ccs_bam_files"
        ]
        for key in numeric_keys:
            s._data[key] = random.randint(0,1000)
        for key in s.keys():
            with self.assertRaises(TypeError):
                s[key]()

    def test_len(self, pBamFile, prolling, pmultihist, pbars, pd):
        s = self.create_summary_report(pBamFile)
        with patch("pacbio_data_processing.summary.SummaryReport.keys"
                       ) as pkeys:
            pkeys.return_value = set(range(489))
            self.assertEqual(len(s), 489)

    def test_iter(self, pBamFile, prolling, pmultihist, pbars, pd):
        s = self.create_summary_report(pBamFile)
        s._data["α"] = "a"
        s._data["β"] = "B"
        with patch("pacbio_data_processing.summary.SummaryReport.keys"
                       ) as pkeys:
            pkeys.return_value = {"α", "β"}
            items = list(s)
            items.sort()
            self.assertEqual(items, ["B", "a"])


class MyBarsPlot(BarsPlotAttribute):
    title = "I see your wonders"
    dependency_names = (
        "what_a",
        "how_k"
    )
    data_definition = {
        'Bases covered': ("perc",),
        'Bases NOT covered': ("perc_not",),
    }
    index_labels = ("Points",)


class FakeHost4BarPlots:
    myplot = MyBarsPlot()
    perc = "2.03"
    perc_not = "3.76"

    def ready_to_go(self, *dependencies):
        return self._ready_to_go


@patch("pacbio_data_processing.summary.pandas")
class BarsPlotAttributeTestCase(unittest.TestCase):
    def test_get_if_not_ready(self, pd):
        host = FakeHost4BarPlots()
        host._ready_to_go = False
        self.assertIs(host.myplot, None)

    def test_get_if_ready(self, pd):
        host = FakeHost4BarPlots()
        host._ready_to_go = True
        host._data = {
            "myplot": "wonderf.png"
        }
        self.assertEqual(
            host.myplot,
            (pd.DataFrame.return_value, "I see your wonders", "wonderf.png")
        )
        pd.DataFrame.assert_called_once_with(
            {"Bases covered": [2.03], "Bases NOT covered": [3.76]},
            index=("Points",)
        )

    def test_issue83(self, pd):
        """It does not raise ValueError if a value is not float"""
        host = FakeHost4BarPlots()
        host.perc = "N/A"
        host._ready_to_go = True
        host._data = {
            "myplot": "wonderf.png"
        }
        host.myplot



class MyHistogramPlot(HistoryPlotAttribute):
    title = "A Beautiful Title"
    dependency_name = "wreck"
    column_name = "len(molecule)"
    data_name = "height"
    labels = ("Width",)
    legend = True
    #column = "obs"
    #hue = "src"


fake_make_data_for_plot = MagicMock()


class MyHistogramPlotDataFaked(MyHistogramPlot):
    make_data_for_plot = fake_make_data_for_plot


class MyPositionCoverageHistory(MyHistogramPlot, PositionCoverageHistory):
    ...


class MyMoleculeLenHistogram(MyHistogramPlot, MoleculeLenHistogram):
    labels = ("one label", "another label")


class FakeHost4Histograms:
    myhist = MyHistogramPlotDataFaked()
    myposhist = MyPositionCoverageHistory()
    mylenhist = MyMoleculeLenHistogram()
    bam = [["x"]*9+["x"*_] for _ in range(2, 10,2)]
    reference_base_pairs = 23

    def ready_to_go(self, *dependencies):
        return self._ready_to_go


@patch("pacbio_data_processing.summary.pandas")
class HistogramPlotTestCase(unittest.TestCase):
    def test_get_if_not_ready(self, pd):
        host = FakeHost4Histograms()
        host._ready_to_go = False
        self.assertIs(host.myhist, None)

    def test_get_if_ready(self, pd):
        host = FakeHost4Histograms()
        host._ready_to_go = True
        host._data = {
            "myhist": "aggderf.png"
        }
        self.assertEqual(
            host.myhist,
            (fake_make_data_for_plot.return_value, "A Beautiful Title",
                 "aggderf.png", True)
        )


@patch("pacbio_data_processing.summary.pandas")
class PositionCoverageHistoryTestCase(unittest.TestCase):
    def test_make_data_for_plot(self, pd):
        host = FakeHost4Histograms()
        host._ready_to_go = True
        host._data = {
            "myposhist": "aggderf.png",
            "wreck": "mr.csv",
        }
        raw_data = {
            "start of molecule": [1, 3, 15, 11, 20],
            "len(molecule)": [5, 2, 2, 5, 5],
        }
        expected_dict = {i: 0 for i in range(1, 23)}
        expected_dict.update(
            {
                1: 2, 2: 1, 3: 2, 4: 2, 5: 1,
                11: 1, 12: 1, 13: 1, 14: 1, 15: 2,
                16: 1, 20: 1, 21: 1, 22: 1, 23: 1
            }
        )
        pd.read_csv.return_value = raw_data
        plot_data = host.myposhist
        pd.read_csv.assert_called_once_with("mr.csv", delimiter=";")
        self.assertEqual(plot_data[0], expected_dict)


@patch("pacbio_data_processing.summary.pandas")
class MoleculeLenHistogramTestCase(unittest.TestCase):
    def test_make_data_for_plot(self, pd):
        host = FakeHost4Histograms()
        host._ready_to_go = True
        host._data = {
            "mylenhist": "aggderf.png",
        }
        host.wreck = "mr.csv"
        subreads = MagicMock()
        mols = MagicMock()
        pd.Series.return_value = subreads
        pd.read_csv.return_value.__getitem__.return_value = mols
        host.mylenhist
        pd.read_csv.assert_called_once_with("mr.csv", delimiter=";")
        pd.Series.assert_called_once_with(list(range(2, 10, 2)), name="height")
        self.assertEqual(mols.name, "height")


class AttributesTestCase(unittest.TestCase):
    def setUp(self):
        class MyClass:
            _data = {
                "amount": 17.2,
                "total": 47,
            }
            perc_amount = PercAttribute(total_attr="total")
            reference = InputReferenceAttribute()
            _on = defaultdict(bool)

            def switch_on(self, attr):
                self._on[attr] = True

        self.instance = MyClass()

    def test_perc_attribute(self):
        self.assertEqual(self.instance.perc_amount, "36.60")

    def test_issue65(self):
        self.instance._data["total"] = 0
        self.assertEqual(self.instance.perc_amount, "N/A")

    def test_input_reference_attribute(self):
        class Reference:
            fasta_name = "mol.fasta"
            description = "No fun here\r\n"
            md5sum = "a3"
            _seq = "agtGaTcCGATC"

            def __len__(self):
                return len(self._seq)

            def upper(self):
                return self._seq.upper()

        self.instance.reference = Reference()
        self.assertEqual(self.instance.reference, "mol.fasta")
        self.assertEqual(self.instance._data["reference_name"], "No fun here")
        self.assertEqual(self.instance._data["reference_base_pairs"], 12)
        self.assertEqual(self.instance._data["reference_md5sum"], "a3")
        self.assertEqual(self.instance._data["total_gatcs_in_ref"], 2)
        self.assertTrue(self.instance._on["reference"])
