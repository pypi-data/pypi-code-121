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

from pathlib import Path
import shutil
from io import StringIO
from collections import Counter
import os
import stat

import pytest


collect_ignore = ["fake.tools"]

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR/"data"
FAKE_RESOURCES_DIR = BASE_DIR/"fake.resources"
FAKE_TOOLS_DIR = BASE_DIR/"fake.tools"
RELATIVE_BIN_NO_PATH_DIR = "bin.no.path"

TEST_BAM_FILE_MOL_COL24 = {
    "in": "body11.bam",
    "in-text": "body11.text",
}
TEST_BAM_FILE_MOL_COL19 = {
    "in": "body11_mol_col19.bam",
    "in-text": "body11_mol_col19.text",
}

MD5s = {
    "blasr.11mols.bam": {"body": "", "full": ""},
}

# It is probably useful to define a SmAnalysisFTData (as dataclass)...
#
# The TEST_DATA_FOR_SM_ANALYSIS dict has some keys worth being described:
#
#  - renames (dict): each key in that dict must be present in the "files"
#    dict. The expected structure is (symbolic notation follows):
#      files:    {key: file-name}
#      renames:  {key: new-file-name}
#    using equivalent shell commands, the procedure would be
#      $ cp file-mane /tmp/.../ # the temp dir for the tests
#      $ cd /tmp/.../
#      $ mv file-name new-file-name

