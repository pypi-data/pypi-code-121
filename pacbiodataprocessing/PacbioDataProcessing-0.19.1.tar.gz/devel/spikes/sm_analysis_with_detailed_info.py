#######################################################################
#
# Copyright (C) 2020, 2021 David Palao
# Copyright (C) 2020 David Velázquez
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

"""This module contains the high level functions necessary to run
the 'Single Molecule Analysis' on an input BAM file."""


import subprocess
import logging
from pathlib import Path
import os
from tempfile import TemporaryDirectory
import shutil
import csv
from itertools import groupby
import time
from statistics import mean
from collections import Counter # untested

from .bam_utils import (
    split_bam_file_in_molecules, select_molecules_from_partition,
    gen_index_single_molecule_bams, join_gffs
)
from .bam import BamFile
from .cigar import Cigar
from .logs import config_logging
from .ui.cl import parse_cl_sm_analysis as parse_cl
from .parameters import SingleMoleculeAnalysisParameters
from .ipd import multi_ipd_summary
from .constants import DNA_SEQ_COLUMN, BLASR_PREF
from .errors import high_level_handler
from .blasr import blasr
from .utils import combine_scores


MODIFIED_BASE_STR = "modified_base"
METHYLATION_REPORT_HEADER = [
    "molecule id", "sequence", "start of molecule", "end of molecule",
    "len(molecule)", "sim ratio", "count(GATC)", "positions of GATCs",
    "count(methylation states)", "methylation states",
    "combined score", "mean(score)", "min(IPDRatio)", "mean(IPDRatio)",
    "combined idQV", "mean(idQV)", "mean(coverage)"
]
METHYLATION_REPORT_MISSING_ALIGNED_CCS_MSG = (
    "Methylation report cannot be produced without an aligned CCS file."
    " Trying to produce it..."
)
METHYLATION_REPORT_MISSING_CCS_MSG = (
    "Aligned CCS file cannot be produced without CCS file. "
    "Trying to produce it..."
)


def add_to_own_output(gffs, own_output_file_name, modification_types):
    """From a set of .gff files, a csv file (delimiter=",") is saved
    with the following columns:

      - mol id: taken each gff file (e.g. 'a.b.c.gff' -> mol id: 'b')
      - modtype: column number 3 (idx: 2) of the gffs (feature type)
      - GATC position: column number column number 5 (idx: 4) of the
        gffs which corresponds to the 'end coordinate of the feature'
        in the GFF3 standard
      - score of the feature: column number 6 (idx: 5); floating point
        (Phred-transformed pvalue that a kinetic deviation exists at
        this position)
      - strand: strand of the feature. It can be +, - with obvious
        meanings. It can also be ? (meaning unknown) or . (for non
        stranded features)

    There are more columns, but they are nor fixed in number. They
    correspond to the values given in the 'attributes' column of the
    gffs (col 9, idx 8).
    For example, given the following attributes column::

      coverage=134;context=TCA...;IPDRatio=3.91;identificationQv=228

    we would get the following 'extra' columns::

      134,TCA...,3.91,228

    and this is exactly what happens with the m6A modification type.

    All the lines starting by '#' in the gff files are ignored.
    The format of the gff file is GFF3:
    https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md

    The value of identificationQV is a a phred transformed probability of
    having a detection. See eq. (8) in [1]

    [1]: "Detection and Identification of Base Modifications with Single
    Molecule Real-Time Sequencing Data"
    """
    # wouldn't it be good if before writing, a dictionary is created
    # with the data already written to the file?
    # This would be helpful to avoid double writing lines
    with open(own_output_file_name, "a") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=",")
        for gff in gffs:
            molecule = str(gff).split(".")[-2]
            with open(gff) as gff_file:
                for line in gff_file:
                    if line.startswith("#"):
                        continue
                    pieces = line.split()
                    if pieces[2] in modification_types:
                        extra = [_.split("=")[1] for _ in pieces[8].split(";")]
                        new_line = [molecule, pieces[2]] + pieces[4:7] + extra
                        csvwriter.writerow(new_line)
    logging.info(f"Own output '{own_output_file_name}' created")


def restore_old_run(old_path, new_path):  #
    keep_old = False
    if os.path.isdir(old_path) and os.path.isdir(new_path):
        for fn in os.listdir(old_path):
            try:
                shutil.move(str(old_path/fn), str(new_path))
            except Exception as e:
                logging.error(f"Error moving '{fn}': {e}")
                keep_old = True
    try:
        if not keep_old:
            shutil.rmtree(old_path, ignore_errors=True)
    except Exception as e:
        logging.error(f"Error removing '{old_path}': {e}")


