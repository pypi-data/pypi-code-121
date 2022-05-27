#######################################################################
#
# Copyright (C) 2020, 2021, 2022 David Palao
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

SM_ANALYSIS_EXE = "sm-analysis"
SM_ANALYSIS_GUI_EXE = "sm-analysis-gui"
PROJECT_WEBSITE_URL = "https://gitlab.com/dvelazquez/pacbio-data-processing"
PROJECT_DOCUMENTATION_URL = "https://pacbio-data-processing.readthedocs.io/"

SM_ANALYSIS_DESC = (
    "Single Molecule Analysis of DNA modifications in PacBio sequencing"
    " data. This program splits a PacBio BAM file into 'molecules', "
    "filters the individual molecules to ensure high quality of data "
    "and analyzes each single-molecule BAM file using ipdSummary (from "
    "the kineticsTools package). The output produced contains detailed "
    "information about individual detections."
)

BAM_FILTER_EXE = "bam-filter"

BAM_FILTER_DESC = (
    "Program to filter BAM files after Pacbio sequencing. "
    "Different filters can be applied on demand (by default all the "
    "filters are disabled). "
    "The order in which the filters are applied is: "
    "1) remove rows with len of DNA sequence under some threshold; "
    "2) take only molecules with a minimum number of subreads; "
    "3) choose molecules with sequencing quality above some threshold; "
    "and "
    "4) choose mapping. "
)

SAMTOOLS_GET_HEADER = ("samtools", "view", "-H")
SAMTOOLS_GET_BODY = ("samtools", "view")
SAMTOOLS_WRITE_BAM = ("samtools", "view", "-S", "-bh")

DNA_SEQ_COLUMN = 9
ASCII_QUALS_COLUMN = DNA_SEQ_COLUMN+1
QUALITY_COLUMN = 4
MAPPING_COLUMN = 1

DEFAULT_PBINDEX_PROGRAM = "pbindex"

DEFAULT_IPDSUMMARY_PROGRAM = "ipdSummary"
DEFAULT_NUM_SIMULTANEOUS_IPDSUMMARYS = 1
DEFAULT_NUM_WORKERS_PER_IPDSUMMARY = 1
DEFAULT_MODIFICATION_TYPE = "m6A"

INDEX_SUF = ".pbi"
GFF_SUF = ".gff"

DEFAULT_BLASR_PROGRAM = "blasr"
DEFAULT_NUM_WORKERS_BLASR = 1
BLASR_PREF = f"{DEFAULT_BLASR_PROGRAM}."

EXIT_CODE_FAILURE = 1

DEFAULT_DNA_LEN_TH = 0
STANDARD_MIN_DNA_LEN = 50
DEFAULT_NUM_MOL_TH = 1
STANDARD_MIN_NUM_SUBREADS = 20
DEFAULT_QUAL_TH = 0
STANDARD_MIN_QUAL = 254
DEFAULT_MINIMUM_MAPPING_RATIO = 0
STANDARD_ACCEPTED_MAPPINGS = ("0", "16")
STANDARD_MAPPINGS_RATIO = 0.9

PI_SHIFTED = "pi-shifted"
PI_SHIFTED_PREF = PI_SHIFTED
PI_SHIFTED_VARIANT = PI_SHIFTED
STRAIGHT = "straight"
STRAIGHT_PREF = ""
STRAIGHT_VARIANT = STRAIGHT

SHORT_LICENSE = """
PacBioDataProcessing is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PacBio data processing is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PacBioDataProcessing. If not, see <http://www.gnu.org/licenses/>.
"""
WAIT_TIME_SECONDS = 10
NEXT_WAIT_TIME_FACTOR = 2