TEST_DATA_FOR_SM_ANALYSIS = [
    {
        "name": "no clos",
        "features": {"no clos"},
        "files": {
            "bam": "blasr.11mols.bam",
            "fasta": "11mols.fasta",
            "fasta.fai": "11mols.fasta.fai",
            "gff": "expected.sm-analysis.blasr.11mols.gff",
            "csv": "expected.sm-analysis.blasr.11mols.csv",
            "methylation-report":
            "expected.V3.methylation.sm-analysis.blasr.11mols.csv",
        },
        "renames": {},
        "CLOs": (),
        "molecules": [
            '19399571', '23658875', '28836053', '29229724',
            '45744686', '52167204', '55116046', '59179888',
            '60359568', '72352689', '74515099',
        ],
        "num CCS molecules": 11,
        "mol ids with reference mismatch": (
            '19399571', '59179888', '72352689'),
        "mols rejected by filters": (),  # ('19399571',),
        "statistics": {
            "mols_ini": "11",
            "subreads_ini": "2030",
            "mols_used_in_aligned_ccs": "11",
            "perc_mols_used_in_aligned_ccs": "100.00",
            "subreads_used_in_aligned_ccs": "2030",
            "perc_subreads_used_in_aligned_ccs": "100.00",
            "mols_dna_mismatches": "3",
            "perc_mols_dna_mismatches": "27.27",
            "subreads_dna_mismatches": "298",
            "perc_subreads_dna_mismatches": "14.68",
            "filtered_out_mols": "0",
            "perc_filtered_out_mols": "0.00",
            "filtered_out_subreads": "0",
            "perc_filtered_out_subreads": "0.00",
            "mols_in_meth_report": "8",
            "perc_mols_in_meth_report": "72.73",
            "subreads_in_meth_report": "1732",
            "perc_subreads_in_meth_report": "85.32",
            "mols_in_meth_report_with_gatcs": "5",
            "perc_mols_in_meth_report_with_gatcs": "45.45",
            "subreads_in_meth_report_with_gatcs": "1183",
            "perc_subreads_in_meth_report_with_gatcs": "58.28",
            "mols_in_meth_report_without_gatcs": "3",
            "perc_mols_in_meth_report_without_gatcs": "27.27",
            "subreads_in_meth_report_without_gatcs": "549",
            "perc_subreads_in_meth_report_without_gatcs": "27.04",
            "all_positions_in_bam": "1891",
            "perc_all_positions_in_bam": "0.04",
            "all_positions_not_in_bam": "4639761",
            "perc_all_positions_not_in_bam": "99.96",
            "all_positions_in_meth": "1891",
            "perc_all_positions_in_meth": "0.04",
            "all_positions_not_in_meth": "4639761",
            "perc_all_positions_not_in_meth": "99.96",
            "total_gatcs_in_ref": "19124",
            "all_gatcs_identified_in_bam": "12",
            "perc_all_gatcs_identified_in_bam": "0.06",
            "all_gatcs_not_identified_in_bam": "19112",
            "perc_all_gatcs_not_identified_in_bam": "99.94",
            "all_gatcs_in_meth": "12",
            "perc_all_gatcs_in_meth": "0.06",
            "all_gatcs_not_in_meth": "19112",
            "perc_all_gatcs_not_in_meth": "99.94",
            "max_possible_methylations": "12",
            "fully_methylated_gatcs": "10",
            "fully_methylated_gatcs_wrt_meth": "83.33",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "0.00",
            "hemi_methylated_gatcs": "2",
            "hemi_methylated_gatcs_wrt_meth": "16.67",
            "hemi_plus_methylated_gatcs": "1",
            "hemi_plus_methylated_gatcs_wrt_meth": "8.33",
            "hemi_minus_methylated_gatcs": "1",
            "hemi_minus_methylated_gatcs_wrt_meth": "8.33",
        },
    },
    ##################################################################
    {
        "name": "unfiltered data",
        "features": {"unfiltered data", "no clos"},
        "files": {
            "bam": "blasr.12mols.bam",
            "fasta": "11mols.fasta",
            "fasta.fai": "11mols.fasta.fai",
            "gff": "expected.sm-analysis.blasr.12mols.gff",
            "csv": "expected.sm-analysis.blasr.12mols.csv",
            "methylation-report":
            "expected.V3.methylation.sm-analysis.blasr.12mols.csv",
        },
        "renames": {},
        "CLOs": (),
        "molecules": [
            '23658875', '28836053', '29229724', '45744686',
            '52167204', '55116046', '59179888', '60359568',
            '72352689', '74515099',
        ],
        "num CCS molecules": 13,
        "mol ids with reference mismatch": (
            '4391567', '19399571', '59179888',),
        "mols rejected by filters": ('9900000',),  # ('4391567', '19399571'),
        "statistics": {
            "reference_base_pairs": "4641652",
            "mols_ini": "13",
            "subreads_ini": "2304",
            "mols_used_in_aligned_ccs": "13",
            "perc_mols_used_in_aligned_ccs": "100.00",
            "subreads_used_in_aligned_ccs": "2304",
            "perc_subreads_used_in_aligned_ccs": "100.00",
            "mols_dna_mismatches": "3",
            "perc_mols_dna_mismatches": "23.08",
            "subreads_dna_mismatches": "246",
            "perc_subreads_dna_mismatches": "10.68",
            "filtered_out_mols": "1",
            "perc_filtered_out_mols": "7.69",
            "filtered_out_subreads": "182",
            "perc_filtered_out_subreads": "7.90",
            "mols_in_meth_report": "9",
            "perc_mols_in_meth_report": "69.23",
            "subreads_in_meth_report": "1876",
            "perc_subreads_in_meth_report": "81.42",
            "mols_in_meth_report_with_gatcs": "5",
            "perc_mols_in_meth_report_with_gatcs": "38.46",
            "subreads_in_meth_report_with_gatcs": "1183",
            "perc_subreads_in_meth_report_with_gatcs": "51.35",
            "mols_in_meth_report_without_gatcs": "4",
            "perc_mols_in_meth_report_without_gatcs": "30.77",
            "subreads_in_meth_report_without_gatcs": "693",
            "perc_subreads_in_meth_report_without_gatcs": "30.08",
            "all_positions_in_bam": "2080",
            "perc_all_positions_in_bam": "0.04",
            "all_positions_not_in_bam": "4639572",
            "perc_all_positions_not_in_bam": "99.96",
            "all_positions_in_meth": "2080",
            "perc_all_positions_in_meth": "0.04",
            "all_positions_not_in_meth": "4639572",
            "perc_all_positions_not_in_meth": "99.96",
            "total_gatcs_in_ref": "19124",
            "all_gatcs_identified_in_bam": "12",
            "perc_all_gatcs_identified_in_bam": "0.06",
            "all_gatcs_not_identified_in_bam": "19112",
            "perc_all_gatcs_not_identified_in_bam": "99.94",
            "all_gatcs_in_meth": "12",
            "perc_all_gatcs_in_meth": "0.06",
            "all_gatcs_not_in_meth": "19112",
            "perc_all_gatcs_not_in_meth": "99.94",
            "max_possible_methylations": "12",
            "fully_methylated_gatcs": "10",
            "fully_methylated_gatcs_wrt_meth": "83.33",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "0.00",
            "hemi_methylated_gatcs": "2",
            "hemi_methylated_gatcs_wrt_meth": "16.67",
            "hemi_plus_methylated_gatcs": "1",
            "hemi_plus_methylated_gatcs_wrt_meth": "8.33",
            "hemi_minus_methylated_gatcs": "1",
            "hemi_minus_methylated_gatcs_wrt_meth": "8.33",
        },
    },
    ##################################################################
    {
        "name": "model P6-C4",
        "features": {"model P6-C4"},
        "files": {
            "bam": "blasr.8mols.bam",
            "fasta": "pMA685.fa",
            "fasta.fai": "pMA685.fa.fai",
            "gff": "expected.sm-analysis.blasr.8mols.gff",
            "csv": "expected.sm-analysis.blasr.8mols.csv",
            "methylation-report":
            "expected.V3.methylation.sm-analysis.blasr.8mols.csv",
        },
        "renames": {},
        "CLOs": ("-M", "P6-C4"),
        "molecules": [
            '25294', '150700', '107947',
            '67334', '49610', '86474',
        ],
        "num CCS molecules": 6,
        "mol ids with reference mismatch": ('49610', '86474',),
        "mols rejected by filters": ('25294',),
        "statistics": {
            "reference_base_pairs": "95304",
            "mols_ini": "8",
            "subreads_ini": "478",
            "mols_used_in_aligned_ccs": "6",
            "perc_mols_used_in_aligned_ccs": "75.00",
            "subreads_used_in_aligned_ccs": "386",
            "perc_subreads_used_in_aligned_ccs": "80.75",
            "mols_dna_mismatches": "2",
            "perc_mols_dna_mismatches": "25.00",
            "subreads_dna_mismatches": "112",
            "perc_subreads_dna_mismatches": "23.43",
            "filtered_out_mols": "1",
            "perc_filtered_out_mols": "12.50",
            "filtered_out_subreads": "93",
            "perc_filtered_out_subreads": "19.46",
            "mols_in_meth_report": "3",
            "perc_mols_in_meth_report": "37.50",
            "subreads_in_meth_report": "141",
            "perc_subreads_in_meth_report": "29.50",
            "mols_in_meth_report_with_gatcs": "0",
            "perc_mols_in_meth_report_with_gatcs": "0.00",
            "subreads_in_meth_report_with_gatcs": "0",
            "perc_subreads_in_meth_report_with_gatcs": "0.00",
            "mols_in_meth_report_without_gatcs": "3",
            "perc_mols_in_meth_report_without_gatcs": "37.50",
            "subreads_in_meth_report_without_gatcs": "141",
            "perc_subreads_in_meth_report_without_gatcs": "29.50",
            "all_positions_in_bam": "2372",
            "perc_all_positions_in_bam": "2.49",
            "all_positions_not_in_bam": "92932",
            "perc_all_positions_not_in_bam": "97.51",
            "all_positions_in_meth": "1740",
            "perc_all_positions_in_meth": "1.83",
            "all_positions_not_in_meth": "93564",
            "perc_all_positions_not_in_meth": "98.17",
            "total_gatcs_in_ref": "62",
            "all_gatcs_identified_in_bam": "0",
            "perc_all_gatcs_identified_in_bam": "0.00",
            "all_gatcs_not_identified_in_bam": "62",
            "perc_all_gatcs_not_identified_in_bam": "100.00",
            "all_gatcs_in_meth": "0",
            "perc_all_gatcs_in_meth": "0.00",
            "all_gatcs_not_in_meth": "62",
            "perc_all_gatcs_not_in_meth": "100.00",
            "max_possible_methylations": "0",
            "fully_methylated_gatcs": "0",
            "fully_methylated_gatcs_wrt_meth": "N/A",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "N/A",
            "hemi_methylated_gatcs": "0",
            "hemi_methylated_gatcs_wrt_meth": "N/A",
            "hemi_plus_methylated_gatcs": "0",
            "hemi_plus_methylated_gatcs_wrt_meth": "N/A",
            "hemi_minus_methylated_gatcs": "0",
            "hemi_minus_methylated_gatcs_wrt_meth": "N/A",
        },
    },
    ##################################################################
    {
        "name": "model dummy",
        "features": {"model dummy"},
        "files": {
            "bam": "blasr.8mols.bam",
            "fasta": "pMA685.fa",
            "fasta.fai": "pMA685.fa.fai",
            "gff": "expected.sm-analysis.blasr.8mols.gff",
            "csv": "expected.sm-analysis.blasr.8mols.csv",
            "methylation-report":
            "expected.V3.methylation.sm-analysis.blasr.8mols.csv",
        },
        "renames": {},
        "CLOs": ("-M", "resources/dummy.npz.gz"),
        "molecules": [
            '25294', '150700', '107947',
            '67334', '49610', '86474',
        ],
        "num CCS molecules": 6,
        "mol ids with reference mismatch": ('49610', '86474'),
        "mols rejected by filters": ('25294',),
        "statistics": {
            "reference_base_pairs": "95304",
            "mols_ini": "8",
            "subreads_ini": "478",
            "mols_used_in_aligned_ccs": "6",
            "perc_mols_used_in_aligned_ccs": "75.00",
            "subreads_used_in_aligned_ccs": "386",
            "perc_subreads_used_in_aligned_ccs": "80.75",
            "mols_dna_mismatches": "2",
            "perc_mols_dna_mismatches": "25.00",
            "subreads_dna_mismatches": "112",
            "perc_subreads_dna_mismatches": "23.43",
            "filtered_out_mols": "1",
            "perc_filtered_out_mols": "12.50",
            "filtered_out_subreads": "93",
            "perc_filtered_out_subreads": "19.46",
            "mols_in_meth_report": "3",
            "perc_mols_in_meth_report": "37.50",
            "subreads_in_meth_report": "141",
            "perc_subreads_in_meth_report": "29.50",
            "mols_in_meth_report_with_gatcs": "0",
            "perc_mols_in_meth_report_with_gatcs": "0.00",
            "subreads_in_meth_report_with_gatcs": "0",
            "perc_subreads_in_meth_report_with_gatcs": "0.00",
            "mols_in_meth_report_without_gatcs": "3",
            "perc_mols_in_meth_report_without_gatcs": "37.50",
            "subreads_in_meth_report_without_gatcs": "141",
            "perc_subreads_in_meth_report_without_gatcs": "29.50",
            "all_positions_in_bam": "2372",
            "perc_all_positions_in_bam": "2.49",
            "all_positions_not_in_bam": "92932",
            "perc_all_positions_not_in_bam": "97.51",
            "all_positions_in_meth": "1740",
            "perc_all_positions_in_meth": "1.83",
            "all_positions_not_in_meth": "93564",
            "perc_all_positions_not_in_meth": "98.17",
            "total_gatcs_in_ref": "62",
            "all_gatcs_identified_in_bam": "0",
            "perc_all_gatcs_identified_in_bam": "0.00",
            "all_gatcs_not_identified_in_bam": "62",
            "perc_all_gatcs_not_identified_in_bam": "100.00",
            "all_gatcs_in_meth": "0",
            "perc_all_gatcs_in_meth": "0.00",
            "all_gatcs_not_in_meth": "62",
            "perc_all_gatcs_not_in_meth": "100.00",
            "max_possible_methylations": "0",
            "fully_methylated_gatcs": "0",
            "fully_methylated_gatcs_wrt_meth": "N/A",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "N/A",
            "hemi_methylated_gatcs": "0",
            "hemi_methylated_gatcs_wrt_meth": "N/A",
            "hemi_plus_methylated_gatcs": "0",
            "hemi_plus_methylated_gatcs_wrt_meth": "N/A",
            "hemi_minus_methylated_gatcs": "0",
            "hemi_minus_methylated_gatcs_wrt_meth": "N/A",
        },
    },
    ##################################################################
    {
        "name": "partition2of3",
        "features": {"partition"},
        "files": {
            "bam": "blasr.11mols.bam",
            "fasta": "11mols.fasta",
            "fasta.fai": "11mols.fasta.fai",
            "gff": "expected.partition_2of3.sm-analysis.blasr.11mols.gff",
            "csv": "expected.partition_2of3.sm-analysis.blasr.11mols.csv",
            "methylation-report": (
                "expected.V3.methylation.partition_2of3.sm-analysis.blasr."
                "11mols.csv"
            ),
        },
        "renames": {},
        "CLOs": ("--partition", "2:3"),
        "molecules": [
            '29229724', '45744686', '52167204',
        ],
        "num CCS molecules": 11,
        "mol ids with reference mismatch": (),
        "mols rejected by filters": (),
        "statistics": {
            "reference_base_pairs": "4641652",
            "mols_ini": "11",
            "subreads_ini": "2030",
            "mols_used_in_aligned_ccs": "11",
            "perc_mols_used_in_aligned_ccs": "100.00",
            "subreads_used_in_aligned_ccs": "2030",
            "perc_subreads_used_in_aligned_ccs": "100.00",
            "mols_dna_mismatches": "3",
            "perc_mols_dna_mismatches": "27.27",
            "subreads_dna_mismatches": "298",
            "perc_subreads_dna_mismatches": "14.68",
            "filtered_out_mols": "0",
            "perc_filtered_out_mols": "0.00",
            "filtered_out_subreads": "0",
            "perc_filtered_out_subreads": "0.00",
            "mols_in_meth_report": "3",
            "perc_mols_in_meth_report": "27.27",
            "subreads_in_meth_report": "560",
            "perc_subreads_in_meth_report": "27.59",
            "mols_in_meth_report_with_gatcs": "1",
            "perc_mols_in_meth_report_with_gatcs": "9.09",
            "subreads_in_meth_report_with_gatcs": "217",
            "perc_subreads_in_meth_report_with_gatcs": "10.69",
            "mols_in_meth_report_without_gatcs": "2",
            "perc_mols_in_meth_report_without_gatcs": "18.18",
            "subreads_in_meth_report_without_gatcs": "343",
            "perc_subreads_in_meth_report_without_gatcs": "16.90",
            "all_positions_in_bam": "1891",
            "perc_all_positions_in_bam": "0.04",
            "all_positions_not_in_bam": "4639761",
            "perc_all_positions_not_in_bam": "99.96",
            "all_positions_in_meth": "814",
            "perc_all_positions_in_meth": "0.02",
            "all_positions_not_in_meth": "4640838",
            "perc_all_positions_not_in_meth": "99.98",
            "total_gatcs_in_ref": "19124",
            "all_gatcs_identified_in_bam": "12",
            "perc_all_gatcs_identified_in_bam": "0.06",
            "all_gatcs_not_identified_in_bam": "19112",
            "perc_all_gatcs_not_identified_in_bam": "99.94",
            "all_gatcs_in_meth": "3",
            "perc_all_gatcs_in_meth": "0.02",
            "all_gatcs_not_in_meth": "19121",
            "perc_all_gatcs_not_in_meth": "99.98",
            "max_possible_methylations": "3",
            "fully_methylated_gatcs": "3",
            "fully_methylated_gatcs_wrt_meth": "100.00",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "0.00",
            "hemi_methylated_gatcs": "0",
            "hemi_methylated_gatcs_wrt_meth": "0.00",
            "hemi_plus_methylated_gatcs": "0",
            "hemi_plus_methylated_gatcs_wrt_meth": "0.00",
            "hemi_minus_methylated_gatcs": "0",
            "hemi_minus_methylated_gatcs_wrt_meth": "0.00",
        },
    },
    ##################################################################
    {
        "name": "two modification types",
        "features": {"two modification types"},
        "files": {
            "bam": "blasr.11mols.bam",
            "fasta": "11mols.fasta",
            "fasta.fai": "11mols.fasta.fai",
            "gff": "expected.sm-analysis.11mols_m6A-m4C.gff",
            "csv": "expected.sm-analysis.11mols_m6A-m4C.csv",
            "methylation-report":
            "expected.V3.methylation.sm-analysis.11mols_m6A-m4C.csv",
        },
        "renames": {},
        "CLOs": ("-m", "m6A", "m4C"),
        "molecules": [
            '23658875', '28836053', '29229724',
            '45744686', '52167204', '55116046', '59179888',
            '60359568', '74515099',
        ],
        "num CCS molecules": 11,
        "mol ids with reference mismatch": (
            '19399571', '59179888', '72352689'),
        "mols rejected by filters": (),
        "statistics": {
            "mols_ini": "11",
            "subreads_ini": "2030",
            "mols_used_in_aligned_ccs": "11",
            "perc_mols_used_in_aligned_ccs": "100.00",
            "subreads_used_in_aligned_ccs": "2030",
            "perc_subreads_used_in_aligned_ccs": "100.00",
            "mols_dna_mismatches": "3",
            "perc_mols_dna_mismatches": "27.27",
            "subreads_dna_mismatches": "298",
            "perc_subreads_dna_mismatches": "14.68",
            "filtered_out_mols": "0",
            "perc_filtered_out_mols": "0.00",
            "filtered_out_subreads": "0",
            "perc_filtered_out_subreads": "0.00",
            "mols_in_meth_report": "8",
            "perc_mols_in_meth_report": "72.73",
            "subreads_in_meth_report": "1732",
            "perc_subreads_in_meth_report": "85.32",
            "mols_in_meth_report_with_gatcs": "5",
            "perc_mols_in_meth_report_with_gatcs": "45.45",
            "subreads_in_meth_report_with_gatcs": "1183",
            "perc_subreads_in_meth_report_with_gatcs": "58.28",
            "mols_in_meth_report_without_gatcs": "3",
            "perc_mols_in_meth_report_without_gatcs": "27.27",
            "subreads_in_meth_report_without_gatcs": "549",
            "perc_subreads_in_meth_report_without_gatcs": "27.04",
            "all_positions_in_bam": "1891",
            "perc_all_positions_in_bam": "0.04",
            "all_positions_not_in_bam": "4639761",
            "perc_all_positions_not_in_bam": "99.96",
            "all_positions_in_meth": "1891",
            "perc_all_positions_in_meth": "0.04",
            "all_positions_not_in_meth": "4639761",
            "perc_all_positions_not_in_meth": "99.96",
            "total_gatcs_in_ref": "19124",
            "all_gatcs_identified_in_bam": "12",
            "perc_all_gatcs_identified_in_bam": "0.06",
            "all_gatcs_not_identified_in_bam": "19112",
            "perc_all_gatcs_not_identified_in_bam": "99.94",
            "all_gatcs_in_meth": "12",
            "perc_all_gatcs_in_meth": "0.06",
            "all_gatcs_not_in_meth": "19112",
            "perc_all_gatcs_not_in_meth": "99.94",
            "max_possible_methylations": "12",
            "fully_methylated_gatcs": "10",
            "fully_methylated_gatcs_wrt_meth": "83.33",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "0.00",
            "hemi_methylated_gatcs": "2",
            "hemi_methylated_gatcs_wrt_meth": "16.67",
            "hemi_plus_methylated_gatcs": "1",
            "hemi_plus_methylated_gatcs_wrt_meth": "8.33",
            "hemi_minus_methylated_gatcs": "1",
            "hemi_minus_methylated_gatcs_wrt_meth": "8.33",
        },
    },
    ##################################################################
    {
        "name": "unaligned input",
        "features": {"unaligned input", "no clos"},
        "files": {
            "bam": "baseline.bam",
            "fasta": "11mols.fasta",
            "fasta.fai": "11mols.fasta.fai",
            "gff": "expected.sm-analysis.baseline.gff",
            "csv": "expected.sm-analysis.baseline.csv",
            "methylation-report":
            "expected.methylation.sm-analysis.baseline.csv",
        },
        "renames": {},
        "CLOs": (),
        "molecules": [
            '19399571', '23658875', '28836053', '29229724',
            '45744686', '52167204', '55116046', '59179888',
            '60359568', '72352689', '74515099',
        ],
        "num CCS molecules": 12,
        "mol ids with reference mismatch": ('19399571', '29229724'),
        "mols rejected by filters": ('5767891',),
        "statistics": {
            "reference_base_pairs": "4641652",
            "mols_ini": "12",
            "subreads_ini": "2222",
            "mols_used_in_aligned_ccs": "12",
            "perc_mols_used_in_aligned_ccs": "100.00",
            "subreads_used_in_aligned_ccs": "2222",
            "perc_subreads_used_in_aligned_ccs": "100.00",
            "mols_dna_mismatches": "2",
            "perc_mols_dna_mismatches": "16.67",
            "subreads_dna_mismatches": "129",
            "perc_subreads_dna_mismatches": "5.81",
            "filtered_out_mols": "1",
            "perc_filtered_out_mols": "8.33",
            "filtered_out_subreads": "185",
            "perc_filtered_out_subreads": "8.33",
            "mols_in_meth_report": "9",
            "perc_mols_in_meth_report": "75.00",
            "subreads_in_meth_report": "1907",
            "perc_subreads_in_meth_report": "85.82",
            "mols_in_meth_report_with_gatcs": "6",
            "perc_mols_in_meth_report_with_gatcs": "50.00",
            "subreads_in_meth_report_with_gatcs": "1402",
            "perc_subreads_in_meth_report_with_gatcs": "63.10",
            "mols_in_meth_report_without_gatcs": "3",
            "perc_mols_in_meth_report_without_gatcs": "25.00",
            "subreads_in_meth_report_without_gatcs": "505",
            "perc_subreads_in_meth_report_without_gatcs": "22.73",
            "all_positions_in_bam": "2465",
            "perc_all_positions_in_bam": "0.05",
            "all_positions_not_in_bam": "4639187",
            "perc_all_positions_not_in_bam": "99.95",
            "all_positions_in_meth": "2222",
            "perc_all_positions_in_meth": "0.05",
            "all_positions_not_in_meth": "4639430",
            "perc_all_positions_not_in_meth": "99.95",
            "total_gatcs_in_ref": "19124",
            "all_gatcs_identified_in_bam": "15",
            "perc_all_gatcs_identified_in_bam": "0.08",
            "all_gatcs_not_identified_in_bam": "19109",
            "perc_all_gatcs_not_identified_in_bam": "99.92",
            "all_gatcs_in_meth": "13",
            "perc_all_gatcs_in_meth": "0.07",
            "all_gatcs_not_in_meth": "19111",
            "perc_all_gatcs_not_in_meth": "99.93",
            "max_possible_methylations": "13",
            "fully_methylated_gatcs": "11",
            "fully_methylated_gatcs_wrt_meth": "84.62",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "0.00",
            "hemi_methylated_gatcs": "2",
            "hemi_methylated_gatcs_wrt_meth": "15.38",
            "hemi_plus_methylated_gatcs": "1",
            "hemi_plus_methylated_gatcs_wrt_meth": "7.69",
            "hemi_minus_methylated_gatcs": "1",
            "hemi_minus_methylated_gatcs_wrt_meth": "7.69",
        },
    },
    ##################################################################
    {
        "name": "unaligned input but aligned present",
        "features": {"unaligned input", "no clos", "aligned present"},
        "files": {
            "bam": "baseline.bam",
            "aligned bam": "blasr.baseline.bam",
            "pi-shifted aligned bam": "pi-shifted.blasr.baseline.bam",
            "fasta": "11mols.fasta",
            "fasta.fai": "11mols.fasta.fai",
            "gff": "expected.sm-analysis.baseline.gff",
            "csv": "expected.sm-analysis.baseline.csv",
            "methylation-report":
            "expected.methylation.sm-analysis.baseline.csv",
        },
        "renames": {
            # "aligned bam": "blasr.baseline.bam",
            # "pi-shifted aligned bam": "pi-shifted.blasr.baseline.bam",
            # "gff": "expected.sm-analysis.baseline.gff",
            # "csv": "expected.sm-analysis.baseline.csv",
            # "methylation-report":
            # "expected.methylation.sm-analysis.baseline.csv",
        },
        "CLOs": (),
        "molecules": [
            '19399571', '23658875', '28836053', '29229724',
            '45744686', '52167204', '55116046', '59179888',
            '60359568', '72352689', '74515099',
        ],
        "num CCS molecules": 12,
        "mol ids with reference mismatch": ('19399571', '29229724'),
        "mols rejected by filters": (),  # ('19399571',),
        "statistics": {
            "reference_base_pairs": "4641652",
            "mols_ini": "12",
            "subreads_ini": "2222",
            "mols_used_in_aligned_ccs": "12",
            "perc_mols_used_in_aligned_ccs": "100.00",
            "subreads_used_in_aligned_ccs": "2222",
            "perc_subreads_used_in_aligned_ccs": "100.00",
            "mols_dna_mismatches": "2",
            "perc_mols_dna_mismatches": "16.67",
            "subreads_dna_mismatches": "129",
            "perc_subreads_dna_mismatches": "5.81",
            "filtered_out_mols": "1",
            "perc_filtered_out_mols": "8.33",
            "filtered_out_subreads": "185",
            "perc_filtered_out_subreads": "8.33",
            "mols_in_meth_report": "9",
            "perc_mols_in_meth_report": "75.00",
            "subreads_in_meth_report": "1907",
            "perc_subreads_in_meth_report": "85.82",
            "mols_in_meth_report_with_gatcs": "6",
            "perc_mols_in_meth_report_with_gatcs": "50.00",
            "subreads_in_meth_report_with_gatcs": "1402",
            "perc_subreads_in_meth_report_with_gatcs": "63.10",
            "mols_in_meth_report_without_gatcs": "3",
            "perc_mols_in_meth_report_without_gatcs": "25.00",
            "subreads_in_meth_report_without_gatcs": "505",
            "perc_subreads_in_meth_report_without_gatcs": "22.73",
            "all_positions_in_bam": "2465",
            "perc_all_positions_in_bam": "0.05",
            "all_positions_not_in_bam": "4639187",
            "perc_all_positions_not_in_bam": "99.95",
            "all_positions_in_meth": "2222",
            "perc_all_positions_in_meth": "0.05",
            "all_positions_not_in_meth": "4639430",
            "perc_all_positions_not_in_meth": "99.95",
            "total_gatcs_in_ref": "19124",
            "all_gatcs_identified_in_bam": "15",
            "perc_all_gatcs_identified_in_bam": "0.08",
            "all_gatcs_not_identified_in_bam": "19109",
            "perc_all_gatcs_not_identified_in_bam": "99.92",
            "all_gatcs_in_meth": "13",
            "perc_all_gatcs_in_meth": "0.07",
            "all_gatcs_not_in_meth": "19111",
            "perc_all_gatcs_not_in_meth": "99.93",
            "max_possible_methylations": "13",
            "fully_methylated_gatcs": "11",
            "fully_methylated_gatcs_wrt_meth": "84.62",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "0.00",
            "hemi_methylated_gatcs": "2",
            "hemi_methylated_gatcs_wrt_meth": "15.38",
            "hemi_plus_methylated_gatcs": "1",
            "hemi_plus_methylated_gatcs_wrt_meth": "7.69",
            "hemi_minus_methylated_gatcs": "1",
            "hemi_minus_methylated_gatcs_wrt_meth": "7.69",
        },
    },
    ##################################################################
    {
        "name": "unaligned input with one mol crossing ori",
        "features": {"unaligned input", "no clos"},
        "files": {
            "bam": "9mols.bam",
            "aligned bam": "blasr.9mols.bam",
            "pi-shifted aligned bam": "pi-shifted.blasr.9mols.bam",
            "fasta": "pMA685.fa",
            "fasta.fai": "pMA685.fa.fai",
            "gff": "expected.sm-analysis.9mols.gff",
            "csv": "expected.sm-analysis.9mols.csv",
            "methylation-report":
            "expected.V3.methylation.sm-analysis.9mols.csv",
        },
        "renames": {},
        "CLOs": (),
        "molecules": [  # molecules in ccs
            '25294', '150700', '107947',
            '67334', '49610', '86474', '155993'
        ],
        "num CCS molecules": 7,
        "mol ids with reference mismatch": ('49610', '86474',),
        "mols rejected by filters": ('25294',),
        "statistics": {
            "reference_base_pairs": "95304",
            "mols_ini": "9",
            "subreads_ini": "328",
            "mols_used_in_aligned_ccs": "7",
            "perc_mols_used_in_aligned_ccs": "77.78",
            "subreads_used_in_aligned_ccs": "267",
            "perc_subreads_used_in_aligned_ccs": "81.40",
            "mols_dna_mismatches": "2",
            "perc_mols_dna_mismatches": "22.22",
            "subreads_dna_mismatches": "52",
            "perc_subreads_dna_mismatches": "15.85",
            "filtered_out_mols": "1",
            "perc_filtered_out_mols": "11.11",
            "filtered_out_subreads": "37",
            "perc_filtered_out_subreads": "11.28",
            "mols_in_meth_report": "4",
            "perc_mols_in_meth_report": "44.44",
            "subreads_in_meth_report": "178",
            "perc_subreads_in_meth_report": "54.27",
            "mols_in_meth_report_with_gatcs": "1",
            "perc_mols_in_meth_report_with_gatcs": "11.11",
            "subreads_in_meth_report_with_gatcs": "37",
            "perc_subreads_in_meth_report_with_gatcs": "11.28",
            "mols_in_meth_report_without_gatcs": "3",
            "perc_mols_in_meth_report_without_gatcs": "33.33",
            "subreads_in_meth_report_without_gatcs": "141",
            "perc_subreads_in_meth_report_without_gatcs": "42.99",
            "all_positions_in_bam": "3271",
            "perc_all_positions_in_bam": "3.43",
            "all_positions_not_in_bam": "92033",
            "perc_all_positions_not_in_bam": "96.57",
            "all_positions_in_meth": "1740",
            "perc_all_positions_in_meth": "1.83",
            "all_positions_not_in_meth": "93564",
            "perc_all_positions_not_in_meth": "98.17",
            "total_gatcs_in_ref": "62",
            "all_gatcs_identified_in_bam": "2",
            "perc_all_gatcs_identified_in_bam": "3.23",
            "all_gatcs_not_identified_in_bam": "60",
            "perc_all_gatcs_not_identified_in_bam": "96.77",
            "all_gatcs_in_meth": "2",
            "perc_all_gatcs_in_meth": "3.23",
            "all_gatcs_not_in_meth": "60",
            "perc_all_gatcs_not_in_meth": "96.77",
            "max_possible_methylations": "2",
            "fully_methylated_gatcs": "0",
            "fully_methylated_gatcs_wrt_meth": "0.00",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "0.00",
            "hemi_methylated_gatcs": "2",
            "hemi_methylated_gatcs_wrt_meth": "100.00",
            "hemi_plus_methylated_gatcs": "2",
            "hemi_plus_methylated_gatcs_wrt_meth": "100.00",
            "hemi_minus_methylated_gatcs": "0",
            "hemi_minus_methylated_gatcs_wrt_meth": "0.00",
        },
    },
]
TEST_DATA_FOR_SM_ANALYSIS_WIP = [
    case for case in TEST_DATA_FOR_SM_ANALYSIS
    if case["name"] == "unaligned input"
]
TEST_DATA_FOR_SM_ANALYSIS_FAULTY_MOL = [
    {
        "name": "faulty molecule",
        "features": {"unaligned input", "no clos", "faulty mol"},
        "files": {
            "bam": "baseline.bam",
            "fasta": "11mols.fasta",
            "fasta.fai": "11mols.fasta.fai",
            "gff": "expected.sm-analysis.baseline-faultymol.gff",
            "csv": "expected.sm-analysis.baseline-faultymol.csv",
            "methylation-report":
            "expected.methylation.sm-analysis.baseline-faultymol.csv",
        },
        "renames": {},
        "CLOs": (),
        "molecules": [
            '19399571', '23658875', '28836053', '29229724',
            '45744686', '52167204', '55116046', '59179888',
            '60359568', '72352689',
        ],
        "num CCS molecules": 12,
        "mol ids with reference mismatch": ('19399571', '29229724'),
        "mols rejected by filters": ('5767891',),
        "faulty molecules": ('74515099',),
        "statistics": {
            "reference_base_pairs": "4641652",
            "mols_ini": "12",
            "subreads_ini": "2222",
            "mols_used_in_aligned_ccs": "12",
            "perc_mols_used_in_aligned_ccs": "100.00",
            "subreads_used_in_aligned_ccs": "2222",
            "perc_subreads_used_in_aligned_ccs": "100.00",
            "mols_dna_mismatches": "2",
            "perc_mols_dna_mismatches": "16.67",
            "subreads_dna_mismatches": "129",
            "perc_subreads_dna_mismatches": "5.81",
            "filtered_out_mols": "1",
            "perc_filtered_out_mols": "8.33",
            "filtered_out_subreads": "185",
            "perc_filtered_out_subreads": "8.33",
            "mols_in_meth_report": "8",
            "perc_mols_in_meth_report": "66.67",
            "subreads_in_meth_report": "1681",
            "perc_subreads_in_meth_report": "75.65",
            "mols_in_meth_report_with_gatcs": "5",
            "perc_mols_in_meth_report_with_gatcs": "41.67",
            "subreads_in_meth_report_with_gatcs": "1176",
            "perc_subreads_in_meth_report_with_gatcs": "52.93",
            "mols_in_meth_report_without_gatcs": "3",
            "perc_mols_in_meth_report_without_gatcs": "25.00",
            "subreads_in_meth_report_without_gatcs": "505",
            "perc_subreads_in_meth_report_without_gatcs": "22.73",
            "all_positions_in_bam": "2465",
            "perc_all_positions_in_bam": "0.05",
            "all_positions_not_in_bam": "4639187",
            "perc_all_positions_not_in_bam": "99.95",
            "all_positions_in_meth": "2068",
            "perc_all_positions_in_meth": "0.04",
            "all_positions_not_in_meth": "4639584",
            "perc_all_positions_not_in_meth": "99.96",
            "total_gatcs_in_ref": "19124",
            "all_gatcs_identified_in_bam": "15",
            "perc_all_gatcs_identified_in_bam": "0.08",
            "all_gatcs_not_identified_in_bam": "19109",
            "perc_all_gatcs_not_identified_in_bam": "99.92",
            "all_gatcs_in_meth": "11",
            "perc_all_gatcs_in_meth": "0.06",
            "all_gatcs_not_in_meth": "19113",
            "perc_all_gatcs_not_in_meth": "99.94",
            "max_possible_methylations": "11",
            "fully_methylated_gatcs": "10",
            "fully_methylated_gatcs_wrt_meth": "90.91",
            "fully_unmethylated_gatcs": "0",
            "fully_unmethylated_gatcs_wrt_meth": "0.00",
            "hemi_methylated_gatcs": "1",
            "hemi_methylated_gatcs_wrt_meth": "9.09",
            "hemi_plus_methylated_gatcs": "1",
            "hemi_plus_methylated_gatcs_wrt_meth": "9.09",
            "hemi_minus_methylated_gatcs": "0",
            "hemi_minus_methylated_gatcs_wrt_meth": "0.00",
        },
    },
]