def ccs(infilename):
    # logging.debug(
    #     "[CCS] Starting computation of Circular Consensus Sequence")
    infilename = Path(infilename)
    base = infilename.name
    new_base = "ccs." + base
    outfilename = infilename.parent/new_base
    ccs_proc = subprocess.run(
        ("ccs", infilename, outfilename), capture_output=True)
    if ccs_proc.returncode == 0:
        logging.info(f"[ccs] File '{outfilename}' generated")
        return outfilename
    else:
        msg = ccs_proc.stderr.decode()
        logging.error(f"[ccs] Could not generate '{outfilename}'")
        logging.error(f"[ccs] ...the error was: {msg}")


def find_gatc_positions(dna):
    """The function returns the position of all the GATCs found in the
    given sequence.

    The return value can be understood as *either* the:

    * 0-based position of the A, or the
    * 1-based position of the G
    """
    gatc_positions = []
    prev = 0
    while True:
        pos = dna.find("GATC", prev)
        if pos != -1:
            gatc_positions.append(pos+1)
            prev = pos+1
        else:
            break
    return gatc_positions


# The next should maybe be absorved by MethylationReport. (?)
def map_molecules_with_highest_sim_ratio(bam_file_name):
    """Given the path to a bam file, it returns a dictionary, whose
    keys are mol ids (strings) and the values are the corresponding
    lines, splitted as bytes.
    If multiple lines share the mol id, the one with the highest
    similarity ratio (according to the cigar) is chosen.
    """
    logging.info(
        "[methylation report] Generating molecules mapping "
        "from aligned CCS file")
    mols = {}
    bam = BamFile(bam_file_name)
    for line in bam.body:
        mol_id = line.molecule_id.decode()
        mol = mols.setdefault(mol_id, line)
        if mol != line:
            oldc = Cigar(mol[5])
            newc = Cigar(line[5])
            if newc.sim_ratio > oldc.sim_ratio:
                mols[mol_id] = line
    logging.debug(
        f"[methylation report] ccs lines (aligned): {len(mols)} "
        "molecules found")
    return mols


def match_methylation_states_m6A(pos_plus, dna_pos, ipd_meth_states):
    state = set()
    pos_min = pos_plus+1
    for j, s in ((pos_plus, "+"), (pos_min, "-")):
        try:
            ipd_state = ipd_meth_states[j+dna_pos]
        except KeyError:
            pass
        else:
            if s == ipd_state:
                state.add(ipd_state)
    # logging.debug(
    #     f"[methylation report] {mol_id}: state {state} (pos={pos_plus})")
    if state == set():
        return "0"
    elif state < set("+-"):
        return state.pop()
    elif state == set("+-"):
        return "f"
    else:
        logging.error(
            f"[methylation report] inconsistent state {state} (pos={pos_plus})"
        )


def generate_aligned_CCS_file(
        in_bam, ccs_bam_file, aligned_ccs_bam_file, fasta, nprocs, blasr_path):
    """If 'ccs_bam_file' is not given, or it does not exist, 'in_bam' is passed
    to the 'ccs' program to produce a file called 'ccs.'+in_bam.

    Once there is a 'ccs_bam_file' it is aligned with 'blasr'.
    """
    logging.warning(METHYLATION_REPORT_MISSING_ALIGNED_CCS_MSG)
    if (not ccs_bam_file) or (not Path(ccs_bam_file).exists()):
        logging.warning(METHYLATION_REPORT_MISSING_CCS_MSG)
        ccs_bam_file = ccs(in_bam)
    else:
        ccs_bam_file = Path(ccs_bam_file)
    if not aligned_ccs_bam_file:
        aligned_ccs_bam_file = ccs_bam_file.parent / ccs_bam_file.with_name(
            BLASR_PREF+ccs_bam_file.name).name
    else:
        aligned_ccs_bam_file = Path(aligned_ccs_bam_file)
    blasr(blasr_path, ccs_bam_file, fasta, nprocs, aligned_ccs_bam_file)
    return aligned_ccs_bam_file


