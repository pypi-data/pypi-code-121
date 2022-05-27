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

from ..constants import (
    DEFAULT_BLASR_PROGRAM, DEFAULT_PBINDEX_PROGRAM, DEFAULT_IPDSUMMARY_PROGRAM,
    DEFAULT_NUM_SIMULTANEOUS_IPDSUMMARYS, DEFAULT_NUM_WORKERS_PER_IPDSUMMARY,
    DEFAULT_NUM_WORKERS_BLASR, DEFAULT_MODIFICATION_TYPE,
    DEFAULT_DNA_LEN_TH, DEFAULT_NUM_MOL_TH, DEFAULT_QUAL_TH,
    DEFAULT_MINIMUM_MAPPING_RATIO,
)
from .. import __version__


BAM_FILE_METAVAR = "BAM-FILE"
INPUT_BAM_FILE_HELP = "input file in BAM format"
ALIGNMENT_FILE_METAVAR = "ALIGNMENT-FILE"
FASTA_FILE_HELP = (
    "input file containing the alignment in FASTA format (typically "
    "a file ending in '.fa' or '.fasta'). A '.fai' file ('%(metavar)s.fai') "
    "is also expected to be found side-by-side to %(metavar)s."
)
INPUT_BAM_FILE_4FILTER_HELP = INPUT_BAM_FILE_HELP + (
    ". The output will be another"
    " %(metavar)s with the same name but prefixed with 'parsed.'"
)


# Options for sm-analysis:
# Refactor hint: replace options by instances of custom dataclasses.

_INPUT_BAM_FILE = (
    ("input_bam_file",),
    dict(metavar=BAM_FILE_METAVAR, type=Path, help=INPUT_BAM_FILE_HELP)
)

_FASTA = (
    ("fasta",),
    dict(metavar=ALIGNMENT_FILE_METAVAR, type=Path, help=FASTA_FILE_HELP)
)

_IPD_MODEL = (
    ("-M", "--ipd-model"),
    dict(type=Path, metavar="MODEL",
         help=(
            "model to be used by ipdSummary to identify the type of "
            "modification. MODEL must be either the model name or the "
            "path to the ipd model. "
            "First, the program will make an attempt "
            "to interprete MODEL as a path to a file defining a model; "
            "if that fails, MODEL will be understood to be "
            "the name of a model that must be "
            "accessible in the resources directory of kineticsTools "
            "(e.g. '-M SP3-C3' would trigger a "
            "search for a file called 'SP3-C3.npz.gz' within the "
            "directory with models provided by kineticsTools). "
            "If this option is not given, the default model in "
            "ipdSummary is used.")
         )
)

_BLASR_PATH = (
    ("-b", "--blasr-path"),
    dict(metavar="PATH", default=DEFAULT_BLASR_PROGRAM,
         help="path to blasr program (default: '%(default)s')"
         )
)

_PBINDEX_PATH = (
    ("-p", "--pbindex-path"),
    dict(metavar="PATH", default=DEFAULT_PBINDEX_PROGRAM, type=Path,
         help="path to pbindex program (default: '%(default)s')"
         )
)

_IPDSUMMARY_PATH = (
    ("-i", "--ipdsummary-path"),
    dict(metavar="PATH", default=DEFAULT_IPDSUMMARY_PROGRAM, type=Path,
         help="path to ipdSummary program (default: '%(default)s')"
         )
)

_NUM_SIMULTANEOUS_IPDSUMMARYS = (
    ("-N", "--num-simultaneous-ipdsummarys"),
    dict(type=int, default=DEFAULT_NUM_SIMULTANEOUS_IPDSUMMARYS, metavar="NUM",
         help=(
             "number of simultaneous instances of ipdSummary that will "
             "cooperate to process the molecules (default: %(default)s)")
         )
)

_NUM_WORKERS_PER_IPDSUMMARY = (
    ("-n", "--num-workers-per-ipdsummary"),
    dict(type=int, default=DEFAULT_NUM_WORKERS_PER_IPDSUMMARY, metavar="NUM",
         help=(
             "number of worker processes that each instance of ipdSummary will"
             " spawn (default: %(default)s)")
         )
)

_NPROCS_BLASR = (
    ("--nprocs-blasr",),
    dict(type=int, default=DEFAULT_NUM_WORKERS_BLASR, metavar="NUM",
         help=(
             "number of worker processes that each instance of blasr will "
             "spawn (default: %(default)s)")
         )
)

_PARTITION = (
    ("-P", "--partition"),
    dict(metavar="PARTITION:NUMBER-OF-PARTITIONS",
         help=(
             "this option instructs the program to only analyze a fraction "
             "(partition) of the molecules present in the input bam file. The "
             "file is divided in `NUMBER OF PARTITIONS` (almost) equal pieces "
             "but ONLY the PARTITION-th partition (fraction) is analyzed. "
             "For instance, `--partition 3:7` means that the bam file is "
             "divided in seven pieces but only the third piece is analyzed "
             "(by default all the file is analyzed)")
         )
)

