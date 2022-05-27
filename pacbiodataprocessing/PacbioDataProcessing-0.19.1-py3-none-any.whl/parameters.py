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

from pathlib import Path
import logging
import importlib.resources

from .filters import filter_mappings_binary, filter_mappings_ratio
from . import __version__ as VERSION


class ParametersBase:
    def __init__(self, cl_input):
        self._cl_input = cl_input

    def __getattr__(self, attr):
        return getattr(self._cl_input, attr)


class BamFilteringParameters(ParametersBase):
    def __str__(self):
        s = (
            f"Filtering '{self.input_bam_file}' to produce "
            f"'{self.out_bam_file}' with:\n"
            f"  minimun DNA sequence length: {self.min_dna_seq_length}\n"
            f"  minimun subreads per molecule: "
            f"{self.min_subreads_per_molecule}\n"
            f"  quality of sequencing: {self.quality_threshold}\n"
            f"  mappings: {self.mappings}\n"
            f"  min mapping ratio: {self.min_relative_mapping_ratio}\n"
        )
        return s

    @property
    def out_bam_file(self):
        base = self.input_bam_file.name
        new_base = "parsed." + base
        return self.input_bam_file.parent/new_base

    @property
    def limit_mappings(self):
        if self._cl_input.mappings != "all":
            return self._cl_input.mappings

    @property
    def filter_mappings(self):
        if self.min_relative_mapping_ratio:
            return filter_mappings_ratio
        return filter_mappings_binary

    @property
    def min_relative_mapping_ratio(self):
        ratio = self._cl_input.min_relative_mapping_ratio
        if ratio > 1:
            ratio = 1.0
        elif ratio < 0:
            ratio = 0.0
        return ratio


class SingleMoleculeAnalysisParameters(ParametersBase):
    def _make_out_filename(self, *, suff: str, pref: str = "") -> Path:
        base = self.input_bam_file.name
        new_base = "sm-analysis." + base
        if self.partition:
            partition, partitions = self.partition
            new_base = f"partition_{partition}of{partitions}."+new_base
        new_name = self.input_bam_file.parent/(pref+new_base)
        if new_name.suffix != ".bam":
            suff = new_name.suffix+suff
        return new_name.with_suffix(suff)

    @property
    def joint_gff_filename(self):
        return self._make_out_filename(suff=".gff")

    @property
    def one_line_per_mod_filename(self):
        return self._make_out_filename(suff=".csv")

    @property
    def summary_report_html_filename(self):
        return self._make_out_filename(suff=".html", pref="summary.")

    def _resolve_model_from_resources(self, model_name):
        container = importlib.resources.files("kineticsTools")
        return container/"resources"/f"{model_name}.npz.gz"

    @property
    def ipd_model(self):
        raw_model = self._cl_input.ipd_model
        if raw_model:
            model = Path(raw_model)
            if not model.is_file():
                model = self._resolve_model_from_resources(raw_model)
                if not model.is_file():
                    model = None
            return model

    @property
    def partition(self):
        try:
            partition, partitions = self._cl_input.partition.split(":")
        except (ValueError, AttributeError):
            return
        try:
            partition = int(partition)
            partitions = int(partitions)
        except ValueError:
            return
        if partition <= partitions:
            return partition, partitions

    def __str__(self):
        s = (
            f"Starting 'sm-analysis' (version {VERSION}) with:\n"
            f"  Input BAM file:  '{self.input_bam_file}'\n"
            f"  Reference file:  '{self.fasta}'\n"
            f"  ipd program:  '{self.ipdsummary_path}'\n"
            f"  # ipd program instances:  {self.num_simultaneous_ipdsummarys}"
            f"\n"
            f"  # workers per ipd instance:  {self.num_workers_per_ipdsummary}"
            f"\n"
            f"  modification types:  {self.modification_types}\n"
            f"  aligner:  '{self.blasr_path}'\n"
            f"  # workers blasr:  {self.nprocs_blasr}\n"
            f"  indexer:  '{self.pbindex_path}'\n"
        )
        if self.ipd_model:
            s = s + f"  ipd model:  {self.ipd_model}\n"
        elif self._cl_input.ipd_model:
            # In this case the user entered the model but it wasn't found:
            logging.error(
                f"Model '{self._cl_input.ipd_model}' "
                "not found. Using default model"
            )
        if self.partition:
            s += f"  partition:  {self.partition[0]} of {self.partition[1]}\n"
        if self.aligned_CCS_bam_file:
            s += f"  aligned CCS bam file:  '{self.aligned_CCS_bam_file}'\n"
        if self.CCS_bam_file:
            s += f"  CCS bam file:  '{self.CCS_bam_file}'\n"
        if self.keep_temp_dir:
            s += "  keep temp dir:  yes\n"
        if self.only_produce_methylation_report:
            s += "  only produce methylation report:  yes\n"
        return s