EXE_PERM = (stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR)


def get_item_from_row(item, col):
    return item.split()[col]


class TextBam:
    def __init__(self, in_text):
        self._in_text_file = in_text

    def filter(self, line):
        return line

    def read(self):
        stream = StringIO()
        with open(self._in_text_file) as f:
            for line in f:
                if self.filter(line):
                    stream.write(line)
        return stream.getvalue()


class DNASeqLenFilteredTextBam(TextBam):
    def __init__(self, in_text, min_len):
        super().__init__(in_text)
        self.min_len = min_len

    def filter(self, line):
        seq_len = len(get_item_from_row(line, 9))
        if seq_len >= self.min_len:
            return line


class NumberSubreadsFilteredTextBam(TextBam):
    def __init__(self, in_text, min_subreads, col_num):
        super().__init__(in_text)
        self.min_subreads = min_subreads
        self.col_num = col_num
        self.mols = Counter()
        prev = -1
        with open(in_text) as f:
            for line in f:
                mol = get_item_from_row(line, self.col_num)
                self.mols[mol] += 1
                if mol != prev:
                    prev = mol

    def filter(self, line):
        mol = get_item_from_row(line, self.col_num)
        if self.mols[mol] >= self.min_subreads:
            return line


class QualityFilteredTextBam(TextBam):
    def __init__(self, in_text, th):
        super().__init__(in_text)
        self.th = th

    def filter(self, line):
        q = int(get_item_from_row(line, 4))
        if q >= self.th:
            return line


