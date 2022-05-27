#######################################################################
#
# Copyright (C) 2020-2022 David Palao
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

"""Some helper functions to manipulate BAM files
"""

import subprocess
from pathlib import Path
import logging
from collections import deque, defaultdict, Counter
from dataclasses import dataclass
from typing import Union, Optional, Any, Literal
from collections.abc import Generator, Iterable
from functools import cached_property

from .bam import BamFile
from .constants import DNA_SEQ_COLUMN, ASCII_QUALS_COLUMN
from .cigar import Cigar
from .utils import shift_me_back, find_gatc_positions


REVERSE_COMPLEMENTED_FLAG = 0x10
DIRECT_PRIMARY_FLAG = 0
SECONDARY_ALIGNMENT_FLAG = 0x100


class CircularDNAPosition:
    """A type that allows to do arithmetics with postitions
    in a circular topology.

    >>> p = CircularDNAPosition(5, ref_len=9)

    The class has a decent repr:

    >>> p
    CircularDNAPosition(5, ref_len=9)

    And we can use it in arithmetic contexts:

    >>> p + 1
    CircularDNAPosition(6, ref_len=9)
    >>> int(p+1)
    6
    >>> int(p+5)
    1
    >>> int(20+p)
    7
    >>> p - 1
    CircularDNAPosition(4, ref_len=9)
    >>> int(p-6)
    8
    >>> int(p-16)
    7
    >>> int(2-p)
    6
    >>> int(8-p)
    3

    Also boolean equality is supported:

    >>> p == CircularDNAPosition(5, ref_len=9)
    True
    >>> p == CircularDNAPosition(6, ref_len=9)
    False
    >>> p == CircularDNAPosition(14, ref_len=9)
    True
    >>> p == CircularDNAPosition(5, ref_len=8)
    False
    >>> p == 5
    False

    But also < is supported:

    >>> p < p+1
    True
    >>> p < p
    False
    >>> p < p-1
    False

    Of course two instances cannot be compared if their underlying
    references are not equally long:

    >>> s = CircularDNAPosition(5, ref_len=10)
    >>> p < s
    Traceback (most recent call last):
    ...
    ValueError: cannot compare positions if topologies differ

    or if they are not both CircularDNAPosition's:

    >>> s < 6
    Traceback (most recent call last):
    ...
    TypeError: '<' not supported between instances of 'CircularDNAPosition' and 'int'

    The class has a convenience method:

    >>> p.as_1base()
    6

    If the ref_len input parameter is less than or equal to 0, the
    topology is assumed to be linear:

    >>> q = CircularDNAPosition(5, ref_len=-1)
    >>> q
    CircularDNAPosition(5, ref_len=0)
    >>> q + 1001
    CircularDNAPosition(1006, ref_len=0)
    >>> q - 100
    CircularDNAPosition(-95, ref_len=0)
    >>> int(10-q)
    5

    Linear topology is the default behaviour:

    >>> r = CircularDNAPosition(5)
    >>> r
    CircularDNAPosition(5, ref_len=0)

    It is possitble to use them as indices in slices:

    >>> seq = "ABCDEFGHIJ"
    >>> seq[r:r+2]
    'FG'

    And CircularDNAPosition instances can be hashed (so that they can
    be elements of a set or keys in a dictionary):

    >>> positions = {p, q, r}

    And, very conveniently, a CircularDNAPosition converts tp str as
    ints do:

    >>> str(r) == '5'
    True
    """
    def __init__(self, pos: int, ref_len: int=0):
        """The parameter 'ref_len' represents the length of the sequence,
        which has full meaning only if the reference is truly circular.
        If the length is 0 or less, it is set to 0 and it is understood
        that the reference has a linear topology.
        """
        self._n = max(ref_len, 0)
        self._pos = self._wrap_around(pos)

    def _wrap_around(self, pos):
        if self._n > 0:
            pos %= self._n
        return pos

    def __add__(self, other):
        new_pos = self._wrap_around(self._pos+int(other))
        return self.__class__(new_pos, self._n)

    def __radd__(self, other):
        return self+other

    def __sub__(self, other):
        new_pos = self._wrap_around(self._pos-int(other))
        return self.__class__(new_pos, self._n)

    def __rsub__(self, other):
        return self.__class__(other, self._n)-self

    def __repr__(self):
        return f"{self.__class__.__name__}({self._pos}, ref_len={self._n})"

    def __int__(self):
        return self._pos

    def as_1base(self) -> int:
        """It returns the raw 1-based position."""
        return self._pos+1

    def __eq__(self, other):
        try:
            epos = (self._pos == other._pos)
            eref = (self._n == other._n)
        except AttributeError:
            res = False
        else:
            res = epos and eref
        return res

    def __lt__(self, other):
        try:
            same_n = self._n == other._n
        except AttributeError:
            type_self = self.__class__.__name__
            type_other = other.__class__.__name__
            raise TypeError(
                "'<' not supported between instances of "
                f"'{type_self}' and '{type_other}'"
            )
        if same_n:
            return self._pos < other._pos
        else:
            raise ValueError("cannot compare positions if topologies differ")

    def __index__(self):
        return self._pos

    def __hash__(self):
        return hash((self._pos, self._n))

    def __str__(self):
        return str(self._pos)