def summarize_bam(bam): # untested
    subreads = Counter()
    sim_ratios = {}
    gatcs = {}
    lens_dnas = {}
    for line in bam:
        mol_id = line.molecule_id.decode()
        subreads[mol_id] += 1
        
        ratios = sim_ratios.setdefault(mol_id, [])
        ratios.append(Cigar(line[5].decode()).sim_ratio)

        num_gatcs = gatcs.setdefault(mol_id, [])
        num_gatcs.append(
            len(find_gatc_positions(
                line[DNA_SEQ_COLUMN].decode()
            ))
        )

        lens_dna = lens_dnas.setdefault(mol_id, [])
        lens_dna.append(len(line[DNA_SEQ_COLUMN]))
        
    return {
        "subreads": subreads,
        "sim_ratios": sim_ratios,
        "# GATCs": gatcs,
        "len(dna)s": lens_dnas,
    }
    

class MethylationReport:
    _VALID_MODIFICATION_TYPES = ("m6A",)

    def __init__(
            self, detections_csv, aligned_ccs_bam_file, modification_types,
            reference, input_bam): # reference, input_bam: untested
        self._detections_csv = Path(detections_csv)
        self._molecules = map_molecules_with_highest_sim_ratio(
            aligned_ccs_bam_file)
        base = self._detections_csv.name
        new_base = "methylation." + base
        self.csv_name = self._detections_csv.parent/new_base
        self.modification_types = modification_types
        self._reference_file_name = reference # untested
        self.input_bam = input_bam # untested

    @property # untested
    def reference_seq(self):
        with open(self._reference_file_name) as reff:
            header = reff.readline()
            seq = "".join(_.strip() for _ in reff.readlines())
        return seq

    @property
    def modification_types(self):
        return self._modification_types

    @modification_types.setter
    def modification_types(self, values):
        self._modification_types = []
        for mod in values:
            if mod in self._VALID_MODIFICATION_TYPES:
                self._modification_types.append(mod)
            else:
                logging.warning(
                    f"[methylation report] modifications of type '{mod}' will"
                    " be ignored"
                )

    def save(self):
        with open(self._detections_csv) as csv_in:
            csvreader = csv.reader(csv_in, delimiter=",")
            with open(self.csv_name, "w") as csv_out:
                csvwriter = csv.writer(csv_out, delimiter=";")
                csvwriter.writerow(METHYLATION_REPORT_HEADER)
                self._write_molecules(csvreader, csvwriter)

    def _write_molecules(self, csvreader, csvwriter):
        """This method implements the methylation report format V3
        It works only for m6A modification types.
        """
        MRLH = "[methylation report]" # untested
        all_gatc_positions = set() # untested
        gatc_positions_in_ref = set(find_gatc_positions(self.reference_seq)) # untested
        in_bam = BamFile(self.input_bam) # untested
        num_mols_original = in_bam.num_molecules # untested
        logging.info(f"{MRLH} Summarizing input BAM...") # untested
        in_bam_summary = summarize_bam(in_bam) # untested
        logging.info(f"{MRLH} ...done!") # untested
        mols_in = set() # untested
        mols_out = set() # untested
        num_detections_in = 0 # untested
        num_detections_out = 0 # untested
        num_methylations = 0 # untested
        for mol_id, detections in groupby(csvreader, key=lambda x: x[0]):
            try:
                mol = self._molecules[mol_id]
            except KeyError:
                mols_out.add(mol_id) # untested
                for _ in detections: # untested
                    num_detections_out += 1 # untested
                msg = (
                    f"Molecule '{mol_id}' expected to be found in "
                    f"raw CCS bam file, but it wasn't found"
                )
                logging.error(msg)
                subreads = in_bam_summary["subreads"][mol_id] # untested
                sim_ratios = in_bam_summary["sim_ratios"][mol_id] # untested
                sim_ratios.sort(reverse=True) # untested
                num_gatcs = in_bam_summary["# GATCs"][mol_id] # untested
                lens_dnas = in_bam_summary["len(dna)s"][mol_id] # untested
                summary_msgs = [ # untested
                    f"{MRLH}[mol={mol_id}] # subreads: {subreads}",
                    f"{MRLH}[mol={mol_id}] sim ratios: {sim_ratios}",
                    f"{MRLH}[mol={mol_id}] # GATCs: {num_gatcs}",
                    f"{MRLH}[mol={mol_id}] # len(dna)s: {lens_dnas}",
                ]
                for summary_msg in summary_msgs: # untested
                    logging.error(summary_msg) # untested
                logging.error("")
                continue
            else:
                mols_in.add(mol_id) # untested
            dna = mol[DNA_SEQ_COLUMN].decode()
            dna_pos = int(mol[3].decode())-1  # aligner indices start by 1

            gatc_positions = find_gatc_positions(dna)
            
            for _pos in gatc_positions: # untested
                _abs_pos = _pos+dna_pos # untested
                all_gatc_positions.add(_abs_pos) # untested
                if _abs_pos not in gatc_positions_in_ref: # untested
                    diffs = {_-_abs_pos for _ in gatc_positions_in_ref}
                    closest_gatcs_in_ref = [
                        _+_abs_pos for _ in sorted(diffs, key=lambda x:x*x)[:3]]
                    logging.info(f"{MRLH}[mol={mol_id}] GATC given by ipdSummary (pos={_abs_pos}; rel={_pos}) not found in reference")
                    logging.info(f"{MRLH}[mol={mol_id}] The closest GATCs in the reference are at positions: {closest_gatcs_in_ref}")
                    cigar = Cigar(mol[5])
                    logging.info(f"{MRLH}[mol={mol_id}] --> {cigar}")
                    logging.info("---")
                    

            # logging.debug(
            #     f"[methylation report] {mol_id}: gatcs: "
            #     f"{gatc_positions} ({abs_gatc_positions})"
            # )
            num_gatc = len(gatc_positions)

            ipd_meth_states = {}
            scores = []
            ipdratios = []
            idQVs = []
            coverages = []
            for detection in detections:
                num_detections_in += 1 # untested
                modification = detection[1]
                if modification in self.modification_types:
                    state = detection[4]
                    pos = int(detection[2])-1  # positions in the csv are 1-based
                    ipd_meth_states[pos] = state
                    scores.append(float(detection[3]))
                    ipdratios.append(float(detection[7]))
                    idQVs.append(float(detection[8]))
                    coverages.append(float(detection[5]))
            # logging.debug(
            #    f"[methylation report] {mol_id}: ipd states: "
            #    f"{ipd_meth_states}")
            meth_states = {}
            for pos_plus in gatc_positions:
                out_state = match_methylation_states_m6A(
                    pos_plus, dna_pos, ipd_meth_states)
                if out_state:
                    meth_states[pos_plus] = out_state
            out_states = [meth_states[_] for _ in sorted(meth_states.keys())]

            sim_ratio = "{:g}".format(Cigar(mol[5]).sim_ratio)
            num_meths_in_this_mol = len([_ for _ in out_states if _ != "0"])
            num_meth_states = "{:d}".format(num_meths_in_this_mol)
            num_methylations += num_meths_in_this_mol # untested
            combined_scores = "{:0.1f}".format(combine_scores(scores))
            mean_scores = "{:0.1f}".format(mean(scores))
            min_ipdratio = "{:0.2f}".format(min(ipdratios))
            mean_ipdratio = "{:0.2f}".format(mean(ipdratios))
            combined_idQVs = "{:0.1f}".format(combine_scores(idQVs))
            mean_idQVs = "{:0.1f}".format(mean(idQVs))
            mean_coverages = "{:0.0f}".format(mean(coverages))
            # dna_pos is 0-based (Python convention), but the output must be
            # 1-based! since the gatc_positions are the 1-based positions of
            # the G, the positions output to the methylation report are
            # correct:
            if num_gatc:
                row = (
                    mol_id, dna, str(dna_pos+1), str(dna_pos+len(dna)),
                    str(len(dna)), sim_ratio, str(num_gatc),
                    ",".join([str(dna_pos+_) for _ in gatc_positions]),
                    num_meth_states, ",".join(out_states), combined_scores,
                    mean_scores, min_ipdratio, mean_ipdratio, combined_idQVs,
                    mean_idQVs, mean_coverages
                )
                csvwriter.writerow(row)
        # untested:
        logging.info(f"{MRLH} =====")
        gatcs_in_ref_not_modified = gatc_positions_in_ref - all_gatc_positions
        gatcs_modified_not_in_ref = all_gatc_positions - gatc_positions_in_ref
        logging.info(
            f"{MRLH} Num of GATCs found in the reference: {len(gatc_positions_in_ref)}")
        logging.info(
            f"{MRLH} Num of GATCs found with modifications: {len(all_gatc_positions)}")
        logging.info(
            f"{MRLH} Num of GATCs found in the reference but NOT modified: {len(gatcs_in_ref_not_modified)}")
        logging.info(
            f"{MRLH} Num of modified GATCs NOT found in the reference: {len(gatcs_modified_not_in_ref)}")
        logging.info(f"{MRLH} Positions of modified GATCs NOT found in the reference: {gatcs_modified_not_in_ref}")
        logging.info(f"{MRLH} =====")
        logging.info(f"{MRLH} Num molecules in input BAM: {num_mols_original}")
        logging.info(f"{MRLH} Num molecules in methylation report: {len(mols_in)}")
        logging.info(f"{MRLH} Num molecules with modifications (<=ipdSummary) excluded: {len(mols_out)}")
        logging.info(f"{MRLH} =====")
        logging.info(f"{MRLH} Num detections by ipdSummary included (molecule OK): {num_detections_in}")
        logging.info(f"{MRLH} Num detections by ipdSummary excluded (molecule discarded): {num_detections_out}")
        logging.info(f"{MRLH} =====")
        logging.info(f"{MRLH} Num of methylations found: {num_methylations}")