class MappingsBinaryFilteredTextBam(TextBam):
    def __init__(self, in_text, *mappings):
        super().__init__(in_text)
        self.mappings = mappings

    def filter(self, line):
        m = get_item_from_row(line, 1)
        if m in self.mappings:
            return line


class MappingsRatioFilteredTextBam(TextBam):
    def __init__(self, in_text, col_num, *mappings, ratio=1):
        super().__init__(in_text)
        self.mappings = mappings
        self.ratio = ratio
        self.col_num = col_num
        mols = {}
        with open(in_text) as f:
            for line in f:
                mol = get_item_from_row(line, self.col_num)
                mappings_counter = mols.setdefault(mol, Counter())
                mapping = get_item_from_row(line, 1)
                if mapping in mappings:
                    mappings_counter["good"] += 1
                else:
                    mappings_counter["bad"] += 1
        self.mols = mols

    def filter(self, line):
        mol = get_item_from_row(line, self.col_num)
        mappings_counter = self.mols[mol]
        total = mappings_counter["good"]+mappings_counter["bad"]
        ratio_found = mappings_counter["good"]/total
        if ratio_found >= self.ratio:
            return line


class CombinedFiltersTextBam(TextBam):
    def __init__(self, in_text, *filters):
        super().__init__(in_text)
        self.filters = filters

    def filter(self, line):
        for f in self.filters:
            line = f.filter(line)
            if line is None:
                break
        return line