@dataclass
class Molecule:
    """Abstraction around a single molecule from a Bam file"""
    id: int
    src_bam_path: Optional[Union[str, Path]] = None
    _best_ccs_line: Optional[tuple[bytes]] = None

    def __post_init__(self):
        self.gff_path = None
        self.reference = ""
        self.had_processing_problems = False

    @property
    def cigar(self) -> Cigar:
        return Cigar(self._best_ccs_line[5].decode())

    @property
    def dna(self) -> str:
        return self._best_ccs_line[DNA_SEQ_COLUMN].decode()

    def __len__(self) -> int:
        return len(self.dna)

    @cached_property
    def start(self) -> CircularDNAPosition:
        """Readable/Writable attribute. It was originally only readable
        but the ``SingleMoleculeAnalysis`` class relies on it being
        writable to make easier the shift back of *pi-shifted* positions,
        that are computed from this attribute.
        The logic is: by default, the value is taken from the
        ``_best_ccs_line`` attribute, until it is modified, in which
        case the value is simply stored and returned upon request.
        """
        return CircularDNAPosition(
            int(self._best_ccs_line[3])-1, # aligner indices start at 1
            len(self.reference)
        )

    @property
    def end(self) -> CircularDNAPosition:
        """Computes the end of a molecule as
        CircularDNAPosition(start+lenght of reference)
        which, obviously takes into account the possible circular
        topology of the reference.
        """
        return self.start+len(self)

    @property
    def ascii_quals(self) -> str:
        """Ascii qualities of sequencing the molecule. Each symbol
        refers to one base.
        """
        return self._best_ccs_line[ASCII_QUALS_COLUMN].decode()

    def find_gatc_positions(self) -> list[CircularDNAPosition]:
        """The function returns the position of all the GATCs found in the
        Molecule's sequence, taking into account the topology of the
        reference.

        The return value is is the 0-based index of the GATC motif, ie,
        the index of the G in the Python convention.
        """
        positions = list(find_gatc_positions(self.dna))
        positions.sort()
        return [
            CircularDNAPosition(pos, ref_len=len(self.reference))+self.start
            for pos in positions
        ]

    def is_crossing_origin(self, *, ori_pi_shifted=False) -> bool:
        """This method answers the question of whether the molecule
        crosses the origin, assuming a circular topology of the
        chromosome.
        The answer is ``True`` if the last base of the molecue is
        located *before* the first base. Otherwise the answer is
        ``False``.
        It will return ``False`` if the molecule *starts at* the origin;
        but it will be ``True`` if it *ends at* the origin.
        There is an optional keyword-only boolean parameter, namely
        ``ori_pi_shifted`` to indicate that the reference has been
        shifted by pi radians, or not.
        """
        if ori_pi_shifted:
            offset = len(self.reference)//2
        else:
            offset = 0
        offset = CircularDNAPosition(offset, len(self.reference))
        if (self.start-offset > self.end-1-offset):
            return True
        else:
            return False

    def pi_shift_back(self) -> None:
        """Method that shifts back the (start, end) positions of
        the molecule assuming that they were shifted before by
        pi radians.
        """
        start = self.start
        pos = shift_me_back(int(start), len(self.reference))
        self.start = CircularDNAPosition(pos, len(self.reference))


MoleculeWorkUnit = tuple[int, Molecule]
WorkUnitGenerator = Generator[MoleculeWorkUnit, None, None]


def write_one_molecule_bam(
        buf: Iterable,
        header: bytes,
        in_file_name: Path,
        suffix: Any) -> Path:
    """Given a sequence of BAM lines, a header, the source name and a
    suffix, a new ``bamFile`` is created containg the data provided
    an a suitable name.
    """
    suffix = ".{}".format(suffix)
    out_bam_file = in_file_name.with_suffix(suffix+in_file_name.suffix)
    out_bam = BamFile(out_bam_file, mode="w")
    out_bam.write(header=header, body=buf)
    logging.info(f"One-molecule BAM file written: {out_bam_file}")
    buf.clear()
    return out_bam_file


def gen_index_single_molecule_bams(
        molecules: WorkUnitGenerator, program: Path,
        ) -> WorkUnitGenerator:
    """It generates indices in the form of ``.pbi`` files using
    ``program``, which must be the path to a working ``pbindex``
    executable.
    For each *molecule* read from the input *pipe*, ``program`` is
    called like follows (the argument is the BAM associated with the
    current molecule)::

       pbindex blasr.pMA683.subreads.bam

    The success of the operation is determined inspecting the return
    code.
    If the call succeeds (ie, the return code is ``0``), the corresponding
    ``MoleculeWorkUnit`` is yielded.

    If the call fails (the return code is NOT ``0``), an error is
    reported.
    """
    for (mol_id, molecule) in molecules:
        file_name = molecule.src_bam_path
        process_res = subprocess.run(
            (str(program), file_name), capture_output=True
        )
        if process_res.returncode == 0:
            yield (mol_id, molecule)
        else:
            molecule.had_processing_problems = True
            logging.error(
                f"[{program.name}] Molecule {mol_id} "
                "could not be processed"
            )
            err_msg = process_res.stderr.decode().strip()
            logging.debug(f"[{program.name}] The reported error was:")
            logging.debug(f"[{program.name}]     '{err_msg}'")


