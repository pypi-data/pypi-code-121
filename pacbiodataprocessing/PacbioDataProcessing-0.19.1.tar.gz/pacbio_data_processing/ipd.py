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

import subprocess
import functools
import logging
from concurrent import futures
from typing import Union, Optional
from collections.abc import Generator
from pathlib import Path

from .bam_utils import WorkUnitGenerator, MoleculeWorkUnit
from .constants import GFF_SUF


class UnknownErrorIpdSummary(Exception):
    ...


def ipd_summary(
        molecule: MoleculeWorkUnit,
        fasta: Union[str, Path],
        program: Path,
        nprocs: int,
        mod_types_comma_sep: str,
        ipd_model: Union[str, Path],
        skip_if_present: bool
        ) -> Optional[MoleculeWorkUnit]:
    """Lowest level interface to ``ipdSummary``: all calls to that
    program are expected to be done through this function.
    It runs ``ipdSummary`` with an input bam file like this::

      ipdSummary  blasr.pMA683.subreads.bam --reference pMA683.fa\
      --identify m6A --gff blasr.pMA683.subreads.476.bam.gff

    As a result of this, a gff file is created. This function sets an
    attribute in the target Molecule with the path to that file.

    If the process went well (``ipdSummary`` returns ``0``), the input
    ``MoleculeWorkUnit`` is returned, otherwise the molecule is tagged
    as being problematic (``had_processing_problems`` is set to ``True``)
    and ``None`` is returned.

    TBD
    ---
    Missing features:

    * skip_if_present
    """
    molecule_id, molecule = molecule
    bam = molecule.src_bam_path
    output = bam.with_suffix(GFF_SUF)
    cmd = (
        str(program), bam, "--reference", fasta, "--identify",
        mod_types_comma_sep, "--numWorkers", str(nprocs), "--gff", output
    )
    if ipd_model:
        cmd = cmd + ("--ipdModel", ipd_model)

    # if skip_if_present and output.is_file():
    #     logging.debug(f"[{program.name}] Modification file '{output}' already present!")

    process_res = subprocess.run(cmd, capture_output=True)
    if process_res.returncode == 0:
        expected_call = " ".join(str(_) for _ in cmd)
        molecule.gff_path = output
        out_msg = process_res.stdout.decode()
        logging.debug(
            f"[{program.name}] Called as follows:")
        logging.debug(f"[{program.name}] '{expected_call}'")
        logging.debug(f"[{program.name}] Output:")
        logging.debug(f"[{program.name}] {out_msg}")
        return (molecule_id, molecule)
    else:
        molecule.had_processing_problems = True
        logging.error(
            f"[{program.name}] Molecule {molecule_id} could not be processed"
        )
        err_msg = process_res.stderr.decode().strip()
        logging.debug(f"[{program.name}] The reported error was:")
        logging.debug(f"[{program.name}]     '{err_msg}'")


def multi_ipd_summary_direct(
        molecules: WorkUnitGenerator,
        fasta: Union[str, Path],
        program: Union[str, Path],
        num_ipds: int,
        nprocs_per_ipd: int,
        modification_types: str,
        ipd_model: Optional[str] = None,
        skip_if_present: bool = False
        ) -> Generator[WorkUnitGenerator, None, None]:
    """Generator that yields ``MoleculeWorkUnit`` resulting from
    ``ipd_summary`` (``None`` results are skipped).
    Serial implementation (one file produced after the other).
    """
    mod_types_comma_sep = ",".join(modification_types)
    for molecule in molecules:
        ipd_result = ipd_summary(
            molecule, fasta=fasta, program=program, nprocs=nprocs_per_ipd,
            mod_types_comma_sep=mod_types_comma_sep, ipd_model=ipd_model,
            skip_if_present=skip_if_present
        )
        if ipd_result is not None:
            yield ipd_result


def multi_ipd_summary_threads(
        molecules: WorkUnitGenerator,
        fasta: Union[str, Path],
        program: Union[str, Path],
        num_ipds: int,
        nprocs_per_ipd: int,
        modification_types: str,
        ipd_model: Optional[str] = None,
        skip_if_present: bool = False
        ) -> Generator[WorkUnitGenerator, None, None]:
    """Generator that yields ``MoleculeWorkUnit`` resulting from
    ``ipd_summary`` (``None`` results are skipped).
    Parallel implementation driven by a pool of threads.
    """
    mod_types_comma_sep = ",".join(modification_types)
    partial_ipd_summary = functools.partial(
        ipd_summary, fasta=fasta, program=program, nprocs=nprocs_per_ipd,
        mod_types_comma_sep=mod_types_comma_sep, ipd_model=ipd_model,
        skip_if_present=skip_if_present,
    )
    exe = futures.ThreadPoolExecutor(max_workers=num_ipds)
    for ipd_result in exe.map(partial_ipd_summary, molecules):
        if ipd_result is not None:
            yield ipd_result


multi_ipd_summary = multi_ipd_summary_threads
