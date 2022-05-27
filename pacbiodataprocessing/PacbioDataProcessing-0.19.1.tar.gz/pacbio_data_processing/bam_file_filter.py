#######################################################################
#
# Copyright (C) 2020 David Velázquez
# Copyright (C) 2020, 2021 David Palao
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

"""This module contains the high level functions necessary to apply
some filters to a given input BAM file."""

import logging

from .ui.cl import parse_cl_bam_filter as parse_cl
from .bam import BamFile
from .logs import config_logging
from .filters import (
    filter_seq_len, filter_enough_data_per_molecule, filter_quality,
)
from .parameters import BamFilteringParameters
from .errors import high_level_handler


class BamFilter:
    def __init__(self, parameters):
        self.input_parameters = parameters
        self.filters = []
        min_seq_len = self.input_parameters.min_dna_seq_length
        if min_seq_len:
            self.filters.append((filter_seq_len, min_seq_len))
        min_subreads_per_molecule = (
            self.input_parameters.min_subreads_per_molecule)
        if min_subreads_per_molecule > 1:
            self.filters.append(
                (filter_enough_data_per_molecule, min_subreads_per_molecule)
            )
        quality_th = self.input_parameters.quality_threshold
        if quality_th:
            self.filters.append((filter_quality, quality_th))
        mappings = self.input_parameters.limit_mappings
        if mappings:
            self.filters.append(
                (self.input_parameters.filter_mappings, mappings,
                 self.input_parameters.min_relative_mapping_ratio)
            )

    def _apply_filters(self, lines):
        for f, *args in self.filters:
            lines = f(lines, *args)
        yield from lines

    def _write_output(self, header, body):
        outbam = BamFile(self.input_parameters.out_bam_file, mode="w")
        outbam.write(header=header, body=body)

    def __call__(self):
        inbam = BamFile(self.input_parameters.input_bam_file)
        filtered_body = self._apply_filters(inbam.body)
        self._write_output(inbam.header, filtered_body)


@high_level_handler
def main():
    cl_input = parse_cl()
    config_logging(cl_input.verbose)
    params = BamFilteringParameters(cl_input)
    logging.info(str(params))
    bam_filter = BamFilter(params)
    bam_filter()