@pytest.fixture()
def bam_file_mol_col_24(tmpdir):
    for el in TEST_BAM_FILE_MOL_COL24.values():
        shutil.copy(DATA_DIR/el, tmpdir)
    tmpdir.chdir()
    bam_dict = {k: Path(v) for k, v in TEST_BAM_FILE_MOL_COL24.items()}
    in_text = bam_dict["in-text"]
    bam_dict["in-text"] = TextBam(in_text)
    bam_dict["dna1500"] = DNASeqLenFilteredTextBam(in_text, min_len=1500)
    bam_dict["subreads100"] = NumberSubreadsFilteredTextBam(
        in_text, col_num=24, min_subreads=100)
    bam_dict["quality254"] = QualityFilteredTextBam(in_text, th=254)
    bam_dict["mappings256"] = MappingsBinaryFilteredTextBam(in_text, "256")
    bam_dict["mappings272+16"] = MappingsBinaryFilteredTextBam(
        in_text, "16", "272")
    bam_dict["mappings256_ratio0.35"] = MappingsRatioFilteredTextBam(
        in_text, 24, "256", ratio=0.35)
    bam_dict["mappings0+16_ratio0.4"] = MappingsRatioFilteredTextBam(
        in_text, 24, "0", "16", ratio=0.4)
    dna_filter = DNASeqLenFilteredTextBam(in_text, min_len=1000)
    subreads_filter = NumberSubreadsFilteredTextBam(
        in_text, col_num=24, min_subreads=70)
    mappings_filter = MappingsBinaryFilteredTextBam(in_text, "256")
    bam_dict["mappings256_subreads70_dna1000"] = CombinedFiltersTextBam(
        in_text, dna_filter, subreads_filter, mappings_filter
    )
    yield bam_dict


