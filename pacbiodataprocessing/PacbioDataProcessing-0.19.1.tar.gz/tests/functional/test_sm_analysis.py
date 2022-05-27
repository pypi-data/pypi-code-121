#######################################################################
#
# Copyright (C) 2020-2022 David Palao
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

"""Functional Tests for `sm-analysis` utility."""

import re
import os
from pathlib import Path
import shutil
from datetime import datetime, timedelta
import socket
from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
from hashlib import md5
import imghdr
import subprocess as sp
import time

from pacbio_data_processing.constants import SM_ANALYSIS_EXE
from pacbio_data_processing import __version__ as VERSION
from pacbio_data_processing.bam import BamFile

import pyfaidx

from .utils import (
    run_sm_analysis, normalize_whitespaces, temporarily_rename_file,
    SummaryReportParser, remove_later, run_later, count_marker_files
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR/"data"
GFF3_URL = (
    "https://github.com/The-Sequence-Ontology/Specifications/blob/master"
    "/gff3.md"
)

SM_ANALYSIS_IMAGES = {
    "molecule_type_bars": "figures/molecule_type_bars.png",
    "molecule_len_histogram": "figures/molecule_length_histogram.png",
    "position_coverage_bars": "figures/position_coverage_bars.png",
    "position_coverage_history": "figures/position_coverage_history.png",
    "gatc_coverage_bars": "figures/gatc_coverage_bars.png",
    "meth_type_bars": "figures/meth_type_bars.png",
}
MISSING_CCS_MSG = (
    "Aligned CCS file cannot be produced without CCS "
    "file. Trying to produce it..."
)


def clean_run_results(*paths):
    """Remove the files given after removing the prefix 'expected.' from
    the name of the file (the directory is excluded). E.g.
    clean_run_results(Path('/tmp/expected.myoutput.text'))

    will try to remove a file called '/tmp/myoutput.text'

    This function is useful if within a test case several runs of the
    same program are done (maybe with slightly different flags).
    """
    for path in paths:
        if path is None:
            continue
        if path.name.startswith("expected."):
            new_name = path.name[9:]
            to_rm = path.with_name(new_name)
        else:
            to_rm = path
        try:
            os.unlink(to_rm)
        except OSError as e:
            print(f"path={path.name}")
            print(f"Cannot delete file '{to_rm}'")
            print("Exception:")
            print(e)
            print("-"*50)


class SmAnalysisMixIn:
    def collect_opts_for_tests(self, sm_test_data):
        # Should clos be a list or a tuple?
        self.clos = sm_test_data["CLOs"]
        self.bam = sm_test_data["bam"]
        self.statistics_of_test_fixture = sm_test_data["statistics"]
        self.aligned_bam = sm_test_data.get("aligned bam")
        self.pi_shifted_aligned_bam = sm_test_data.get(
            "pi-shifted aligned bam")
        self.fasta = sm_test_data["fasta"]
        self.pi_shifted_fasta = self.fasta.with_name(
            "pi-shifted."+self.fasta.name)
        self.expected_gff = sm_test_data["gff"]
        self.expected_csv = sm_test_data["csv"]
        self.expected_meth_report = sm_test_data["methylation-report"]
        self.imperfect_molecules = sm_test_data[
            "mol ids with reference mismatch"]
        self.rejected_molecules = sm_test_data["mols rejected by filters"]
        self.all_molecules = sm_test_data["molecules"]
        self.one_mol_bams = [
            str(self.bam).replace(
                ".bam", f".{m}.bam") for m in self.all_molecules
            if m not in self.imperfect_molecules
        ]
        self.analyzed_molecules = (
            set(self.all_molecules)
            - set(self.rejected_molecules)
            - set(self.imperfect_molecules)
        )
        self.num_ccs_mols = sm_test_data["num CCS molecules"]
        self.unaligned_input = ("unaligned input" in sm_test_data["features"])
        self.faulty_molecules = {
            _: {} for _ in sm_test_data.get("faulty molecules", ())
        }

    @cached_property
    def executor(self) -> ThreadPoolExecutor:
        """Just in case it is needed, an executor can be created."""
        return ThreadPoolExecutor(max_workers=2)

    def make_ccs(self, missing_ok=False):
        """It calls the ccs program and deletes the marker file possibly
        created by the fake ccs tools.
        """
        proc = sp.Popen(
            ["ccs", self.bam, self.ccs], stdout=sp.PIPE, stderr=sp.PIPE
        )
        marker = Path(f".ccs.pid.{proc.pid}")
        while True:
            try:
                marker.unlink(missing_ok)
            except OSError:
                files = os.listdir()
                print("cwd:", os.getcwd())
                print(f"  trying to remove: {marker}")
                print(f"   dir contents ({len(files)} files):", files)
                time.sleep(1)
            else:
                break

    @cached_property
    def ccs(self):
        """It returns the Path corresponding to the *canonical* ccs
        file constructed from ``self.bam``."""
        ccs_name = "ccs."+self.bam.name
        return self.bam.with_name(ccs_name)

    @cached_property
    def blasr_ccs(self):
        blasr_ccs_name = "blasr."+self.ccs.name
        return self.ccs.with_name(blasr_ccs_name)

    @cached_property
    def pi_shifted_blasr_ccs(self):
        pi_shifted_blasr_ccs_name = "pi-shifted.blasr."+self.ccs.name
        return self.ccs.with_name(pi_shifted_blasr_ccs_name)

    @property
    def partition_prefix(self):
        partition_prefix = ""
        for arg in ("-P", "--partition"):
            if arg in self.clos:
                partition, partitions = (
                    self.clos[self.clos.index(arg)+1].split(":")
                )
                partition_prefix = f"partition_{partition}of{partitions}."
        return partition_prefix

    @property
    def found_meth_report(self):
        return self.bam.with_name(
            "methylation."+self.partition_prefix+"sm-analysis."
            + self.bam.stem+".csv"
        )

    @property
    def found_summary_report(self):
        return self.bam.with_name(
            "summary."+self.partition_prefix+"sm-analysis."
            + self.bam.stem+".html"
        )

    @property
    def found_csv(self):
        return self.bam.with_name(
            self.partition_prefix+"sm-analysis."+self.bam.stem+".csv"
        )

    @property
    def found_gff(self):
        return self.bam.with_name(
            self.partition_prefix+"sm-analysis."+self.bam.stem+".gff"
        )

    def check_temp_files(
            self, output, one_mol_bams, rejected_molecules, options):
        """Aux method: checks temp files backup related messages and looks
        for temp files.
        """
        assert "keep temp dir: yes" in output
        if "--verbose" in options:
            assert re.search(
                r"Copied temporary dir to: 'tmp[\w]+.backup'",
                output) is not None
        rootg = Path(".").iterdir()
        tempdirs = {
            x for x in rootg if x.is_dir() and x.name.startswith("tmp")}
        tempfiles = set()
        for d in tempdirs:
            tempfiles.update({_ for _ in d.iterdir()})
        for one_mol_bam in one_mol_bams:
            rejected = any(
                _ in one_mol_bam for _ in rejected_molecules)
            assert any(i.match(f"tmp*/{one_mol_bam}") for i in tempfiles)
            if not rejected:
                assert any(
                    i.match(f"tmp*/{one_mol_bam}.pbi") for i in tempfiles
                )

    def check_modification_types(self, output, options):
        mod_types = ['m6A']
        for arg in ("-m", "--modification-types"):
            if arg in options:
                mod_types = []
                # very basic parsing of clos:
                idx = options.index(arg)+1
                for mod_type in options[idx:]:
                    if mod_type.startswith("-"):
                        break
                    else:
                        mod_types.append(mod_type)
        assert f"modification types: {mod_types}" in output
        for mod_type in mod_types:
            if mod_type != "m6A":
                ignore_msg = (
                    f"[methylation report] modifications of type '{mod_type}'"
                    " will be ignored"
                )
                assert ignore_msg in output

    def check_for_gff(self):
        """Auxiliary method to directly check that the gff file is correct."""
        with open(self.found_gff) as gff_f:
            with open(self.expected_gff) as expected_gff_f:
                expected_gff_lines = [
                    _ for _ in expected_gff_f.readlines() if
                    not _.startswith("#")
                ]
                gff_lines = [
                    _ for _ in gff_f.readlines() if not _.startswith("#")
                ]
                assert expected_gff_lines == gff_lines

    def check_for_csv(self, output):
        with open(self.found_csv) as csv_f:
            with open(self.expected_csv) as expected_csv_f:
                assert expected_csv_f.read() == csv_f.read()
        own_output_message = f"Own output '{self.found_csv}' created"
        assert own_output_message in output

    def check_ipdsummary_program_and_processes(
            self, options, output, cmd_result):
        ipdSummary = "ipdSummary"
        for arg in ("-i", "--ipdsummary-path"):
            if arg in options:
                ipdSummary = options[options.index(arg)+1]
                break
        assert f"ipd program: '{ipdSummary}'" in output

        ipdsummary_instances = 1
        for arg in ("-N", "--num-simultaneous-ipdsummarys"):
            if arg in options:
                ipdsummary_instances = int(options[options.index(arg)+1])
                break
        assert f"# ipd program instances: {ipdsummary_instances}" in output

        ipdsummary_workers = 1
        for arg in ("-n", "--num-workers-per-ipdsummary"):
            if arg in options:
                ipdsummary_workers = int(options[options.index(arg)+1])
                break
        assert f"# workers per ipd instance: {ipdsummary_workers}" in output
        # (the following is because if num workers > 1, then the processes
        #  are the workers plus 1 times the number of ipdsummary instances)
        # The expression is:
        #  total #procs = #mols*(1+workers) = #mols + #mols*workers
        num_healthy_mols = len(self.analyzed_molecules)
        expected_ipdsummary_processes = num_healthy_mols*ipdsummary_workers
        if "--only-produce-methylation-report" not in options:
            assert (
                expected_ipdsummary_processes
                == count_marker_files("ipdSummary")
            )

    def check_one_molecule_bam_files_produced(self, output, options):
        if "--only-produce-methylation-report" not in options:
            for one_mol_file in self.one_mol_bams:
                if self.unaligned_input:
                    prefixes = ["blasr.", "pi-shifted.blasr."]
                else:
                    prefixes = [""]
                matches = []
                for pref in prefixes:
                    one_mol_bam_produced_msg = (
                        f"One-molecule BAM file written: \\w+/{pref}"
                        f"{one_mol_file}"
                    )
                    matches.append(re.search(one_mol_bam_produced_msg, output))
                assert any(matches), one_mol_bam_produced_msg

    def make_expected_summary_report(self, clos):
        stats = self.statistics_of_test_fixture
        methylation_report = self.found_meth_report
        raw_detections = self.found_csv
        gff_results = self.found_gff
        h1 = "Summary report: Single Molecule Methylation Analysis"
        overview_head = h1 + " >> " + "Overview"
        results_head = h1 + " >> " + "Result filenames"
        inputs_head = h1 + " >> " + "Input files"
        bam_file_head = inputs_head + " >> " + "BAM File"
        reference_file_head = inputs_head + " >> " + "Reference"
        mols_subs_head = h1 + " >> " + "Molecules/subreads"
        seq_coverage_head = h1 + " >> " + "Sequencing Position Coverage"
        GATCs_head = h1 + " >> " + "GATCs"
        methylations_head = GATCs_head + " >> " + "Methylations"

        # There exists an HTML file containing a summary of the process...
        overview_dict = {
            "PacBio Data Processing version": VERSION,
            "Date": datetime.now().isoformat(timespec="minutes"),
            "Program name": "sm-analysis",
            "Program options": " ".join(
                [str(self.bam), str(self.fasta)]+list(clos)),
            "Hostname": socket.gethostname(),
        }
        # ...a summary with result files...
        results_dict = {
            "Methylation report": f"{methylation_report}",
            "Raw detections": f"{raw_detections}",
            "Joint ": f"{gff_results}",
        }
        bamfile = BamFile(self.bam)
        # ...some info about the input BAM...
        bam_dict = {
            "File name": str(self.bam),
            "Size (bytes)": str(self.bam.stat().st_size),
            "MD5 checksum (full)": md5(open(self.bam, "rb").read()
                                       ).hexdigest(),
            "MD5 checksum (body)": bamfile.md5sum_body,
        }
        # ...as well as info about the input fasta...
        genes = pyfaidx.Fasta(str(self.fasta))
        gene = genes[0]
        reference_base_pairs = len(gene)
        reference_dict = {
            "File name": str(self.fasta),
            "Reference name": gene.long_name.strip(),
            "Size (base pairs)": str(reference_base_pairs),
            "MD5 checksum (fully capitalized string)": md5(
                str(gene).upper().encode("utf8")
            ).hexdigest(),
        }
        # ...statistics about the molecules and subreads...
        num_mols = bamfile.num_molecules
        num_subreads = bamfile.num_subreads

        molecules_subreads_dict = {
            "Initial": {
                "number of molecules": "{mols_ini}".format(**stats),
                "number of subreads": "{subreads_ini}".format(**stats),
            },
            "Used in aligned CCS BAM": {
                "number of molecules": (
                    "{mols_used_in_aligned_ccs} "
                    "({perc_mols_used_in_aligned_ccs} %)"
                ).format(**stats),
                "number of subreads": (
                    "{subreads_used_in_aligned_ccs} "
                    "({perc_subreads_used_in_aligned_ccs} %)"
                ).format(**stats),
            },
            "DNA mismatch discards": {
                "number of molecules": (
                    "{mols_dna_mismatches} ({perc_mols_dna_mismatches} %)"
                ).format(**stats),
                "number of subreads": (
                    "{subreads_dna_mismatches} "
                    "({perc_subreads_dna_mismatches} %)"
                ).format(**stats),
            },
            "Filtered out": {
                "number of molecules": (
                    "{filtered_out_mols} ({perc_filtered_out_mols} %)"
                ).format(**stats),
                "number of subreads": (
                    "{filtered_out_subreads} ({perc_filtered_out_subreads} %)"
                ).format(**stats),
            },
            "In methylation report...": {
                "number of molecules": (
                    "{mols_in_meth_report} ({perc_mols_in_meth_report} %)"
                ).format(**stats),
                "number of subreads": (
                    "{subreads_in_meth_report} "
                    "({perc_subreads_in_meth_report} %)"
                ).format(**stats),
            },
            "...only with GATCs": {
                "number of molecules": (
                    "{mols_in_meth_report_with_gatcs} "
                    "({perc_mols_in_meth_report_with_gatcs} %)"
                ).format(**stats),
                "number of subreads": (
                    "{subreads_in_meth_report_with_gatcs} "
                    "({perc_subreads_in_meth_report_with_gatcs} %)"
                ).format(**stats),
            },
            "...only without GATCs": {
                "number of molecules": (
                    "{mols_in_meth_report_without_gatcs} "
                    "({perc_mols_in_meth_report_without_gatcs} %)"
                ).format(**stats),
                "number of subreads": (
                    "{subreads_in_meth_report_without_gatcs} "
                    "({perc_subreads_in_meth_report_without_gatcs} %)"
                ).format(**stats),
            },
        }

        # ...statistics about the coverage...
        seq_coverage_dict = {
            "Number of base pairs in reference": (
                f"{reference_base_pairs}"
            ),
            "Positions covered by molecules in the BAM file": (
                "{all_positions_in_bam} ({perc_all_positions_in_bam} %)"
            ).format(**stats),
            "Positions NOT covered by molecules in the BAM file": (
                "{all_positions_not_in_bam} "
                "({perc_all_positions_not_in_bam} %)"
            ).format(**stats),
            "Positions covered by molecules in the methylation report": (
                "{all_positions_in_meth} ({perc_all_positions_in_meth} %)"
            ).format(**stats),
            "Positions NOT covered by molecules in the methylation report": (
                "{all_positions_not_in_meth} "
                "({perc_all_positions_not_in_meth} %)"
            ).format(**stats),
        }

        # ...about the GATCs...
        GATCs_dict = {
            "Total number of GATCs in reference": (
                "{total_gatcs_in_ref}"
            ).format(**stats),
            "Number of GATCs identified in the BAM file": (
                "{all_gatcs_identified_in_bam} "
                "({perc_all_gatcs_identified_in_bam} %)"
            ).format(**stats),
            "Number of GATCs NOT identified in the BAM file": (
                "{all_gatcs_not_identified_in_bam} "
                "({perc_all_gatcs_not_identified_in_bam} %)"
            ).format(**stats),
            "Number of GATCs in methylation report": (
                "{all_gatcs_in_meth} ({perc_all_gatcs_in_meth} %)"
            ).format(**stats),
            "Number of GATCs NOT in methylation report": (
                "{all_gatcs_not_in_meth} ({perc_all_gatcs_not_in_meth} %)"
            ).format(**stats),
        }

        # ...and about the methylations:
        methylations_dict = {
            "Total number of GATCs in all the analyzed molecules": (
                "{max_possible_methylations}".format(**stats)
                ),
            "Fully methylated": (
                "{fully_methylated_gatcs} "
                "({fully_methylated_gatcs_wrt_meth} %)"
                ).format(**stats),
            "Fully unmethylated": (
                "{fully_unmethylated_gatcs} "
                "({fully_unmethylated_gatcs_wrt_meth} %)"
                ).format(**stats),
            "Hemi-methylated...": (
                "{hemi_methylated_gatcs} ({hemi_methylated_gatcs_wrt_meth} %)"
                ).format(**stats),
            "...only in '+' strand": (
                "{hemi_plus_methylated_gatcs} "
                "({hemi_plus_methylated_gatcs_wrt_meth} %)"
                ).format(**stats),
            "...only in '-' strand": (
                "{hemi_minus_methylated_gatcs} "
                "({hemi_minus_methylated_gatcs_wrt_meth} %)"
                ).format(**stats),
        }

        self.expected_summary = {
            "title": "sm-analysis · summary report",
            overview_head: overview_dict,
            results_head: results_dict,
            bam_file_head: bam_dict,
            reference_file_head: reference_dict,
            mols_subs_head: molecules_subreads_dict,
            seq_coverage_head: seq_coverage_dict,
            GATCs_head: GATCs_dict,
            methylations_head: methylations_dict,
            "images": [
                {"src": "{molecule_type_bars}".format(**SM_ANALYSIS_IMAGES),
                     "alt": "count of molecule types"
                 },
                {"src": "{molecule_len_histogram}".format(
                    **SM_ANALYSIS_IMAGES),
                    "alt": "molecule length histogram"
                 },
                {"src": "{position_coverage_bars}".format(
                    **SM_ANALYSIS_IMAGES),
                    "alt": (
                        "Position coverage in BAM file and in Methylation "
                        "report")
                 },
                {"src": "{position_coverage_history}".format(
                    **SM_ANALYSIS_IMAGES),
                    "alt": "Sequencing position coverage history"
                 },
                {"src": "{gatc_coverage_bars}".format(**SM_ANALYSIS_IMAGES),
                    "alt": "GATC coverage"},
                {"src": "{meth_type_bars}".format(**SM_ANALYSIS_IMAGES),
                    "alt": "count of methylation types"},
            ]
        }

    def check_summary_report_created(self):
        with open(self.found_summary_report) as summary_report_f:
            report_text = summary_report_f.read()
        parser = SummaryReportParser()
        parser.feed(report_text)

        self.check_and_update_date_in_summary_report(parser.parsed_data)

        # For debugging the next splitting makes things easier:
        for key, value in self.expected_summary.items():
            assert parser.parsed_data[key] == value
        # ...if the previous part is enabled, the next is redundant:
        assert parser.parsed_data == self.expected_summary

        # Finally he checks that the report includes some images:
        # (yes, this is quite smocky: only testing that a file exists and it
        # is an image by inspecting the header)
        assert len(parser.images) == len(self.expected_summary["images"])
        for image in parser.images:
            assert image in self.expected_summary["images"]
            image_path = Path(image["src"])
            assert image_path.is_file()
            ext = image_path.suffix.strip(".")
            assert ext == imghdr.what(image_path)

    def check_and_update_date_in_summary_report(self, current_data):
        key = (
            "Summary report: Single Molecule Methylation Analysis >> Overview"
        )
        expected_datetime_iso = self.expected_summary[key]["Date"]
        current_datetime_iso = current_data[key]["Date"]
        expected_datetime = datetime.fromisoformat(expected_datetime_iso)
        current_datetime = datetime.fromisoformat(current_datetime_iso)
        assert abs(expected_datetime-current_datetime) < timedelta(seconds=300)
        # Once we are sure that, within a safety margin, the dates agree,
        # the expected date is updated with the current, to simplify
        # comparisons later on...
        self.expected_summary[key]["Date"] = current_datetime_iso

    def check_unique_id_in_log_messages(self, raw_lines: list[str]) -> None:
        """Ensures that all log message contains a unique ID."""
        ids = set()
        for line in raw_lines:
            line = line.strip()
            if line.startswith("["):
                start_id = line.find("[", 1)+1
                end_id = line.find("]", start_id)
                ids.add(line[start_id:end_id])
        assert len(ids) <= 1
        if (unique_id := ids.pop()):
            assert set(unique_id) <= set("0123456789abcdef")

    def remove_marker_files(self):
        """Marker files are files generated by each process launched
        by fake tools as a cheap mean to signal that there was a process
        running. Since some FTs cound the number of marker files to
        determine if the behavior was correct, they must be cleaned up
        before running checks.
        This method removes the marker files generated by external tools.
        """
        cwd = Path(".")
        for tool in ("ccs", "ipdSummary", "blasr"):
            for markerfile in cwd.glob(f".{tool}.pid.*"):
                markerfile.unlink(missing_ok=True)

    def check_sm_analysis_with_bam_and_expected_results(self, *options):
        """This function accepts an arbitrary number of options to recycle it
        for verbose/quiet runs.
        """
        self.remove_marker_files()
        options = self.clos+options
        bam = self.bam
        cmd = (bam, self.fasta)+options

        expected_blasr_calls = 4
        if self.blasr_ccs.exists():
            expected_blasr_calls -= 1
        if self.pi_shifted_blasr_ccs.exists():
            expected_blasr_calls -= 1

        need_to_do_blasr_ccs = not self.blasr_ccs.exists()

        if "-v" in options or "--verbose" in options:
            verbose = True
        else:
            verbose = False
        self.make_expected_summary_report(options)
        with run_sm_analysis(*cmd) as cmd_result:
            raw_output_lines = (
                cmd_result[0].stdout.decode().split("\n")
                + cmd_result[0].stderr.decode().split("\n")
            )
            self.check_unique_id_in_log_messages(raw_output_lines)
            clean_stdout = normalize_whitespaces(cmd_result[0].stdout.decode())
            clean_stderr = normalize_whitespaces(cmd_result[0].stderr.decode())
            output = clean_stdout+clean_stderr
            # and he finds no critical errors:
            actual_msg = f"Actual output:\n{output}"
            for error_indicator in ("critical",):
                assert error_indicator not in output.lower(), actual_msg
            assert len(clean_stdout) == 0
            # and the return code of the program is 0, which reassures him:
            cmd_result[0].check_returncode()
        # he inspects more carefully the output:
        assert f"Starting 'sm-analysis' (version {VERSION}) with:" in output
        assert f"Input BAM file: '{bam}'" in output
        assert f"Reference file: '{self.fasta}'" in output

        self.check_ipdsummary_program_and_processes(
            options, output, cmd_result)

        if "--keep-temp-dir" in options:
            self.check_temp_files(
                output, self.one_mol_bams, self.rejected_molecules, options)

        self.check_modification_types(output, options)

        if self.unaligned_input:
            assert "The input BAM is NOT aligned" in output
            if self.aligned_bam:
                assert (
                    "...but a possible aligned version of the input BAM was "
                    f"found: 'blasr.{bam}'. It will be used.") in output
                expected_blasr_calls -= 1
            else:
                assert (
                    "...since no aligned version of the input BAM was found, "
                    f"one has been produced and it will be used: 'blasr.{bam}'"
                ) in output
            if self.pi_shifted_aligned_bam:
                assert (
                    "...but a possible pi-shifted aligned version of the input"
                    f" BAM was found: 'pi-shifted.blasr.{bam}'. It will be "
                    "used."
                ) in output
                expected_blasr_calls -= 1
            else:
                assert (
                    "...since no pi-shifted aligned version of the input BAM "
                    "was found, one has been produced and it will be used: "
                    f"'pi-shifted.blasr.{bam}'"
                ) in output
        else:
            expected_blasr_calls -= 2
            assert "The input BAM is aligned" in output
            if self.pi_shifted_aligned_bam:
                assert (
                    f"...a possible pi-shifted aligned version of the "
                    f"input BAM was found: '{self.pi_shifted_aligned_bam}'. It"
                    " will be used."
                ) in output
            else:
                assert (
                    "...but no pi-shifted aligned version of the input BAM "
                    "was found"
                ) in output
                assert (
                    "...therefore the pi-shifted analysis is disabled"
                ) in output
                expected_blasr_calls //= 2
        # Just to be sure that ugly warning messages from Pysam are not there:
        assert (
            "[E::idx_find_and_load] Could not retrieve index "
            "file for"
        ) not in output

        if "--only-produce-methylation-report" not in options:
            assert ("[filter] Sieving molecules from input BAM "
                    "before the IPD analysis") in output
            if verbose:
                for rejected_molecule in self.rejected_molecules:
                    assert (f"[filter] Molecule '{rejected_molecule}' rejected"
                            ) in output

        missing_aligned_ccs_msg = (
            "The methylation analysis requires aligned CCS files --for all "
            "variants-- to proceed. Trying to get them..."
        )
        missing_ccs_msg = MISSING_CCS_MSG
        ccs_generated_msg = f"[ccs] File 'ccs.{bam}' generated"
        aligned_ccs_generated_msg = (
            f"[blasr] Aligned file 'blasr.ccs.{bam}' generated"
        )

        generate_mol_mapping_msgs = [
            "Generating molecules mapping from aligned CCS file"
        ]
        # The first case is obvious; the second happens when the input is
        # aligned but there is a pi-shifted aligned file present:
        if self.unaligned_input or (self.pi_shifted_aligned_bam is not None):
            generate_mol_mapping_msgs.append(
                "Generating molecules mapping from pi-shifted aligned CCS file"
            )
        meth_report_produced_msg = (
            "[methylation report] Results saved to file "
            f"'{self.found_meth_report}'"
        )
        meth_msgs = [
            missing_aligned_ccs_msg,
            missing_ccs_msg,
            ccs_generated_msg,
        ] + generate_mol_mapping_msgs

        if need_to_do_blasr_ccs:
            meth_msgs.append(aligned_ccs_generated_msg)

        check_blasr = True
        check_ccs = True
        # need to review next blocks:
        for arg in ("-c", "--CCS-bam-file"):
            if arg in options:
                ccs_bam_file = options[options.index(arg)+1]
                meth_msgs = [
                    missing_aligned_ccs_msg,
                    aligned_ccs_generated_msg
                ] + generate_mol_mapping_msgs
                check_ccs = False
                assert f"CCS bam file: '{ccs_bam_file}'" in output
                break
        for arg in ("-C", "--aligned-CCS-bam-file"):
            if arg in options:
                aligned_ccs_bam_file = options[options.index(arg)+1]
                meth_msgs = generate_mol_mapping_msgs
                check_blasr = False
                check_ccs = False
                assert (
                    f"aligned CCS bam file: '{aligned_ccs_bam_file}'" in output
                )
                break
        if verbose:
            meth_msgs.append(
                f"ccs lines (aligned): {self.num_ccs_mols} molecules found"
            )
        for imperfect_mol in self.imperfect_molecules:
            meth_msgs.append(
                f"Molecule {imperfect_mol} discarded "
                f"due to DNA sequence mismatch with reference"
            )
        # (I add here the last methylation report-related message after all the
        # others):
        meth_msgs.append(meth_report_produced_msg)

        for msg in meth_msgs:
            assert msg in output

        # The molecules having a perfect mapping should not be reported as
        # "discarded due to sequence mismatch":
        for mol in self.all_molecules:
            if mol not in self.imperfect_molecules:
                assert (
                    f"Molecule {mol} discarded "
                    "due to DNA sequence mismatch with reference"
                ) not in output

        aligner = "blasr"
        for arg in ("-b", "--blasr-path"):
            if arg in options:
                aligner = options[options.index(arg)+1]
                break
        assert f"aligner: '{aligner}'" in output

        nprocs_blasr = 1
        if "--nprocs-blasr" in options:
            nprocs_blasr = int(options[options.index("--nprocs-blasr")+1])
        assert f"# workers blasr: {nprocs_blasr}" in output
        if check_blasr:
            total_blasr_procs = expected_blasr_calls*nprocs_blasr
            assert total_blasr_procs == count_marker_files("blasr")
            # assert 2*nprocs_blasr == count_marker_files("blasr")
            # assert nprocs_blasr == cmd_result[1]["nprocs_blasr"]

        if check_ccs:
            # this is artificial. The real ccs uses more than one proc
            assert 1 == count_marker_files("ccs")
            # assert 1 == cmd_result[1]["nprocs_ccs"]

        indexer = "pbindex"
        for arg in ("-p", "--pbindex-path"):
            if arg in options:
                indexer = options[options.index(arg)+1]
                break
        assert f"indexer: '{indexer}'" in output

        for faulty_mol, tool_info in self.faulty_molecules.items():
            tool = tool_info["tool"]
            tool_error = tool_info["error"]
            assert (
                f"[{tool}] Molecule {faulty_mol} could not be processed"
                in output
            )
            if verbose:
                assert f"[{tool}] The reported error was:" in output
                assert f"[{tool}]     '{tool_error}'" in output

        for arg in ("-M", "--ipd-model"):
            if arg in options:
                model = options[options.index(arg)+1]
                assert re.search(f"ipd model:.*{model}.*", output)
                break

        if "--only-produce-methylation-report" in options:
            assert "only produce methylation report: yes" in output

        assert re.search(
            r"Execution time [(]wall clock time[)]: \d+[.]\d* s = \d+[.]\d* h",
            output
        )

        self.check_one_molecule_bam_files_produced(output, options)

        # he sees that three new files have been created:
        # First, a joint gff file:
        if self.expected_gff:
            self.check_for_gff()
        # Also a summary per methylation found, in csv format:
        if self.expected_csv:
            self.check_for_csv(output)
        # and a summary of methylations per molecule is also produced,
        # in csv format too:
        assert self.found_meth_report.exists()
        with open(self.found_meth_report) as meth_report_f:
            with open(self.expected_meth_report) as expected_meth_report_f:
                assert expected_meth_report_f.read() == meth_report_f.read()
        # Last, but not least, a summary report in HTML format has been
        # created:
        self.check_summary_report_created()


class TestCaseSmAnalysis:
    expected_help_lines = [
        "Single Molecule Analysis",
        "-h, --help show this help message and exit",
        "-v, --verbose",
        "--version show program's version number and exit",
        "-M MODEL, --ipd-model MODEL",
        (
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
            "ipdSummary is used."
        ),
        "-b PATH, --blasr-path PATH path to blasr program (default: 'blasr')",
        (
            "-p PATH, --pbindex-path PATH path to pbindex program (default: "
            "'pbindex')"
        ),
        (
            "-i PATH, --ipdsummary-path PATH path to ipdSummary program "
            "(default: 'ipdSummary')"
        ),
        (
            "-N NUM, --num-simultaneous-ipdsummarys NUM number of simultaneous"
            " instances of ipdSummary that will cooperate to process the "
            "molecules (default: 1)"
        ),
        (
            "-n NUM, --num-workers-per-ipdsummary NUM number of worker proce"
            "sses that each instance of ipdSummary will spawn (default: 1)"
        ),
        (
            "--nprocs-blasr NUM number of worker processes "
            "that each instance of blasr will spawn (default: 1)"
        ),
        (
            "-P PARTITION:NUMBER-OF-PARTITIONS, --partition PARTITION:NUMBER-"
            "OF-PARTITIONS "
            "this option instructs the program to only analyze a fraction "
            "(partition) of the molecules present in the input bam file. The "
            "file is divided in `NUMBER OF PARTITIONS` (almost) equal pieces "
            "but ONLY the PARTITION-th partition (fraction) is analyzed. For "
            "instance, `--partition 3:7` means that the bam file is divided in"
            " seven pieces but only the third piece is analyzed (by default "
            "all the file is analyzed)"
        ),
        (
            "-C BAM-FILE, --aligned-CCS-bam-file BAM-FILE "
            "aligned CCS file in BAM format used to produce a report of "
            "methylation states. If provided, it is used in the production of "
            "the methylation states report. If missing, "
            "one is generated from the CCS file using 'blasr'"
        ),
        (
            "-c BAM-FILE, --CCS-bam-file BAM-FILE "
            "CCS file in BAM format used to produce a report of methylation "
            "states. If provided, and the aligned version of it is not "
            "provided, it is aligned and the result is used in the production "
            "of the methylation states report. If missing, one is generated "
            "from the original BAM file using the 'ccs' program"
        ),
        (
            "--keep-temp-dir should we make a copy of the temporary files "
            "generated? (default: False)"
        ),
        (
            "-m MOD-TYPE [MOD-TYPE ...], --modification-types MOD-TYPE "
            "[MOD-TYPE ...] focus only in the requested modification types "
            "(default: ['m6A'])"
        ),
        (
            "--only-produce-methylation-report "
            "use this flag to only produce the methylation report from the "
            "per detection csv file"
        ),
    ]

    def test_message_and_return_code_with_no_argument(self):
        #  Nathan is a new PhD student in the Biology department. He is working
        # in the analysis of DNA sequences.
        #  He needs to analyze the data coming from the expensive sequencer,
        # but has no idea about how to do it. Someone tells him about a
        # software called "PacbioDataProcessing". The name is promising. He
        # installs it and wants to try it.
        #  Reading the docs he learns that the package comes with a program
        # called 'sm-analysis' that seems to do what he looks after.
        #  First off he wants to test the program. How does it work? Why not
        # just run it?
        with run_sm_analysis() as plain_res:
            # he does so and he sees some clarifying error message:
            expected = [_.format(exe=SM_ANALYSIS_EXE) for _ in (
                "usage: {exe} [-h]",
                "[-v] [--version]",
                "{exe}: error: the following arguments are required:",
            )]
            for e in expected:
                assert e in normalize_whitespaces(plain_res[0].stderr.decode())
            # and it returns an error code to the terminal:
            assert plain_res[0].returncode != 0

    def test_help_run(self):
        # Ok, ok, he got it; he needs to call it with -h:
        with run_sm_analysis("-h") as help_res:
            # and, he gets a very informative message about its usage. Great!
            help_res_normalized = normalize_whitespaces(
                help_res[0].stdout.decode())
            for line in self.expected_help_lines:
                assert line in help_res_normalized
            # BTW, the returned code is not an error anymore:
            help_res[0].check_returncode()

    def test_version_option(self):
        # Nathan is curious about the version of the program he's using.
        with run_sm_analysis("--version") as version_res:
            version = version_res[0].stdout.decode().split(".")
            for i in version:
                int(i)


class TestCaseHappyPathSmAnalysis(SmAnalysisMixIn):
    def test_straight_run_with_only_bam_and_fai_files(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # Nathan finds the killing program provided by the package:
        #  sm-analysis
        # It does exactly what he needs: single molecule analysis of
        # methylation states.
        # He learned that it must be run providing a bam file and a fasta file
        # afterwards, so he does:
        self.collect_opts_for_tests(sm_test_data)
        aligned_bams_to_rm = (self.aligned_bam, self.pi_shifted_aligned_bam)
        ccs_bam = self.bam.with_name("ccs."+self.bam.name)
        if "aligned present" in sm_test_data["features"]:
            aligned_bams_to_rm = ()
        elif "unaligned input" in sm_test_data["features"]:
            aligned_bams_to_rm = (
                self.bam.with_name("blasr."+self.bam.name),
                self.bam.with_name("pi-shifted.blasr."+self.bam.name)
            )
            self.aligned_bam = None
            self.pi_shifted_aligned_bam = None

        if len(self.clos) == 0:  # want to run without options in this FT
            if sm_test_data["name"] == (
                    "unaligned input with one mol crossing ori"):
                # In this case, the fixture provides some files that
                # must be deleted in the straight case:
                clean_run_results(*aligned_bams_to_rm)
            self.check_sm_analysis_with_bam_and_expected_results()
            ccs_files_to_remove = ccs_bam.parent.glob("*"+ccs_bam.stem+"*")
            clean_run_results(
                *aligned_bams_to_rm, *ccs_files_to_remove,
                self.found_gff, self.found_csv, self.found_meth_report
            )
            self.check_sm_analysis_with_bam_and_expected_results("--verbose")

    def test_different_combinations_of_aligned_files_unexpectedly_present(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # Nathan runs the 'sm-analysis' program in a directory where he
        # previously ran it, with some files remaining...
        self.collect_opts_for_tests(sm_test_data)
        if sm_test_data["name"] == "unaligned input with one mol crossing ori":
            aligned_bam = self.aligned_bam
            pi_shifted_aligned_bam = self.pi_shifted_aligned_bam

            # 1) ∃ aligned and ∃ pi-shifted
            self.check_sm_analysis_with_bam_and_expected_results()
            clean_run_results(
                self.found_gff, self.found_csv, self.found_meth_report,
                self.ccs, self.blasr_ccs
            )
            self.check_sm_analysis_with_bam_and_expected_results("--verbose")
            clean_run_results(
                self.found_gff, self.found_csv, self.found_meth_report,
                self.ccs, self.blasr_ccs
            )
            # 2) ∃ aligned and ∄ pi-shifted
            self.pi_shifted_aligned_bam = None
            with temporarily_rename_file(pi_shifted_aligned_bam):
                self.check_sm_analysis_with_bam_and_expected_results()
                clean_run_results(
                    pi_shifted_aligned_bam, self.ccs, self.blasr_ccs,
                    self.found_gff, self.found_csv, self.found_meth_report
                )
                self.check_sm_analysis_with_bam_and_expected_results(
                    "--verbose")
                clean_run_results(
                    self.found_gff, self.found_csv, self.found_meth_report,
                    self.ccs, self.blasr_ccs
                )
            self.pi_shifted_aligned_bam = pi_shifted_aligned_bam
            # 3) ∄ aligned and ∃ pi-shifted
            self.aligned_bam = None
            with temporarily_rename_file(aligned_bam):
                self.check_sm_analysis_with_bam_and_expected_results()
                clean_run_results(
                    aligned_bam,
                    self.found_gff, self.found_csv, self.found_meth_report,
                    self.ccs, self.blasr_ccs
                )
                self.check_sm_analysis_with_bam_and_expected_results(
                    "--verbose")
                clean_run_results(
                    self.found_gff, self.found_csv, self.found_meth_report
                )
            self.aligned_bam = aligned_bam
        elif sm_test_data["name"] == "no clos":
            pi_shifted_aligned_bam = self.pi_shifted_aligned_bam
            # 5) input aligned and ∄ pi-shifted
            clean_run_results(pi_shifted_aligned_bam)
            self.check_sm_analysis_with_bam_and_expected_results()
            clean_run_results(
                pi_shifted_aligned_bam, self.ccs, self.blasr_ccs,
                self.found_gff, self.found_csv, self.found_meth_report
            )
            self.check_sm_analysis_with_bam_and_expected_results("--verbose")

    def test_ipd_model(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # One thing that Nathan is interested to test has to do with some
        # exotic data he has that he wants to analyze with a special ipd
        # model. Therefore, he wants to run sm-analysis with -M. He tries
        # it out:
        self.collect_opts_for_tests(sm_test_data)
        if ("-M" in self.clos) or ("--ipd-model" in self.clos):
            self.check_sm_analysis_with_bam_and_expected_results()
            clean_run_results(
                self.found_gff, self.found_csv, self.found_meth_report,
                self.ccs, self.blasr_ccs
            )
            self.check_sm_analysis_with_bam_and_expected_results("--verbose")

    def _test_run_including_preprocessing_to_align_input(self):
        ...

    def test_choose_aligner(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr_no_path):
        self.collect_opts_for_tests(sm_test_data)
        # Now, Nathan does not have the aligner in the path. What happens if
        # he runs the analysis like this?
        if sm_test_data["name"] == "no clos":
            try:
                self.check_sm_analysis_with_bam_and_expected_results()
            except AssertionError as e:
                assert "CRITICAL" in str(e)
                assert "No such file or directory: 'blasr'" in str(e)
            clean_run_results(
                self.found_gff, self.found_csv, self.found_meth_report,
                self.ccs,
            )
            # he needs to provide the path to an executable that he wants to
            # use as aligner. He launches the analysis with such an argument:
            self.check_sm_analysis_with_bam_and_expected_results(
                "-b", "bin.no.path/blasr"
            )

    def test_choose_indexer(
            self, sm_test_data, install_pbindex_no_path, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_test_data)
        # Now, Nathan does not have the indexer in the path. What happens if
        # he runs the analysis like this?
        if sm_test_data["name"] == "no clos":
            try:
                self.check_sm_analysis_with_bam_and_expected_results()
            except AssertionError as e:
                assert "CRITICAL" in str(e)
                assert "no such file or directory: 'pbindex'" in str(e)
            else:
                self.fail("The expected error did not occur!")
            clean_run_results(self.ccs, self.blasr_ccs)
            # he needs to provide the path to an executable that he wants to
            # use as indexer. He launches the analysis with such an argument:
            self.check_sm_analysis_with_bam_and_expected_results(
                "-p", "bin.no.path/pbindex"
            )

    def test_without_ipd_analysis_program(
            self, sm_test_data, install_pbindex, temporarily_unplug_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_test_data)
        # Now, Nathan does not have the ipd analysis program in the path.
        # What happens if he runs the analysis like this?
        if sm_test_data["name"] == "no clos":
            try:
                self.check_sm_analysis_with_bam_and_expected_results()
            except AssertionError as e:
                assert "CRITICAL" in str(e)
                assert "No such file or directory: 'ipdSummary'" in str(e)

    def test_choose_ipd_analysis_program(
            self, sm_test_data, install_pbindex, install_ipdSummary_no_path,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_test_data)
        # Now, Nathan does provide the path to the ipd analysis program.
        # He launches the analysis with such an argument:
        if sm_test_data["name"] == "no clos":
            self.check_sm_analysis_with_bam_and_expected_results(
                "-i", "bin.no.path/ipdSummary"
            )

    def test_run_several_instances_of_ipd_analysis_program(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # Since the time needed to process large bam files is long, Nathan
        # wonders what happens if he uses the -N option:
        self.collect_opts_for_tests(sm_test_data)
        # hence, Nathan provides the number of simultaneous instances of the
        # ipd analysis program. He launches the analysis with such an argument:
        if sm_test_data["name"] == "no clos":
            self.check_sm_analysis_with_bam_and_expected_results("-N", "3")

    def test_run_with_num_workers_for_ipd_analysis(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # Another interesting option to explore is -n: it seems to allow
        # to run ipdSummary with several workers. It is worth exploring:
        self.collect_opts_for_tests(sm_test_data)
        # hence, Nathan provides the number of simultaneous instances of the
        # ipd analysis program. He launches the analysis with such an argument:
        if sm_test_data["name"] == "no clos":
            self.check_sm_analysis_with_bam_and_expected_results("-n", "5")

    def test_run_with_num_workers_for_alignment(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # Yet another interesting option to explore is --nprocs-blasr:
        # it seems to further speed up the process by launching the aligner
        # with more than 1 worker. He gives it a try:
        self.collect_opts_for_tests(sm_test_data)
        # hence, Nathan provides the number of simultaneous instances of the
        # ipd analysis program. He launches the analysis with such an argument:
        if sm_test_data["name"] == "no clos":
            self.check_sm_analysis_with_bam_and_expected_results(
                "--nprocs-blasr", "3"
            )

    def _test_restart_run(self):
        ...

    def test_choose_modification_types(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # What if he is interested in different type of modifications?
        # The -m option of sm-analysis seems to be the answer. He tries it:
        self.collect_opts_for_tests(sm_test_data)
        # hence, Nathan provides the number of simultaneous instances of the
        # ipd analysis program. He launches the analysis with such an argument:
        if sm_test_data["name"] == "two modification types":
            self.check_sm_analysis_with_bam_and_expected_results(
                "-m", "m6A", "m4C")

    def test_run_with_partition(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # Nathan has troubles with the speed of the analysis. Since he has
        # to analze large files with many molecules, and since most of the
        # analysis for each molecule is independent of the other molecules,
        # he would like to divide the file in pieces each processed
        # independently.
        # The sm-analysis program has an option for that (-P/--partition);
        # hence he chooses a test BAM file to try it.
        self.collect_opts_for_tests(sm_test_data)
        # He goes to a newly created directory, copies the file there,
        # and he runs the program on it:
        if sm_test_data["name"] == "partition2of3":
            self.check_sm_analysis_with_bam_and_expected_results()
            clean_run_results(
                self.found_gff, self.found_csv, self.found_meth_report,
                self.ccs, self.blasr_ccs
            )
            self.check_sm_analysis_with_bam_and_expected_results("--verbose")

    def test_run_with_aligned_CCS_bam_file(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs):
        self.collect_opts_for_tests(sm_test_data)
        # Since the production of the CCS file takes some time, Nathan
        # would like to recycle its aligned version. Would it work if
        # he simply copies the file?
        if sm_test_data["name"] == "no clos":
            # he copies the aligned CCS file the he wants to use to
            # the current working dir:
            shutil.copy(DATA_DIR/self.blasr_ccs.name, ".")
            self.check_sm_analysis_with_bam_and_expected_results()
            clean_run_results(
                self.found_gff, self.found_csv, self.found_meth_report,
                self.ccs
            )
            self.check_sm_analysis_with_bam_and_expected_results("--verbose")

    def test_run_with_CCS_bam_file_without_aligned_one(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_blasr):
        self.collect_opts_for_tests(sm_test_data)
        # Since the production of the CCS file takes some time, Nathan wants to
        # recycle it. But he didn't run it through 'blasr', thankfully he finds
        # the option to provide a raw --not aligned-- ccs file: -c
        # Here he goes:
        if sm_test_data["name"] == "no clos":
            # he copies the aligned CCS file the he wants to use to
            # the current working dir:
            shutil.copy(DATA_DIR/self.ccs.name, ".")
            clos = ("-c", f"{self.ccs.name}")
            self.check_sm_analysis_with_bam_and_expected_results(*clos)
            clean_run_results(
                self.found_gff, self.found_csv, self.found_meth_report,
                self.blasr_ccs
            )
            self.check_sm_analysis_with_bam_and_expected_results(
                *clos, "--verbose")

    def test_keeping_the_temporary_directory(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_test_data)
        # One thing Nathan is wishing to do is inspecting the one-molecule
        # intermediate files produced in the analysis. He finds an option
        # for that: --keep-temp-dir
        if sm_test_data["name"] == "no clos":
            self.check_sm_analysis_with_bam_and_expected_results(
                "--keep-temp-dir"
            )
            clean_run_results(
                self.found_gff, self.found_csv, self.found_meth_report,
                self.ccs, self.blasr_ccs
            )
            self.check_sm_analysis_with_bam_and_expected_results(
                "--keep-temp-dir", "--verbose"
            )

    def test_can_produce_just_methylation_reports(
            self, sm_test_data, install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_test_data)
        # Nathan has satisfactorily run sm-analysis to produce some data
        # and wants to re-produce the methylation report. Thankfully there
        # is an option for that. He runs the code with that option to see if
        # it works well:
        if sm_test_data["name"] == "no clos":
            gff = sm_test_data["gff"]
            shutil.copy2(gff, gff.with_name(gff.name[9:]))
            csv = sm_test_data["csv"]
            shutil.copy2(csv, csv.with_name(csv.name[9:]))
            self.expected_gff = None
            self.expected_csv = None
            self.check_sm_analysis_with_bam_and_expected_results(
                "--only-produce-methylation-report"
            )
            clean_run_results(self.found_meth_report, self.ccs, self.blasr_ccs)
            self.check_sm_analysis_with_bam_and_expected_results(
                "--only-produce-methylation-report", "--verbose"
            )


class TestCaseErrors(SmAnalysisMixIn):
    def test_wrong_type_of_files_passed_as_input(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # Nathan passes by accident the wrong files to sm-analysis:
        bam = sm_test_data["bam"]
        fasta = sm_test_data["fasta"]
        cmd = (fasta, bam)
        with run_sm_analysis(*cmd) as cmd_result:
            clean_stdout = normalize_whitespaces(cmd_result[0].stdout.decode())
            clean_stderr = normalize_whitespaces(cmd_result[0].stderr.decode())
            output = clean_stdout+clean_stderr
            # and he finds a critical error:
            assert "critical" in output.lower(), f"Actual output:\n{output}"
            assert len(clean_stdout) == 0
            # and the return code of the program is not 0, which is a clear
            # sign that there was a problem:
            assert cmd_result[0].returncode != 0

    def test_wrong_model_name_passed_as_input(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        # Nathan makes a typo passing the name of the model:
        clos = sm_test_data["CLOs"]
        for arg in ("-M", "--ipd-model"):
            if arg in clos:
                model_idx = clos.index(arg)+1
                clos = list(clos)
                fake_model_path = "/tmp/icannotexist_nunca"
                while Path(fake_model_path).is_file():
                    fake_model_path += "."
                clos[model_idx] = fake_model_path
                bam = sm_test_data["bam"]
                fasta = sm_test_data["fasta"]
                cmd = (bam, fasta)+tuple(clos)
                with run_sm_analysis(*cmd) as cmd_result:
                    # clean_stdout = normalize_whitespaces(
                    #     cmd_result[0].stdout.decode())
                    clean_stderr = normalize_whitespaces(
                        cmd_result[0].stderr.decode())
                    assert (f"Model '{fake_model_path}' not found. "
                            "Using default model") in clean_stderr
                break

    def check_error_msgs_in_ccs(
            self, bam, fasta, *,
            check_critical=False,
            check_could_not=False,
            check_stderr=False,
            check_suspucious=False,
            check_stderr_empty=False
    ):
        ccs_bam_file = bam.with_name("ccs."+bam.name)
        cmd = (bam, fasta)
        with run_sm_analysis(*cmd) as cmd_result:
            clean_stdout = normalize_whitespaces(
                cmd_result[0].stdout.decode())
            clean_stderr = normalize_whitespaces(
                cmd_result[0].stderr.decode())
            output = clean_stdout+clean_stderr
        # and he finds a critical error:
        if check_critical:
            assert "critical" in output.lower(), f"Actual output:\n{output}"
        if check_could_not:
            assert (
                f"[CRITICAL] CCS BAM file '{ccs_bam_file}' could not "
                "be produced."
            ) in output
        if check_suspucious:
            assert (
                f"Although the file '{ccs_bam_file}' has been generated,"
                " there was an error.") in output
            assert (
                "It is advisable to check the correctness of the "
                "generated ccs file."
            ) in output
            assert (
                "[ccs] The following command was issued:"
            ) in output
            assert f"'ccs {bam} {ccs_bam_file}'" in output
        if check_stderr:
            assert (
                "[ccs] ...the error message was: 'libchufa.so not found'"
            ) in output
        elif check_stderr_empty:
            assert (
                "[ccs] ...but the program did not report any error message."
            ) in output
        if check_could_not:
            # and the return code of the program is not 0, which is a clear
            # sign that there was a problem:
            assert cmd_result[0].returncode != 0
            # and indeed the file was not produced
            assert not ccs_bam_file.exists()
        else:
            # and the return code of the program is 0:
            assert cmd_result[0].returncode == 0
            # and indeed the file was produced
            assert ccs_bam_file.exists()

    def test_ccs_does_not_produce_its_output_and_gives_error(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs_without_result_with_error, install_blasr):
        # Nathan ran 'sm-analysis' but the ccs program did not
        # create a ccs file. He's pleased to see that the
        # program displays an informative message and stops:
        if sm_test_data["name"] == "no clos":
            bam = sm_test_data["bam"]
            fasta = sm_test_data["fasta"]
            self.check_error_msgs_in_ccs(
                bam, fasta,
                check_critical=True,
                check_could_not=True
            )

    def test_ccs_does_produce_its_output_but_gives_error(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs_with_error, install_blasr):
        # Nathan ran 'sm-analysis' with a new ccs program. This time a
        # ccs file has been created, but the process returned an error.
        # Once more, he's pleased to see that the
        # program displays an informative message:
        if sm_test_data["name"] == "no clos":
            bam = sm_test_data["bam"]
            fasta = sm_test_data["fasta"]
            self.check_error_msgs_in_ccs(
                bam, fasta,
                check_suspucious=True,
                check_stderr=True
            )

    def test_ccs_does_produce_its_output_but_gives_empty_error(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs_with_empty_error, install_blasr):
        # Nathan ran 'sm-analysis' with a new ccs program. This time a
        # ccs file has been created, but the process returned an error.
        # Once more, he's pleased to see that the
        # program displays an informative message:
        if sm_test_data["name"] == "no clos":
            bam = sm_test_data["bam"]
            fasta = sm_test_data["fasta"]
            self.check_error_msgs_in_ccs(
                bam, fasta,
                check_suspucious=True,
                check_stderr_empty=True
            )

    def test_ccs_does_not_produce_its_output_but_gives_no_error(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs_without_result, install_blasr):
        # Nathan ran 'sm-analysis' yet with another faulty ccs program.
        # This time it did not create a ccs file, although there was no
        # error. He's pleased to see that the program displays an
        # informative message and stops:
        if sm_test_data["name"] == "no clos":
            bam = sm_test_data["bam"]
            fasta = sm_test_data["fasta"]
            self.check_error_msgs_in_ccs(
                bam, fasta,
                check_critical=True,
                check_could_not=True,
            )

    def test_pbindex_fails(
            self, sm_faulty_mol_test_data, install_pbindex_1mol_fails,
            install_ipdSummary, install_ccs, install_blasr):
        # Nathan tries the tool again, but for some reason he
        # sees that a molecule is missing in the results, and
        # inspecting the logs, he realizes that pbindex could not
        # produce the required file:
        self.collect_opts_for_tests(sm_faulty_mol_test_data)
        for tool_info in self.faulty_molecules.values():
            tool_info["tool"] = "pbindex"
            tool_info["error"] = "who knows what happens here"
        self.check_sm_analysis_with_bam_and_expected_results()
        self.bam.with_name(
            "blasr."+self.bam.name).unlink(missing_ok=True)
        self.bam.with_name(
            "pi-shifted.blasr."+self.bam.name).unlink(missing_ok=True)
        self.bam.with_name(
            "ccs."+self.bam.name).unlink(missing_ok=True)
        self.bam.with_name(
            "blasr.ccs."+self.bam.name).unlink(missing_ok=True)
        self.bam.with_name(
            "pi-shifted.blasr.ccs."+self.bam.name).unlink(missing_ok=True)
        clean_run_results(
            self.found_gff, self.found_csv, self.found_meth_report,
        )
        self.check_sm_analysis_with_bam_and_expected_results("--verbose")

    def test_ipdSummary_fails(
            self, sm_faulty_mol_test_data, install_pbindex,
            install_ipdSummary_1mol_fails, install_ccs, install_blasr):
        # Nathan tries the tool again, but for some reason he
        # sees that a molecule is missing in the results, and
        # inspecting the logs, he realizes that ipdSummary could not
        # produce the required file:
        self.collect_opts_for_tests(sm_faulty_mol_test_data)
        for tool_info in self.faulty_molecules.values():
            tool_info["tool"] = "ipdSummary"
            tool_info["error"] = "whatever I feel like I wanna do"
        self.check_sm_analysis_with_bam_and_expected_results()
        self.bam.with_name(
            "blasr."+self.bam.name).unlink(missing_ok=True)
        self.bam.with_name(
            "pi-shifted.blasr."+self.bam.name).unlink(missing_ok=True)
        self.bam.with_name(
            "ccs."+self.bam.name).unlink(missing_ok=True)
        self.bam.with_name(
            "blasr.ccs."+self.bam.name).unlink(missing_ok=True)
        self.bam.with_name(
            "pi-shifted.blasr.ccs."+self.bam.name).unlink(missing_ok=True)
        clean_run_results(
            self.found_gff, self.found_csv, self.found_meth_report,
        )
        self.check_sm_analysis_with_bam_and_expected_results("--verbose")


class TestCaseProvidedCCS(SmAnalysisMixIn):
    def test_ccs_file_passed_in_cl_and_present(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        if sm_test_data["name"] == "unaligned input":
            self.collect_opts_for_tests(sm_test_data)
            # Nathan wants to inject the ccs file in the process,
            # so he calls directly the ccs tool:
            bam = self.bam
            ccs_name = "ccs."+bam.name
            ccs_path = bam.with_name(ccs_name)
            sp.run(["ccs", bam, ccs_path], stdout=sp.PIPE, stderr=sp.PIPE)
            self.remove_marker_files()
            # Nathan calls the sm-analysis program
            cmd = (bam, self.fasta, "-c", ccs_path)
            with run_sm_analysis(*cmd) as cmd_result:
                clean_stdout = normalize_whitespaces(
                    cmd_result[0].stdout.decode())
                clean_stderr = normalize_whitespaces(
                    cmd_result[0].stderr.decode())
                output = clean_stdout+clean_stderr
            # he checks that the program did not compute the ccs file
            assert MISSING_CCS_MSG not in output
            # assert 0 == cmd_result[1]["nprocs_ccs"]
            assert 0 == count_marker_files("ccs")

    def test_ccs_computed_only_once(
            self, sm_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        if sm_test_data["name"] == "unaligned input":
            self.collect_opts_for_tests(sm_test_data)
            # Nathan wants to inject the ccs file in the process,
            # so he calls directly the ccs tool:
            bam = self.bam
            # Nathan calls the sm-analysis program
            cmd = (bam, self.fasta)
            with run_sm_analysis(*cmd) as cmd_result:
                clean_stdout = normalize_whitespaces(
                    cmd_result[0].stdout.decode())
                clean_stderr = normalize_whitespaces(
                    cmd_result[0].stderr.decode())
                output = clean_stdout+clean_stderr
            # he checks that the program did compute the ccs file only ONCE:
            assert MISSING_CCS_MSG in output
            new_output = output.replace(MISSING_CCS_MSG, "XXX", 1)
            assert MISSING_CCS_MSG not in new_output
            # assert 1 == cmd_result[1]["nprocs_ccs"]
            assert 1 == count_marker_files("ccs")


class TestCaseBlasrWIP(SmAnalysisMixIn):
    def make_alignment_bam_and_wip_names(self, bam=None, variant=""):
        if bam is None:
            bam = self.bam
        prefix = "blasr."
        if variant != "":
            prefix = variant+"."+prefix
        blasr_bam = bam.with_name(prefix+bam.name)
        blasr_wip = blasr_bam.with_name("."+blasr_bam.name+".wip")
        return blasr_bam, blasr_wip

    def check_blasr_msgs(
            self,
            blasr_calls: list[tuple] = None,
            blasr_found: list[tuple] = None,
            blasr_not_found: list[tuple] = None
    ) -> tuple[sp.CompletedProcess, str]:
        """Items in ``blasr_calls`` are:
        (blasr_bam: Path, fasta: Path, blasr_wip: Path)

        Items in ``blasr_found`` and in  ``blasr_not_found`` are:
        (blasr_bam: Path, variant: str)

        where variant is expected to be one of these:

        * ``aligned``
        * ``pi-shifted aligned``
        """
        cmd = (self.bam, self.fasta)
        if blasr_calls is None:
            blasr_calls = []
        if blasr_found is None:
            blasr_found = []
        if blasr_not_found is None:
            blasr_not_found = []
        for (blasr_bam, fasta, blasr_wip) in blasr_calls:
            blasr_cmd = ["blasr", self.bam, fasta, "--bam", "--out", blasr_bam]
            self.executor.submit(lambda: remove_later(3, blasr_wip))
            self.executor.submit(lambda: run_later(2.8, blasr_cmd))
            # blasr_wip.unlink()
        with run_sm_analysis(*cmd) as cmd_result:
            clean_stdout = normalize_whitespaces(
                cmd_result[0].stdout.decode())
            clean_stderr = normalize_whitespaces(
                cmd_result[0].stderr.decode())
            output = clean_stdout+clean_stderr
        # He checks that sm-analysis did not computed the aligned bam files:
        assert "The input BAM is NOT aligned" in output
        for (blasr_bam, variant) in blasr_found:
            if "ccs" in str(blasr_bam):
                inbam = "ccs"
            else:
                inbam = "input"
            assert (
                f"...but a possible {variant} version of the {inbam} BAM was "
                f"found: '{blasr_bam}'. It will be used."
            ) in output
            assert (
                f"...since no {variant} version of the {inbam} BAM was found, "
                f"one has been produced and it will be used: '{blasr_bam}'"
            ) not in output
        for (blasr_bam, variant) in blasr_not_found:
            if "ccs" in str(blasr_bam):
                inbam = "ccs"
            else:
                inbam = "input"
            assert (
                f"...but a possible {variant} version of the {inbam} BAM"
                f" was found: '{blasr_bam}'. It will be used."
            ) not in output
            assert (
                f"...since no {variant} version of the {inbam} BAM "
                "was found, one has been produced and it will be used: "
                f"'{blasr_bam}'"
            ) in output
        return cmd_result, output

    def test_both_wip_files_present(
            self, sm_wip_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_wip_test_data)
        blasr_bam, blasr_wip = self.make_alignment_bam_and_wip_names()
        blasr_wip.touch()
        pi_shifted_blasr_bam, pi_shifted_blasr_wip = (
            self.make_alignment_bam_and_wip_names(variant="pi-shifted")
        )
        pi_shifted_blasr_wip.touch()
        # There is another simultaneous run of sm-analysis, but Nathan
        # tries to launch the program in parallel
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[
                (blasr_bam, self.fasta, blasr_wip),
                (pi_shifted_blasr_bam, self.pi_shifted_fasta,
                    pi_shifted_blasr_wip),
            ],
            blasr_found=[
                (blasr_bam, "aligned"),
                (pi_shifted_blasr_bam, "pi-shifted aligned"),
            ]
        )
        # assert 0 == cmd_result[1]["nprocs_blasr"]

    def test_one_wip_file_present(
            self, sm_wip_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_wip_test_data)
        # He runs again sm-analysis while another instance is processing
        # the same file:
        blasr_bam, blasr_wip = self.make_alignment_bam_and_wip_names()
        blasr_wip.touch()
        pi_shifted_blasr_bam, pi_shifted_blasr_wip = (
            self.make_alignment_bam_and_wip_names(variant="pi-shifted")
        )
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[(blasr_bam, self.fasta, blasr_wip)],
            blasr_found=[(blasr_bam, "aligned")],
            blasr_not_found=[(pi_shifted_blasr_bam, "pi-shifted aligned")]
        )
        # assert 1 == count_marker_files("blasr")

        blasr_bam.unlink()
        blasr_wip.touch()
        # He tries again, but now the file without wip is there:
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[(blasr_bam, self.fasta, blasr_wip)],
            blasr_found=[
                (pi_shifted_blasr_bam, "pi-shifted aligned"),
                (blasr_bam, "aligned"),
            ]
        )
        # assert 1 == count_marker_files("blasr")

        # And the same happens the other way around: blasr <-> pi-shifted.blasr
        blasr_bam.unlink()
        pi_shifted_blasr_bam.unlink()
        pi_shifted_blasr_wip.touch()
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[(pi_shifted_blasr_bam, self.pi_shifted_fasta,
                          pi_shifted_blasr_wip)],
            blasr_found=[(pi_shifted_blasr_bam, "pi-shifted aligned")],
            blasr_not_found=[(blasr_bam, "aligned")],
        )
        # assert 1 == count_marker_files("blasr")

        pi_shifted_blasr_bam.unlink()
        pi_shifted_blasr_wip.touch()
        # He tries again, but now the file without wip is there:
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[(pi_shifted_blasr_bam, self.pi_shifted_fasta,
                          pi_shifted_blasr_wip)
                         ],
            blasr_found=[
                (blasr_bam, "aligned"),
                (pi_shifted_blasr_bam, "pi-shifted aligned")
            ]
        )
        # assert 1 == count_marker_files("blasr")

    def test_abandoned_wips_present(
            self, sm_wip_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_wip_test_data)
        blasr_bam, blasr_wip = self.make_alignment_bam_and_wip_names()
        pi_shifted_blasr_bam, pi_shifted_blasr_wip = (
            self.make_alignment_bam_and_wip_names(variant="pi-shifted")
        )
        blasr_wip.touch()
        pi_shifted_blasr_wip.touch()
        # the files have been created long ago...
        t = blasr_wip.stat().st_mtime-1000
        os.utime(blasr_wip, times=(t, t))
        os.utime(pi_shifted_blasr_wip, times=(t, t))
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[
                (blasr_bam, self.fasta, blasr_wip),
                (pi_shifted_blasr_bam, self.pi_shifted_fasta,
                 pi_shifted_blasr_wip)
            ],
            blasr_not_found=[
                (blasr_bam, "aligned"),
                (pi_shifted_blasr_bam, "pi-shifted aligned")
            ]
        )
        assert (
            f"Abandoned sentinel '{blasr_wip}' detected; overwritten."
            in output
        )
        assert (
            f"Abandoned sentinel '{pi_shifted_blasr_wip}'"
            " detected; overwritten.") in output

    def test_both_ccs_wip_files_present(
            self, sm_wip_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_wip_test_data)
        self.make_ccs()
        blasr_ccs_bam, blasr_ccs_wip = self.make_alignment_bam_and_wip_names(
            bam=self.ccs)
        blasr_ccs_wip.touch()
        pi_shifted_blasr_ccs_bam, pi_shifted_blasr_ccs_wip = (
            self.make_alignment_bam_and_wip_names(
                bam=self.ccs, variant="pi-shifted")
        )
        pi_shifted_blasr_ccs_wip.touch()
        # There is another simultaneous run of sm-analysis, but Nathan
        # tries to launch the program in parallel
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[
                (blasr_ccs_bam, self.fasta, blasr_ccs_wip),
                (pi_shifted_blasr_ccs_bam, self.pi_shifted_fasta,
                    pi_shifted_blasr_ccs_wip),
            ],
            blasr_found=[
                (blasr_ccs_bam, "aligned"),
                (pi_shifted_blasr_ccs_bam, "pi-shifted aligned"),
            ]
        )
        # assert 0 == cmd_result[1]["nprocs_blasr"]

    def test_two_blasrs_if_no_ccs_wip_files(
            self, sm_wip_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_wip_test_data)
        self.make_ccs()
        # If Nathan runs sm-analysis without another instance already
        # running, 2 blasr instances run:
        cmd = (self.bam, self.fasta)
        with run_sm_analysis(*cmd):
            ...
        assert 4 == count_marker_files("blasr")

    def test_one_ccs_wip_file_present(
            self, sm_wip_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_wip_test_data)
        self.make_ccs(missing_ok=True)
        # He runs again sm-analysis while another instance is processing
        # the same file:
        blasr_ccs_bam, blasr_ccs_wip = self.make_alignment_bam_and_wip_names(
            bam=self.ccs)
        blasr_ccs_wip.touch()
        pi_shifted_blasr_ccs_bam, pi_shifted_blasr_ccs_wip = (
            self.make_alignment_bam_and_wip_names(
                bam=self.ccs, variant="pi-shifted"
            )
        )
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[(blasr_ccs_bam, self.fasta, blasr_ccs_wip)],
            blasr_found=[(blasr_ccs_bam, "aligned")],
            blasr_not_found=[(pi_shifted_blasr_ccs_bam, "pi-shifted aligned")]
        )
        # assert 1 == count_marker_files("blasr")

        blasr_ccs_bam.unlink()
        blasr_ccs_wip.touch()
        # He tries again, but now the file without wip is there:
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[(blasr_ccs_bam, self.fasta, blasr_ccs_wip)],
            blasr_found=[
                (pi_shifted_blasr_ccs_bam, "pi-shifted aligned"),
                (blasr_ccs_bam, "aligned")
            ]
        )
        # assert 1 == count_marker_files("blasr")

        # And the same happens the other way around: blasr <-> pi-shifted.blasr
        blasr_ccs_bam.unlink()
        pi_shifted_blasr_ccs_bam.unlink()
        pi_shifted_blasr_ccs_wip.touch()
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[(pi_shifted_blasr_ccs_bam, self.pi_shifted_fasta,
                          pi_shifted_blasr_ccs_wip)],
            blasr_found=[(pi_shifted_blasr_ccs_bam, "pi-shifted aligned")],
            blasr_not_found=[(blasr_ccs_bam, "aligned")],
        )
        # assert 1 == count_marker_files("blasr")

        pi_shifted_blasr_ccs_bam.unlink()
        pi_shifted_blasr_ccs_wip.touch()
        # He tries again, but now the file without wip is there:
        cmd_result, output = self.check_blasr_msgs(
            blasr_calls=[(pi_shifted_blasr_ccs_bam, self.pi_shifted_fasta,
                          pi_shifted_blasr_ccs_wip)
                         ],
            blasr_found=[
                (blasr_ccs_bam, "aligned"),
                (pi_shifted_blasr_ccs_bam, "pi-shifted aligned")
            ]
        )
        # assert 1 == count_marker_files("blasr")

    def test_abandoned_ccs_wips_present(
            self, sm_wip_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_wip_test_data)
        self.make_ccs(missing_ok=True)
        blasr_ccs_bam, blasr_ccs_wip = self.make_alignment_bam_and_wip_names(
            bam=self.ccs)
        pi_shifted_blasr_ccs_bam, pi_shifted_blasr_ccs_wip = (
            self.make_alignment_bam_and_wip_names(
                bam=self.ccs, variant="pi-shifted"
            )
        )
        blasr_ccs_wip.touch()
        pi_shifted_blasr_ccs_wip.touch()
        # the files have been created long ago...
        t = blasr_ccs_wip.stat().st_mtime-1000
        os.utime(blasr_ccs_wip, times=(t, t))
        os.utime(pi_shifted_blasr_ccs_wip, times=(t, t))
        cmd_result, output = self.check_blasr_msgs(
            blasr_not_found=[
                (blasr_ccs_bam, "aligned"),
                (pi_shifted_blasr_ccs_bam, "pi-shifted aligned")
            ]
        )
        assert (f"Abandoned sentinel '{blasr_ccs_wip}' detected; "
                "overwritten.") in output
        assert (f"Abandoned sentinel '{pi_shifted_blasr_ccs_wip}' detected; "
                "overwritten.") in output


class TestCaseCCSWIP(SmAnalysisMixIn):
    def make_ccs_bam_and_wip_names(self):
        ccs_bam = self.bam.with_name("ccs."+self.bam.name)
        ccs_wip = ccs_bam.with_name("."+ccs_bam.name+".wip")
        return ccs_bam, ccs_wip

    def test_wip_file_present(
            self, sm_wip_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_wip_test_data)
        ccs_bam, ccs_wip = self.make_ccs_bam_and_wip_names()
        ccs_wip.touch()
        # There is another simultaneous run of sm-analysis, but Nathan
        # tries to launch the program in parallel
        self.executor.submit(lambda: remove_later(3, ccs_wip))
        self.executor.submit(lambda: run_later(2.8, self.make_ccs))
        cmd = (self.bam, self.fasta, "--verbose")
        with run_sm_analysis(*cmd) as cmd_result:
            clean_stdout = normalize_whitespaces(
                cmd_result[0].stdout.decode())
            clean_stderr = normalize_whitespaces(
                cmd_result[0].stderr.decode())
            output = clean_stdout+clean_stderr
        # He checks that sm-analysis did not compute the ccs bam file:
        assert (
            f"CCS file '{ccs_bam}' found. Skipping its computation."
        ) in output
        assert 0 == count_marker_files("ccs")

    def test_abandoned_wip_present(
            self, sm_wip_test_data, install_pbindex, install_ipdSummary,
            install_ccs, install_blasr):
        self.collect_opts_for_tests(sm_wip_test_data)
        ccs_bam, ccs_wip = self.make_ccs_bam_and_wip_names()
        ccs_wip.touch()
        # the file has been created long ago...
        t = ccs_wip.stat().st_mtime-1000
        os.utime(ccs_wip, times=(t, t))
        cmd = (self.bam, self.fasta)
        with run_sm_analysis(*cmd) as cmd_result:
            clean_stdout = normalize_whitespaces(
                cmd_result[0].stdout.decode())
            clean_stderr = normalize_whitespaces(
                cmd_result[0].stderr.decode())
            output = clean_stdout+clean_stderr
        # This time the program informs him about an old sentinel file.
        assert (
            f"CCS file '{ccs_bam}' found. Skipping its computation."
        ) not in output
        assert (
            f"Abandoned sentinel '{ccs_wip}' detected; overwritten."
        ) in output
        assert (
            "Aligned CCS file cannot be produced without CCS file. "
            "Trying to produce it..."
        ) in output
        # And he checks that sm-analysis did compute the ccs bam file:
        assert 1 == count_marker_files("ccs")