_ALIGNED_CCS_BAM_FILE = (
    ("-C", "--aligned-CCS-bam-file"),
    dict(metavar="BAM-FILE", type=Path,
         help=(
             "aligned CCS file in BAM format used to produce a report of "
             "methylation states. If provided, it "
             "is used in the production of the methylation states report. "
             "If missing, one is generated from the CCS file using 'blasr'")
         )
)

_CCS_BAM_FILE = (
    ("-c", "--CCS-bam-file"),
    dict(metavar="BAM-FILE", type=Path,
         help=(
             "CCS file in BAM format used to produce a report of "
             "methylation states. If provided, and the aligned version of "
             "it is not provided, it is aligned and the result is used in the "
             "production of the methylation states report. If missing, one is "
             "generated from the original BAM file using the 'ccs' program")
         )
)

_KEEP_TEMP_DIR = (
    ("--keep-temp-dir",),
    dict(action="store_true",
         help=(
             "should we make a copy of the temporary files generated?"
             " (default: %(default)s)")
         )
)

_MODIFICATION_TYPES = (
    ("-m", "--modification-types"),
    dict(default=[DEFAULT_MODIFICATION_TYPE], nargs="+", metavar="MOD-TYPE",
         help=(
             "focus only in the requested modification types (default: "
             "%(default)s)")
         )
)

_ONLY_PRODUCE_METHYLATION_REPORTS = (
    ("--only-produce-methylation-report",),
    dict(action="store_true",
         help=(
             "use this flag to only produce the methylation report from the "
             "per detection csv file (default: %(default)s)")
         )
)

# Options for bam-filter:

_INPUT_BAM_FILE_4FILTER = (
    ("input_bam_file",),
    dict(metavar=BAM_FILE_METAVAR, type=Path, help=INPUT_BAM_FILE_4FILTER_HELP)
)

_MIN_DNA_SEQ_LENGTH = (
    ("-l", "--min-dna-seq-length"),
    dict(default=DEFAULT_DNA_LEN_TH, type=int, metavar="NUM",
         help=(
             "minimum length of DNA sequence to be kept "
             "(default: %(default)s)")
         )
)

_MIN_SUBREADS_PER_MOLECULE = (
    ("-r", "--min-subreads-per-molecule"),
    dict(default=DEFAULT_NUM_MOL_TH, type=int, metavar="NUM",
         help=(
             "minimum number of subreads per molecule to keep it (default: "
             "%(default)s)")
         )
)

_QUALITY_THRESHOLD = (
    ("-q", "--quality-threshold"),
    dict(default=DEFAULT_QUAL_TH, type=int, metavar="NUM", choices=range(256),
         help=(
             "quality threshold of the sample. Between 0 (the lowest) and 255 "
             "(the highest) (default: %(default)s)")
         )
)

_MAPPINGS = (
    ("-m", "--mappings"),
    dict(default="all", nargs="+", metavar="MAPPING",
         help=(
             "keep only the requested (space separated) list of mappings "
             "(default: keep %(default)s)")
         )
)

_MIN_RELATIVE_MAPPING_RATIO = (
    ("-R", "--min-relative-mapping-ratio"),
    dict(default=DEFAULT_MINIMUM_MAPPING_RATIO, metavar="NUM", type=float,
         help=(
             "minimum ratio (amount of found wanted mappings/all mappings "
             "present) in order to keep the data point (default: take all)")
         )
)

# Common options:
_VERBOSE = (("-v", "--verbose"), dict(action="count", default=0))

_VERSION = (("--version",), dict(action="version", version=__version__))


# Full lists of options for each program:

SM_ANALYSIS_OPTS = [
    _INPUT_BAM_FILE,
    _FASTA,
    _IPD_MODEL,
    _BLASR_PATH,
    _PBINDEX_PATH,
    _IPDSUMMARY_PATH,
    _NUM_SIMULTANEOUS_IPDSUMMARYS,
    _NUM_WORKERS_PER_IPDSUMMARY,
    _NPROCS_BLASR,
    _PARTITION,
    _ALIGNED_CCS_BAM_FILE,
    _CCS_BAM_FILE,
    _KEEP_TEMP_DIR,
    _MODIFICATION_TYPES,
    _ONLY_PRODUCE_METHYLATION_REPORTS,
    _VERBOSE,
    _VERSION,
]

BAM_FILTER_OPTS = [
    _INPUT_BAM_FILE_4FILTER,
    _MIN_DNA_SEQ_LENGTH,
    _MIN_SUBREADS_PER_MOLECULE,
    _QUALITY_THRESHOLD,
    _MAPPINGS,
    _MIN_RELATIVE_MAPPING_RATIO,
    _VERBOSE,
    _VERSION
]