@pytest.fixture()
def bam_file_mol_col_19(tmpdir):
    for el in TEST_BAM_FILE_MOL_COL19.values():
        shutil.copy(DATA_DIR/el, tmpdir)
    tmpdir.chdir()
    bam_dict = {k: Path(v) for k, v in TEST_BAM_FILE_MOL_COL19.items()}
    in_text = bam_dict["in-text"]
    bam_dict["in-text"] = TextBam(in_text)
    bam_dict["subreads400"] = NumberSubreadsFilteredTextBam(
        in_text, col_num=19, min_subreads=400)
    bam_dict["mappings256_ratio0.2"] = MappingsRatioFilteredTextBam(
        in_text, 19, "256", ratio=0.2)
    yield bam_dict


@pytest.fixture()
def temporarily_unplug_ipdSummary():
    """It removes from the path all the executables called 'ipdSummary'
    and restores them after the tests are done.

    This can damage the current venv. It could be a good idea to run the
    FTs through tox (or by other means that uses its own environment).
    """
    ipd_summary = shutil.which("ipdSummary")
    replacements = {}
    while ipd_summary:
        new_ipd_summary = ipd_summary+"."
        while Path(new_ipd_summary).exists():
            new_ipd_summary += "."
        shutil.move(ipd_summary, new_ipd_summary)
        replacements[new_ipd_summary] = ipd_summary
        ipd_summary = shutil.which("ipdSummary")
    yield
    for backup, original in replacements.items():
        shutil.move(backup, original)