def produce_methylation_report(
        csv_own_file, modification_types,
        in_bam_file=None, ccs_bam_file=None,
        aligned_ccs_bam_file=None, fasta=None, nprocs=1, blasr_path=None):
    # code smell! Too many parameters
    # refactor hint: make it a method of SingleMoleculeAnalysis

    if not aligned_ccs_bam_file:  # or it does not exist (TBI)
        aligned_ccs_bam_file = generate_aligned_CCS_file(
            in_bam_file, ccs_bam_file, aligned_ccs_bam_file, fasta, nprocs,
            blasr_path)
    mr = MethylationReport(
        detections_csv=csv_own_file,
        aligned_ccs_bam_file=aligned_ccs_bam_file,
        modification_types=modification_types,
        reference=fasta, # untested
        input_bam=in_bam_file, # untested
    )
    mr.save()


class SingleMoleculeAnalysis:
    def __init__(self, parameters):
        self.input_parameters = parameters
        self._set_tasks()

    def _set_tasks(self):
        opmr = self.input_parameters.only_produce_methylation_report
        self._do_split_bam = not opmr
        self._do_generate_indices = not opmr
        self._do_ipd_analysis = not opmr
        self._do_create_own_output = not opmr
        self._do_produce_methylation_report = True
        self._do_need_temp_dir = not opmr

    def _split_bam(self):
        if self._do_split_bam:
            molecules_todo = select_molecules_from_partition(
                self.input_parameters.input_bam_file,
                self.input_parameters.partition
            )
            self._per_molecule_bam_generator = split_bam_file_in_molecules(
                self.input_parameters.input_bam_file,
                self._workdir.name, molecules_todo)

    def _generate_indices(self):
        if self._do_generate_indices:
            self._indexed_bams_generator = gen_index_single_molecule_bams(
                self._per_molecule_bam_generator,
                self.input_parameters.pbindex_path
            )

    def _ipd_analysis(self):
        if self._do_ipd_analysis:
            self._single_molecule_gff_generator = multi_ipd_summary(
                self._indexed_bams_generator,
                self.input_parameters.fasta,
                self.input_parameters.ipdsummary_path,
                self.input_parameters.num_simultaneous_ipdsummarys,
                self.input_parameters.num_workers_per_ipdsummary,
                self.input_parameters.modification_types,
                self.input_parameters.ipd_model
            )

    def _dump_results(self):
        if self._do_create_own_output:
            joint_gffs = join_gffs(
                self._single_molecule_gff_generator,
                self.input_parameters.joint_gff_filename
            )
            add_to_own_output(
                joint_gffs,
                self.input_parameters.one_line_per_mod_filename,
                self.input_parameters.modification_types,
            )
        if self._do_produce_methylation_report:
            produce_methylation_report(
                self.input_parameters.one_line_per_mod_filename,
                self.input_parameters.modification_types,
                in_bam_file=self.input_parameters.input_bam_file,
                fasta=self.input_parameters.fasta,
                nprocs=self.input_parameters.nprocs_blasr,
                blasr_path=self.input_parameters.blasr_path,
                aligned_ccs_bam_file=(
                    self.input_parameters.aligned_CCS_bam_file),
                ccs_bam_file=self.input_parameters.CCS_bam_file,
            )

    def _backup_temp_dir_if_needed(self):
        if self._do_need_temp_dir:
            if self.input_parameters.keep_temp_dir:
                suffix = ".backup"
                partition = self.input_parameters.partition
                if partition:
                    ip, p = partition
                    suffix = f"-partition_{ip}of{p}"+suffix
                backup = Path(self._workdir.name+suffix)
                shutil.copytree(Path(self._workdir.name), backup)
                logging.debug(f"Copied temporary dir to: '{backup}'")

    def _make_temp_dir(self):
        if self._do_need_temp_dir:
            self._workdir = TemporaryDirectory(dir=".")

    def __call__(self):
        start = time.time()
        self._make_temp_dir()
        self._split_bam()
        self._generate_indices()
        self._ipd_analysis()
        self._dump_results()
        self._backup_temp_dir_if_needed()
        end = time.time()
        t = end-start
        t_h = t/3600
        logging.info(
            f"Execution time (wall clock time): {t:.2f} s = {t_h:.2f} h")


