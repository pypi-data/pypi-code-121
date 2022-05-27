#######################################################################
#
# Copyright (C) 2021 David Palao
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

from collections import deque
import itertools
import logging
from typing import Generator
from collections.abc import Iterable

from .bam import BamFile
from .bam_utils import WorkUnitGenerator, flag2strand

from .constants import (
    DNA_SEQ_COLUMN, QUALITY_COLUMN, MAPPING_COLUMN, STANDARD_MIN_DNA_LEN,
    STANDARD_MIN_QUAL, STANDARD_ACCEPTED_MAPPINGS, STANDARD_MAPPINGS_RATIO,
    STANDARD_MIN_NUM_SUBREADS
)


def filter_seq_len(lines, len_th):
    for line in lines:
        dna_len = len(line[DNA_SEQ_COLUMN])
        if dna_len >= len_th:
            # logging.debug(f"[DNA seq len: {dna_len} >= {len_th}]: OK")
            yield line
        # else:
        #     logging.debug(f"[DNA seq len: {dna_len} < {len_th}]: DISCARDED")


def empty_buffer(
        buf: deque, threshold: int, flags_seen: set
) -> Generator[tuple[bytes], None, None]:
    """
    This generator cleans the passed-in buffer either yielding its
    items, if the *conditions* are met, or throwing away them if not.

    The *conditions* are:

    1. the number of items are at least ``threshold``, and
    2. the ``flags_seen`` is a (non-necessarily proper) superset of
      ``{'+', '-'}``.
    """
    if len(buf):
        num_mols = len(buf)
        if num_mols >= threshold:
            if {"+", "-"} <= flags_seen:
                yield from buf
        buf.clear()


def filter_enough_data_per_molecule(
        lines: Iterable[tuple], threshold: int
) -> Generator[tuple[bytes], None, None]:
    """
    This generator yields the input data if (WIP) 
    """
    flags_seen = set()
    prev_mol_id = None
    mol_id = None
    buf = deque()
    for line in lines:
        mol_id = line.molecule_id
        flags_seen.add(flag2strand(line.flag))
        first_time = prev_mol_id is None
        diff_id = (mol_id != prev_mol_id)
        if (not first_time) and diff_id:
            yield from empty_buffer(buf, threshold, flags_seen)
        buf.append(line)
        prev_mol_id = mol_id
    yield from empty_buffer(buf, threshold, flags_seen)


def filter_quality(lines, quality_th):
    for line in lines:
        quality = int(line[QUALITY_COLUMN])
        if quality >= quality_th:
            # logging.debug(f"[Quality: {quality} >= {quality_th}]: OK")
            yield line
        # else:
        #     logging.debug(f"[Quality: {quality} < {quality_th}]: DISCARDED")


def filter_mappings_binary(lines, mappings, *rest):
    """Simply take or reject mappings depending on passed sequence"""
    for line in lines:
        mapping = line[MAPPING_COLUMN].decode()
        if (not mappings) or (mapping in mappings):
            yield line


# def filter_mappings_binary(lines, mappings, *rest): #
#     """Simply take or reject mappings depending on passed sequence"""
#     for line in lines:
#         mapping = line[MAPPING_COLUMN].decode()
#         if (not mappings) or (mapping in mappings):
#             logging.debug(f"[Mapping: {mapping} in {{{mappings}}}]: OK")
#             yield line
#         else:
#             logging.debug(
#                 f"[Mapping: {mapping} not in {{{mappings}}}]: DISCARDED")


def filter_mappings_ratio(lines, mappings, ratio):  # review the UTs
    """Take or reject mappings depending on ratio of wished mappings vs total
    """
    for mol, single_molecule_lines in itertools.groupby(
            lines, key=lambda x: x.molecule_id):
        lines1, lines2 = itertools.tee(single_molecule_lines)
        good_mappings = 0
        bad_mappings = 0
        for line in lines1:
            mapping = line[MAPPING_COLUMN].decode()
            if (not mappings) or (mapping in mappings):
                good_mappings += 1
            else:
                bad_mappings += 1
        measured_ratio = good_mappings/(good_mappings+bad_mappings)
        # logging.info(
        #    f"[Mapping filter (mol={mol}] computed ratio = {measured_ratio}")
        if measured_ratio >= ratio:
            yield from lines2
            # for line in lines2:
            #     mapping = line[MAPPING_COLUMN].decode()
            #     if mapping in mappings:
            #         yield line


def cleanup_molecules(molecules: WorkUnitGenerator) -> WorkUnitGenerator:
    """Generator of ``MoleculeWorkUnit``s that pass all the *standard*
    *filters*, ie the sequence of filters needed by ``sm-analysis``
    to select what molecules (and what subreads in those molecules) will
    be IPD-analyzed.

    It is assumed that each file contains subreads corresponding to
    only ONE molecule (ie, 'molecules' is a generator of tuples
    (mol id, Molecule), with ``Molecule`` being related to a single
    molecule id).
    [Note for developers: Should we allow multiple molecules per file?]

    If there are subreads surviving the filtering process, the bam
    file is overwritten with the filtered data and the tuple
    (mol id, Molecule) is yielded.
    If no subread survives the process, nothing is done (no bam
    written, no tuple yielded).
    """
    for (mol_id, molecule) in molecules:
        inbam = BamFile(molecule.src_bam_path)
        lines = inbam.body
        inmols = set(inbam.all_molecules)
        lines_f1 = filter_seq_len(lines, STANDARD_MIN_DNA_LEN)
        lines_f2 = filter_quality(lines_f1, STANDARD_MIN_QUAL)
        lines_f3 = filter_mappings_ratio(
            lines_f2, STANDARD_ACCEPTED_MAPPINGS, STANDARD_MAPPINGS_RATIO)
        lines_f4 = filter_mappings_binary(lines_f3, STANDARD_ACCEPTED_MAPPINGS)
        lines_ff = filter_enough_data_per_molecule(
            lines_f4, STANDARD_MIN_NUM_SUBREADS)
        lines_to_write = list(lines_ff)
        if len(lines_to_write) == 0:
            for mol in inmols:
                mol = mol.decode()
                logging.debug(f"[filter]  Molecule '{mol}' rejected")
            continue
        else:
            out_bam = BamFile(molecule.src_bam_path, mode="w")
            out_bam.write(header=inbam.header, body=lines_to_write)
            yield (mol_id, molecule)