@pytest.fixture()
def sm_resources(tmpdir):
    """Copies the files found in ./fake.resources/ (fake ipd model
    files) and the files found in the resources/ dir of the
    kineticsTools distribution to the tmp test dir/resources
    """
    tmpdir.chdir()
    rdir = tmpdir.mkdir("resources")
    for rfile in FAKE_RESOURCES_DIR.iterdir():
        shutil.copy(rfile, rdir)
    # r = Requirement.parse("kineticsTools")
    # kt_dir = Path(resource_filename(r, "kineticsTools/resources/"))
    # for rfile in kt_dir.iterdir():
    #     shutil.copy(rfile, rdir)


def create_sm_analysis_fixture_data(tmpdir, request, sm_resources):
    for el in request.param["files"].values():
        shutil.copy(DATA_DIR/el, tmpdir)
    tmpdir.chdir()
    bam_dict = {
        k: Path(v) for k, v in request.param["files"].items()}
    # Some files must be renamed:
    for name, dst in request.param["renames"].items():
        src = bam_dict[name]
        shutil.move(src, dst)
        # The dict must be updated too:
        bam_dict[name] = Path(dst)
    bam_dict["molecules"] = request.param["molecules"]
    bam_dict["num CCS molecules"] = request.param["num CCS molecules"]
    bam_dict["CLOs"] = request.param["CLOs"]
    bam_dict["name"] = request.param["name"]
    bam_dict["features"] = request.param["features"]
    bam_dict["mol ids with reference mismatch"] = request.param[
        "mol ids with reference mismatch"]
    bam_dict["mols rejected by filters"] = request.param[
        "mols rejected by filters"]
    bam_dict["statistics"] = request.param["statistics"]
    return bam_dict


