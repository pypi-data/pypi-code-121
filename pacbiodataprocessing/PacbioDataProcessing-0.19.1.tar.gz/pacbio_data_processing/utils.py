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

from math import log10
from typing import Optional, Union, TypeVar, Any, Generic, Callable
from pathlib import Path
from functools import cached_property
from hashlib import md5
from collections.abc import Sequence
import time
from uuid import uuid1

import Bio.Seq
import Bio.SeqIO
from Bio.SeqIO import SeqRecord
from pyfaidx import Faidx

from .bam import BamFile
from .types import PathOrStr
from .constants import WAIT_TIME_SECONDS, NEXT_WAIT_TIME_FACTOR


DNASeqType = TypeVar("DNASeqType", bound="DNASeq")
DNASeqLike = TypeVar("DNASeqLike")


def combine_scores(scores: Sequence[float]) -> float:
    """It computes the combined phred transformed score of the ``scores``
    provided. Some examples:

    >>> combine_scores([10])
    10.0
    >>> q = combine_scores([10, 12, 14])
    >>> print(round(q, 6))
    7.204355
    >>> q = combine_scores([30, 20, 100, 92])
    >>> print(round(q, 6))
    19.590023
    >>> q_500 = combine_scores([30, 20, 500])
    >>> q_no_500 = combine_scores([30, 20])
    >>> q_500 == q_no_500
    True
    >>> combine_scores([200, 300, 500])
    200.0
    """
    p_ok = 1
    for q in scores:
        p_ok *= 1-10**(-q/10)
    try:
        combined_score = -10*log10(1-p_ok)
    except ValueError:
        combined_score = float(min(scores))
    return combined_score