@high_level_handler
def main():
    config = parse_cl()
    config_logging(config.verbose)
    # default_dir = resource_filename(Requirement.parse(
    #     'kineticsTools'), 'kineticsTools/resources')
    # logging.info(str(default_dir))
    params = SingleMoleculeAnalysisParameters(config)
    logging.info(str(params))
    sma = SingleMoleculeAnalysis(params)
    sma()


# def old_main(): #
#     starttime = time.time()
#     program = SM_ANALYSIS_EXE
#     config = parse_cl()
#     config_logging(config.verbose)
#     logging.info(f"Starting {program}")
#     call_cmd = " ".join(sys.argv)
#     logging.debug(f" ...called like: '{call_cmd}'")

#     in_bam_file = config.input_bam_file
#     bam_file = in_bam_file
#     partition_limits = check_partition(config.partition)
#     out_gff_file = make_out_filename(in_bam_file, ".gff", partition_limits)
#     own_output_file_name = make_out_filename(
#         in_bam_file, ".csv", partition_limits)
#     if config.only_produce_methylation_report:
#         logging.info("Only producing methylation report...")
#     else:
#         skip_if_present = False
#         try:
#             restart_dir = config.restart_from_old_dir
#         except AttributeError:
#             restart_dir = None
#         with tempfile.TemporaryDirectory(dir=".") as tempdir:
#             if restart_dir:
#                 restore_old_run(restart_dir, tempdir)
#                 skip_if_present = True
#             else:
#                 open(own_output_file_name, "w").close()
#             if config.align_file:
#                 out_name = in_bam_file.parent / in_bam_file.with_name(
#                     BLASR_PREF+in_bam_file.name).name
#                 blasr(
#                     config.blasr_program,
#                     in_bam_file, config.fasta, config.nprocs_blasr, out_name
#                 )
#                 bam_file = out_name