def subreads_per_molecule(
        lines: Iterable,
        header: bytes,
        file_name_prefix: Path,
        todo: dict[int, Molecule]
        ) -> WorkUnitGenerator:
    """This generator yields 2-tuples of (mol-id, Molecule) after
    having isolated the subreads corresponding to that molecule id
    from the ``lines`` (coming from the iteration over a ``BamFile``
    instance). Before yielding, a one-molecule BAM file is created.
    """
    prev_mol_id = None
    mol_id = None
    buf = deque()
    for line in lines:
        mol_id = int(line.molecule_id)
        first_time = prev_mol_id is None
        diff_id = (mol_id != prev_mol_id)
        if (not first_time) and diff_id:
            # then, we know we have lines in the buffer and the
            # mol id changed. Time to clean the buffer or write a file:
            if prev_mol_id in todo:
                new_file = write_one_molecule_bam(
                    buf, header, file_name_prefix, prev_mol_id)
                mol = todo[prev_mol_id]
                mol.src_bam_path = new_file
                yield (prev_mol_id, mol)
            else:
                buf.clear()
        buf.append(line)
        prev_mol_id = mol_id
    if mol_id in todo:
        new_file = write_one_molecule_bam(
            buf, header, file_name_prefix, mol_id)
        mol = todo[mol_id]
        mol.src_bam_path = new_file
        yield (mol_id, mol)


def split_bam_file_in_molecules(
        in_bam_file: Union[str, Path],
        tempdir: Union[str, Path],
        todo: dict[int, Molecule]
        ) -> WorkUnitGenerator:
    """All the individual molecules in the bam file path given,
    ``in_bam_file``, that are found in ``todo``, will be isolated
    and stored individually in the directory ``tempdir``.
    The yielded Molecule instances will have their ``src_bam_path``
    updated accordingly.
    """
    name_prefix = Path(tempdir) / Path(in_bam_file).name
    inbam = BamFile(in_bam_file)
    subreads = subreads_per_molecule(
        inbam.body, inbam.header, name_prefix, todo)
    for (mol_id, molecule) in subreads:
        logging.debug(f"BAM file '{molecule.src_bam_path}' generated")
        yield (mol_id, molecule)


def join_gffs(
        work_units: WorkUnitGenerator,
        out_file_path: Union[str, Path]
        ) -> Generator[Path, None, None]:
    """The gff files related to the molecules provided in the input
    are read and joined in a single file.
    The individual gff files are yielded back.

    Probably this function is useless and should be removed in the
    future: it only provides a joint gff file that is not a valid gff
    file and that is never used in the rest of the processing.
    """
    with open(out_file_path, "w") as out:
        for mol_id, molecule in work_units:
            with open(molecule.gff_path) as f:
                out.write(f.read())
            yield molecule.gff_path


def flag2strand(flag: int) -> Literal["+", "-", "?"]:
    """
    Given a ``FLAG`` (see the
    `BAM format <https://samtools.github.io/hts-specs/SAMv1.pdf>`_
    specification), it transforms it to the corresponding strand.

    :return: ``+``, ``-`` or ``?`` depending on the strand the input
             ``FLAG`` can be assigned to (``?`` means: it could not
             be assigned to any strand).
    """
    is_reverse = (
        (flag & REVERSE_COMPLEMENTED_FLAG) == REVERSE_COMPLEMENTED_FLAG
    )
    is_direct = (
        (flag == 0) or (
            (flag & SECONDARY_ALIGNMENT_FLAG) == SECONDARY_ALIGNMENT_FLAG
        )
    )
    if is_reverse:
        category = "-"
    elif is_direct:
        # This case must come after checking reverse because, eg 272 is
        # not 0, and it is secondary, so it would be classified as
        # secondary direct if not checking first if it is reverse.
        # I don't know a better way to check it for now...
        category = "+"
    else:
        # This case ('?') is not tested from the FTs point of view:
        category = "?"
    return category


def count_subreads_per_molecule(bam: BamFile) -> defaultdict[int, Counter]:
    """Given a read-open BamFile instance, it returns a defaultdict
    with keys being molecule ids (str) and values, a counter with
    subreads classified by strand.
    The possible keys of the returned counter are:
    +, -, ?
    meaning direct strand, reverse strand and unknown, respectively.
    """
    count = defaultdict(Counter)
    for line in bam:
        flag = int(line[1])
        category = flag2strand(flag)
        count[int(line.molecule_id)][category] += 1
    return count