@pytest.fixture(params=TEST_DATA_FOR_SM_ANALYSIS)
def sm_test_data(tmpdir, request, sm_resources):
    bam_dict = create_sm_analysis_fixture_data(tmpdir, request, sm_resources)
    yield bam_dict


@pytest.fixture(params=TEST_DATA_FOR_SM_ANALYSIS_WIP)
def sm_wip_test_data(tmpdir, request, sm_resources):
    bam_dict = create_sm_analysis_fixture_data(tmpdir, request, sm_resources)
    yield bam_dict


@pytest.fixture(params=TEST_DATA_FOR_SM_ANALYSIS_FAULTY_MOL)
def sm_faulty_mol_test_data(tmpdir, request, sm_resources):
    bam_dict = create_sm_analysis_fixture_data(tmpdir, request, sm_resources)
    yield bam_dict


@pytest.fixture()
def prepend_to_path(tmpdir):
    tmpdir.chdir()
    bindir = tmpdir.mkdir("bin")
    old_path = os.get_exec_path()
    new_path = ":".join([str(bindir)]+old_path)
    os.environ["PATH"] = new_path
    yield bindir
    os.environ["PATH"] = ":".join(old_path)


def render_template_program(src, exit_code=0, stderr="", failing_mols=()):
    with open(src) as template_f:
        code = template_f.read()
        code = code.replace("_DATA_DIR_", repr(DATA_DIR))
        code = code.replace("_RESOURCES_DIR_", repr(FAKE_RESOURCES_DIR))
        code = code.replace("_EXIT_CODE_", repr(exit_code))
        code = code.replace("_STDERR_", repr(stderr))
        code = code.replace("_FAILING_MOLS_", repr(failing_mols))
    return code


def make_exe(code, name, tmpsubdir):
    exe = tmpsubdir.join(name)
    exe.write(code)
    os.chmod(exe, EXE_PERM)


@pytest.fixture()
def install_pbindex(tmpdir, prepend_to_path):
    pbindex_code = render_template_program(FAKE_TOOLS_DIR/"pbindex.py")
    make_exe(pbindex_code, "pbindex", prepend_to_path)
    yield


@pytest.fixture()
def install_pbindex_no_path(tmpdir):
    pbindex_code = render_template_program(FAKE_TOOLS_DIR/"pbindex.py")
    path = tmpdir.mkdir(RELATIVE_BIN_NO_PATH_DIR)
    make_exe(pbindex_code, "pbindex", path)
    yield


@pytest.fixture(params=TEST_DATA_FOR_SM_ANALYSIS_FAULTY_MOL)
def install_pbindex_1mol_fails(tmpdir, request, prepend_to_path):
    code = render_template_program(
        FAKE_TOOLS_DIR/"pbindex.py",
        stderr="who knows what happens here",
        failing_mols=request.param["faulty molecules"]
    )
    make_exe(code, "pbindex", prepend_to_path)
    yield


@pytest.fixture()
def install_ipdSummary(tmpdir, prepend_to_path):
    code = render_template_program(FAKE_TOOLS_DIR/"ipdSummary.py")
    make_exe(code, "ipdSummary", prepend_to_path)
    yield


@pytest.fixture()
def install_ipdSummary_no_path(tmpdir):
    code = render_template_program(FAKE_TOOLS_DIR/"ipdSummary.py")
    path = tmpdir.mkdir(RELATIVE_BIN_NO_PATH_DIR)
    make_exe(code, "ipdSummary", path)
    yield


@pytest.fixture(params=TEST_DATA_FOR_SM_ANALYSIS_FAULTY_MOL)
def install_ipdSummary_1mol_fails(tmpdir, request, prepend_to_path):
    code = render_template_program(
        FAKE_TOOLS_DIR/"ipdSummary.py",
        stderr="whatever I feel like I wanna do",
        failing_mols=request.param["faulty molecules"]
    )
    make_exe(code, "ipdSummary", prepend_to_path)
    yield


@pytest.fixture()
def install_ccs(tmpdir, prepend_to_path):
    code = render_template_program(FAKE_TOOLS_DIR/"ccs.py")
    make_exe(code, "ccs", prepend_to_path)
    yield


@pytest.fixture()
def install_ccs_without_result(tmpdir, prepend_to_path):
    code = render_template_program(FAKE_TOOLS_DIR/"ccs_without_result.py")
    make_exe(code, "ccs", prepend_to_path)
    yield


@pytest.fixture()
def install_ccs_with_error(tmpdir, prepend_to_path):
    code = render_template_program(
        FAKE_TOOLS_DIR/"ccs.py", exit_code=1,
        stderr="libchufa.so not found"
    )
    make_exe(code, "ccs", prepend_to_path)
    yield


@pytest.fixture()
def install_ccs_with_empty_error(tmpdir, prepend_to_path):
    code = render_template_program(
        FAKE_TOOLS_DIR/"ccs.py", exit_code=1,
        stderr=""
    )
    make_exe(code, "ccs", prepend_to_path)
    yield


@pytest.fixture()
def install_ccs_without_result_with_error(tmpdir, prepend_to_path):
    code = render_template_program(
        FAKE_TOOLS_DIR/"ccs_without_result.py", exit_code=1,
        stderr="libchufa.so not found"
    )
    make_exe(code, "ccs", prepend_to_path)
    yield


@pytest.fixture()
def install_blasr(tmpdir, prepend_to_path):
    code = render_template_program(FAKE_TOOLS_DIR/"blasr.py")
    make_exe(code, "blasr", prepend_to_path)
    yield


@pytest.fixture()
def install_blasr_no_path(tmpdir):
    code = render_template_program(FAKE_TOOLS_DIR/"blasr.py")
    path = tmpdir.mkdir(RELATIVE_BIN_NO_PATH_DIR)
    make_exe(code, "blasr", path)
    yield


@pytest.fixture
def missing_bam(tmpdir):
    tmpdir.chdir()
    name = "none.bam"
    bam = tmpdir.join(name)
    while bam.exists():
        name = "none." + name
        bam = tmpdir.join(name)
    yield bam


@pytest.fixture
def forbidden_bam(tmpdir):
    """BAM file located in a directory that is permission-wise
    unreachable"""
    tmpdir.chdir()
    locked = tmpdir.mkdir("locked")
    bam = locked.join("unreachable.bam")
    os.chmod(locked, 0)
    yield bam
    os.chmod(locked, EXE_PERM)