#             mols_todo = select_molecules_partition(
#                 bam_file, partition_limits, config.molecule_column)
#             single_molecule_bam_files = split_bam_file_in_molecules(
#                 bam_file, tempdir, config.molecule_column, mols_todo)
#             # aligned_molecules = multi_blasr(
#             #     molecules, config.fasta, config.blasr_program,
#             #     config.nprocs, skip_if_present
#             # )
#             indexed_molecules = gen_index(
#                 single_molecule_bam_files, config.pbindex_program,
#                 skip_if_present
#             )
#             analyzed_aligned_molecules = multi_ipd_summary(
#                 indexed_molecules, config.fasta, config.ipdsummary_program,
#                 config.num_simultaneous_ipdsummarys, config.nprocs,
#                 config.modification_type, config.ipd_model,
#                 skip_if_present
#             )
#             gff_stored = join_gffs(analyzed_aligned_molecules, out_gff_file)
#             add_to_own_output(
#                 gff_stored, own_output_file_name, config.modification_type
#             )
#             if config.keep_temp_dir:
#                 base = Path(tempdir).name
#                 backup_dir = add_partition_string_to_filename(
#                     base, partition_limits)
#                 shutil.copytree(tempdir, backup_dir)
#                 logging.debug(f"Backup data in directory: {backup_dir}")
#     produce_methylation_report(
#         own_output_file_name, blasr_program=config.blasr_program,
#         fasta=config.fasta, nprocs=config.nprocs_blasr,
#         in_bam_file=bam_file, ccs_bam_file=config.CCS_bam_file,
#         aligned_ccs_bam_file=config.aligned_CCS_bam_file)

#     elapsed_s = time.time()-starttime
#     elapsed_h = elapsed_s/3600
#     logging.debug(
#         f"Execution time (wall clock time): {elapsed_s} s = {elapsed_h} h")