class DNASeq(Generic[DNASeqLike]):
    """Wrapper around 'Bio.Seq.Seq'."""
    def __init__(
            self, raw_seq: DNASeqLike, name: str = "", description: str = ""):
        self._seq = Bio.Seq.Seq(raw_seq)
        self.name = name
        self.description = description
        self.fasta_name = None

    def __eq__(self, other: DNASeqLike) -> bool:
        return self._seq.upper() == other.upper()

    def __getattr__(self, attr: str) -> Any:
        return getattr(self._seq, attr)

    def upper(self) -> Bio.Seq.Seq:
        return self._seq.upper()

    def __getitem__(self, idx: Union[int, slice]) -> DNASeqType:
        return DNASeq(self._seq[idx])

    def __len__(self) -> int:
        return len(self._seq)

    @classmethod
    def from_fasta(cls: type[DNASeqType], fasta_name: str) -> DNASeqType:
        """Returns a DNASeq from the first DNA sequence stored in
        the fasta named 'fasta_name'.
        """
        seq_record_iter = Bio.SeqIO.parse(fasta_name, "fasta")
        record = next(seq_record_iter)
        seq = cls(
            record.seq, name=record.name, description=record.description
        )
        seq.fasta_name = fasta_name
        return seq

    def pi_shifted(self) -> DNASeqType:
        """Method to return a pi-shifted DNASeq from the original one.
        pi-shifted means that a circular topology is assumed in the
        DNA sequence and a shift in the origin is done by π radians, ie
        the sequence is splitted in two parts and both parts are permuted.
        """
        N = len(self)
        original = self._seq
        return DNASeq(
            original[N//2:]+original[:N//2], name=self.name,
            description=self.description+" (pi-shifted)"
        )

    def write_fasta(self, output_file_name: PathOrStr) -> None:
        # The next would be useful to have the metadata:
        #     orig = Bio.SeqIO.parse(self.source_fasta, "fasta")
        #     rec = next(orig)
        #     rec.seq = self._seq
        rec = SeqRecord(self._seq, id=self.name, description=self.description)
        Bio.SeqIO.write([rec], output_file_name, "fasta")
        Faidx(output_file_name)

    @cached_property
    def md5sum(self) -> str:
        """It returns the MD5 checksum's hexdigest of the *upper*
        version of the sequence as a string.
        """
        return md5(str(self._seq).upper().encode()).hexdigest()


class Partition:
    """A ``Partition`` is a class that helps answering the following
    question: assuming that we are interested in processing a fraction
    of a BamFile, does the molecule ID ``mol_id`` belongs to that
    fraction, or not?
    A prior implementation consisted in storing all the molecule IDs
    in the ``BamFile`` for a given partition in a set, and the answer
    is just obtained by querying if a molecule ID belongs to the set or
    not.
    That former implementation is not enough for the case of multiple
    alignment processes for the same raw ``BamFile`` (eg, when a
    combined analysis of the so-called 'straight' and 'pi-shifted'
    variants is performed). In that case the partition is decided with
    one file. And all molecule IDs belonging to the non-empty
    intersection with the other file must be unambiguously accomodated
    in a certain partition. This class has been designed to solve
    that problem.
    """

    def __init__(
            self,
            partition_specification: Optional[tuple[int, int]],
            bamfile: BamFile) -> None:
        try:
            current, num_partitions = partition_specification
        except TypeError:
            current, num_partitions = 1, 1
        self._current = current
        self._num_partitions = num_partitions
        self._bamfile = bamfile
        self._delimit_partitions()
        self._set_current_limits()

    def _delimit_partitions(self) -> None:
        """:meta public:
        [Internal method]
        This method decides what are the limits of all partitions
        given the number of partitions.
        The method sets an internal mapping, ``self._lower_limits``, of
        the type ``{partition number [int]: lower limit [int]}``
        with that information.
        This mapping is populated with *all* the partition numbers and
        corresponding values.
        """
        nmols = self._bamfile.num_molecules
        mols_per_part = nmols//self._num_partitions
        lower_limits = {}
        all_mols = [int(_) for _ in self._bamfile.all_molecules]
        all_mols.sort()
        lower_limits[1] = 0
        for ipart in range(2, self._num_partitions+1):
            lower_limits[ipart] = all_mols[mols_per_part*(ipart-1)]
        self._lower_limits = lower_limits

    def _set_current_limits(self) -> None:
        """:meta public:
        [Internal method]
        Auxiliary method for __contains__
        Here it is determined what is the range of molecule IDs, as
        ints, that belong to the partition.
        The method sets two integer attributes, namely:
        - ``_lower_limit_current``: the minimum molecule ID of the
          current partition, and
        - ``_higher_limit_current``: the maximum molecule ID of the
          current partition; it can be ``None``, meaning that there
          is no maximum (last partition).
        """
        self._lower_limit_current = self._lower_limits[self._current]
        if self._current == self._num_partitions:
            self._higher_limit_current = None
        else:
            self._higher_limit_current = self._lower_limits[self._current+1]

    def __contains__(self, mol_id: Union[bytes, int, str]) -> bool:
        """Main mathod of the Partition class. It decides whether a
        given molecule ID, ``mol_id`` is within the limits of the
        partition.
        """
        mol_id = int(mol_id)
        if mol_id >= self._lower_limit_current:
            lower_check = True
        else:
            lower_check = False
        if ((self._higher_limit_current is None) or
                (mol_id < self._higher_limit_current)):
            higher_check = True
        else:
            higher_check = False
        return lower_check and higher_check


def find_gatc_positions(seq: str, offset: int = 0) -> set[int]:
    """Convenience function that computes the positions of all GATCs
    found in the given sequence.
    The values are relative to the offset.

    >>> find_gatc_positions('AAAGAGAGATCGCGCGATC') == {7, 15}
    True
    >>> find_gatc_positions('AAAGAGAGTCGCGCCATC')
    set()
    >>> find_gatc_positions('AAAGAGAGATCGgaTcCGCGATC') == {7, 12, 19}
    True
    >>> s = find_gatc_positions('AAAGAGAGATCGgaTcCGCGATC', offset=23)
    >>> s == {30, 35, 42}
    True
    """
    result = set()
    prev = 0
    seq = seq.upper()
    while (pos := seq.find("GATC", prev)) != -1:
        result.add(pos+offset)
        prev = pos+1
    return result


def shift_me_back(pos: int, nbp: int) -> int:
    """Unshifts a given position taking into account that it has been
    previously shifted by half of the number of base pairs. It takes
    into account the possibility of having a sequence with an odd
    length.

    @params:

       * pos - 1-based position of a base pair to unshift
       * nbp - number of base pairs in the reference

    @returns:

       * unshifted position

    Some examples:

    >>> shift_me_back(3, 10)
    8
    >>> shift_me_back(1, 20)
    11
    >>> shift_me_back(3, 7)
    6
    >>> shift_me_back(4, 7)
    7
    >>> shift_me_back(5, 7)
    1
    >>> shift_me_back(7, 7)
    3
    >>> shift_me_back(1, 7)
    4

    To understand the operation of this function consider the following
    example. Given a sequence of 7 base pairs with the following indices
    found in the reference in the natural order, ie

    1 2 3 4 5 6 7

    then, after being *pi-shifted* the base pairs in the sequence are
    reordered, and the indices become (in parenthesis the former
    indices):

    1'(=4) 2'(=5) 3'(=6) 4'(=7) 5'(=1) 6'(=2) 7'(=3)

    The current function accepts *primed* indices and transforms them to
    the *unprimed* indices, ie, the positions returned refer to the
    original reference.
    """
    shift = nbp//2
    if pos <= (nbp-shift):
        pos += shift
    else:
        pos -= (nbp-shift)
    return pos


def pishift_back_positions_in_gff(gff_path: Union[str, Path]) -> None:
    """A function that parses the input GFF file (assumed to be a valid
    `GFF3`_ file) and *shifts back* the positions found in it (columns
    4th and 5th of lines not starting by ``#``).
    It is assumed that the positions in the input file (``gff_path``)
    are referring to a *pi-shifted* origin.
    To undo the shift, the length of the sequence(s) is (are) read
    from the *GFF3 directives* (lines starting by ``##``), in
    particular from the ``##sequence-region`` *pragmas*.
    This function can handle the case of multiple sequences.

    Warning! The function overwrites the input ``gff_path``.

    .. GFF3: https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md
    """
    with open(gff_path) as ingff:
        inlines = ingff.readlines()
    outlines = []
    seq_lens = {}
    for line in inlines:
        if line.startswith("##sequence-region"):
            _, name, seq_num, seq_len = line.strip().split()
            N = int(seq_len)
            seq_lens[name] = N
        else:
            pieces = line.split("\t")
            name = pieces[0]
            if name in seq_lens:
                N = seq_lens[name]
                positions = [int(_) for _ in pieces[3:5]]
                new_positions = [str(shift_me_back(_, N)) for _ in positions]
                line = "\t".join(
                    pieces[:3]+new_positions+pieces[5:]
                )
        outlines.append(line)
    with open(gff_path, "w") as outgff:
        for line in outlines:
            outgff.write(line)


def try_computations_with_variants_until_done(
        func: Callable, variants: Sequence[str], *args: Any) -> None:
    """This function runs the passed in function ``func`` with the
    arguments``*args`` and for each ``variant`` in ``variants``,eg.
    something like this::

    for v in variants:
        result = func(*args, variant=v)

    but it keeps doing so until each result returned by ``func`` is not
    ``None``. When a ``None`` is returned by ``func``, a call to ``sleep``
    is warranted before continuing. The time slept depends on how many
    times it was sleeping before; the sleep time grows exponentially
    with every iteration::

      t -> 2*t

    until all the computations (results of ``func`` for each variant)
    are completed, ie all are not ``None``.
    The main application of this function is to ensure that some common
    operations of the ``SingleMoleculeAnalysis`` are done once and only
    once irrespective of how many parallel instances of the analysis
    (with different partitions each) are carried out. For example, this
    function can be used to avoid collisions in the generation of aligned
    BAM files since :py:class:`pacbio_data_processing.blasr.Blasr` has a
    mechanism that allows concurrent computations.
    This function delegates the decision on whether the computation is
    done or not to ``func``.

    .. note::

       A special case is when a ``variant`` is ``None``, in that case
       the function ``func`` is called without the ``variant`` argument::

      result = func(*args)

      Therefore, if ``variants`` is, e.g. ``(None,)``, then ``func`` is
      only called once in each iteration WITHOUT ``variant`` keyword
      argument. That is useful if the function ``func`` must be called
      until is done, but it takes no variant argument.
    """
    computations = {variant: None for variant in variants}
    wait_time_seconds = WAIT_TIME_SECONDS
    already_run = False
    while None in set(computations.values()):
        for variant in variants:
            if computations[variant] is None:
                if variant is None:
                    kwargs = {}
                else:
                    kwargs = {"variant": variant}
                result = func(*args, **kwargs)
                computations[variant] = result
        if already_run or (None in set(computations.values())):
            time.sleep(wait_time_seconds)
            wait_time_seconds *= NEXT_WAIT_TIME_FACTOR
        else:
            already_run = True


class AlmostUUID:
    """A class that provides a 5 letters summary of a UUID.
    It is intended to be used as prefix in all log message.
    It is not necessary that two instances are different. But it is
    necessary that:

    1. the string representation is short, and
    2. given two instances their string representations most
       *probably differ*.

    The underlying UUID is obtained from the stdlib using
    ``uuid.uuid1``.
    The class is implemented using the Borg pattern: all instances
    running in the same interpreter share a common ``_uuid`` attribute.
    """
    _uuid = None

    def __init__(self) -> None:
        if self.__class__._uuid is None:
            self.__class__._uuid = uuid1()

    @cached_property
    def _short_str(self) -> str:
        return "".join([_[-1] for _ in str(self._uuid).split("-")])

    def __str__(self) -> str:
        return self._short_str
