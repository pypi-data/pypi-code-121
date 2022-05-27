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

import unittest
from unittest.mock import patch, mock_open, call, MagicMock
from uuid import UUID

import Bio.SeqRecord

from pacbio_data_processing.utils import (
    DNASeq, Partition, pishift_back_positions_in_gff,
    try_computations_with_variants_until_done, AlmostUUID
)
from pacbio_data_processing.constants import (
    WAIT_TIME_SECONDS, NEXT_WAIT_TIME_FACTOR
)


class DNASeqTestCase(unittest.TestCase):
    def test_comparable_for_equality(self):
        a = DNASeq("AATT")
        b = DNASeq("GATTTCA")
        c = DNASeq("AATT")
        d = DNASeq("GAttTCA")
        self.assertEqual(a, c)
        self.assertNotEqual(a, b)
        self.assertEqual(b, d)

    def test_comparable_with_strs(self):
        a = DNASeq("GAttTCA")
        b = DNASeq("GAttTCT")
        s = "GATTTCA"
        self.assertEqual(s, a)
        self.assertEqual(a, s)
        self.assertFalse(a != s)
        self.assertFalse(s != a)
        self.assertNotEqual(s, b)

    def test_slicing(self):
        a = DNASeq("GATACA")
        b = DNASeq("AAGATACACC")
        self.assertEqual(b[2:-2], a)

    def test_len(self):
        self.assertEqual(len(DNASeq("GATC")), 4)
        self.assertEqual(len(DNASeq("AAGATC")), 6)

    def test_default_fasta_name(self):
        a = DNASeq("A")
        self.assertEqual(a.fasta_name, None)

    @patch("pacbio_data_processing.utils.Bio.SeqIO.parse")
    def test_from_fasta(self, pparse):
        a = DNASeq("GTACA")
        srec = Bio.SeqRecord.SeqRecord(
            "GTACA", name="abg", description="long story short")
        pparse.return_value = iter([srec])
        b = DNASeq.from_fasta("my.fasta")
        self.assertEqual(b, a)
        self.assertEqual(b.name, "abg")
        self.assertEqual(b.description, "long story short")
        self.assertEqual(b.fasta_name, "my.fasta")
        pparse.assert_called_once_with("my.fasta", "fasta")

    def test_pi_shifted(self):
        raw_seqs = ["GTACATCGATTTCA", "GTACATCGATTTCAG"]
        shifted_seqs = ["GATTTCAGTACATC", "GATTTCAGGTACATC"]
        for s, shifted in zip(raw_seqs, shifted_seqs):
            a = DNASeq(s, name="c", description="long story")
            pi_a = a.pi_shifted()
            self.assertEqual(pi_a, shifted)
            self.assertEqual(pi_a.name, a.name)
            self.assertEqual(pi_a.description, a.description+" (pi-shifted)")

    @patch("pacbio_data_processing.utils.Faidx")
    @patch("pacbio_data_processing.utils.Bio.SeqIO.write")
    @patch("pacbio_data_processing.utils.SeqRecord")
    def test_write_fasta(self, pSeqRecord, pwrite, pFaidx):
        s = DNASeq("AACCGGG", name="FDR5", description="all you can eat")
        s.write_fasta("another.fasta")
        pSeqRecord.assert_called_once_with(
            s._seq, id="FDR5", description="all you can eat")
        pwrite.assert_called_once_with(
            [pSeqRecord.return_value], "another.fasta", "fasta"
        )
        pFaidx.assert_called_once_with("another.fasta")

    def test_name_and_description(self):
        s = DNASeq("AACCGGG", name="uyh", description="hello, it's me")
        self.assertEqual(s.name, "uyh")
        self.assertEqual(s.description, "hello, it's me")

    def test_md5sum(self):
        S = DNASeq("AACCGTG")
        s = DNASeq("aaccgtg")
        self.assertEqual(S.md5sum, "a51924da94d51a87df5d56f46a10a9cb")
        self.assertEqual(s.md5sum, S.md5sum)

    def test_count(self):
        a = DNASeq("GATACAGATCCGGAATGATCGATT")
        self.assertEqual(a.count("GATC"), 2)
        self.assertEqual(a.count("GAT"), 4)
        self.assertEqual(a.count("A"), 8)


class PartitionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mols_in_bam = (
            b"23", b"299", b"302", b"424",
            b"599", b"1920", b"2242",
        )

        class BamFile:
            num_molecules = 7
            _all_molecules = cls.mols_in_bam

            @property
            def all_molecules(self):
                return iter(self._all_molecules)

        cls.bam = BamFile()

    def test_full_partition_contains_any_molecule(self):
        pall = [Partition(_, self.bam) for _ in (None, (1, 1))]
        mols_not_in_bam = (b"123", b"1", b"2223", b"1928475")
        mols = self.mols_in_bam + mols_not_in_bam
        for mol in mols:
            for p in pall:
                self.assertTrue(mol in p)

    def test_non_trivial_partitions(self):
        partitions = [(1, 3), (3, 3), (3, 4), (4, 4)]
        expected_mols = [
            {b"5", b"23", b"299", b"301"},
            {b"599", b"1920", b"2242", b"3000"},
            {b"302", b"423"},
            {b"424", b"599", b"600", b"1920", b"2242", b"5000"}
        ]
        unexpected_molecules = [
            {b"302", b"10040"},
            {b"5", b"598"},
            {b"301", b"424"},
            {b"1", b"423"}
        ]
        for partition, inmols, outmols in zip(
                partitions, expected_mols, unexpected_molecules):
            p = Partition(partition, self.bam)
            for mol in inmols:
                self.assertTrue(mol in p)
            for mol in outmols:
                self.assertFalse(mol in p)


class PiShiftBackPositionsInGFFTestCase(unittest.TestCase):
    def setUp(self):
        self.in_lines_in_gff = [
            '##gff-version 3\n',
            '##source ipdSummary v2.0\n',
            '##source-commandline ipdSummary ...\n',
            '##sequence-region wwrd 1 193\n',
            ('wwrd\tkinModCall\tmodified_base\t1\t1\t24\t+\t.\t'
             'coverage=33;context=GCCTCACAACAGCCCAAACGCGTCGTCAAAGACGGCCCCAA'
             ';IPDRatio=1.85\n'),
            ('wwrd\tkinModCall\tmodified_base\t193\t193\t27\t+\t.\t'
             'coverage=30;context=TCTTCATCTACTCCAAATAGTGGTAGTTCCGTTGCGGCTAT'
             ';IPDRatio=2.24\n'),
            ('wwrd\tkinModCall\tmodified_base\t97\t97\t26\t+\t.\t'
             'coverage=29;context=GGCTATGTGGCCGCCTCTTCCTATGCCATCACACGGTGGCG'
             ';IPDRatio=2.07\n'),
            ('wwrd\tkinModCall\tmodified_base\t98\t98\t25\t-\t.\t'
             'coverage=32;context=CATTCGTGGGTAGGAATCAACGGTAGAATTAGTTTAGAGAT'
             ';IPDRatio=1.93\n')
        ]
        self.out_lines_in_gff = [
            '##gff-version 3\n',
            '##source ipdSummary v2.0\n',
            '##source-commandline ipdSummary ...\n',
            '##sequence-region wwrd 1 193\n',
            ('wwrd\tkinModCall\tmodified_base\t97\t97\t24\t+\t.\t'
             'coverage=33;context=GCCTCACAACAGCCCAAACGCGTCGTCAAAGACGGCCCCAA'
             ';IPDRatio=1.85\n'),
            ('wwrd\tkinModCall\tmodified_base\t96\t96\t27\t+\t.\t'
             'coverage=30;context=TCTTCATCTACTCCAAATAGTGGTAGTTCCGTTGCGGCTAT'
             ';IPDRatio=2.24\n'),
            ('wwrd\tkinModCall\tmodified_base\t193\t193\t26\t+\t.\t'
             'coverage=29;context=GGCTATGTGGCCGCCTCTTCCTATGCCATCACACGGTGGCG'
             ';IPDRatio=2.07\n'),
            ('wwrd\tkinModCall\tmodified_base\t1\t1\t25\t-\t.\t'
             'coverage=32;context=CATTCGTGGGTAGGAATCAACGGTAGAATTAGTTTAGAGAT'
             ';IPDRatio=1.93\n')
        ]

    def test_file_correctly_shifted(self):
        mopen = mock_open(read_data="".join(self.in_lines_in_gff))
        with patch("pacbio_data_processing.utils.open", mopen):
            pishift_back_positions_in_gff("my.gff")
        mopen.assert_has_calls(
            [call().write(_) for _ in self.out_lines_in_gff]
        )


@patch("pacbio_data_processing.utils.time.sleep")
class TryComputationsWithVariantsUntilDoneTestCase(unittest.TestCase):
    def test_computations_ok_the_first_time(self, psleep):
        func = MagicMock()
        func.return_value = 0
        variants = ("a", "b", "j")
        args = (8, None, ["--"])
        try_computations_with_variants_until_done(func, variants, *args)
        func.assert_has_calls(
            [call(*args, variant=_) for _ in variants]
        )
        psleep.assert_not_called()

    def test_computations_repeated_until_done(self, psleep):
        func = MagicMock()
        results = {
            "a": [None, 0],
            "b": [None]*7+[0],
        }
        result_gens = {k: iter(v) for k, v in results.items()}

        def results_func(*args, variant):
            gen = result_gens[variant]
            return next(gen)
        func.side_effect = results_func
        variants = ("a", "b")
        args = (8, None, ["--"])
        try_computations_with_variants_until_done(func, variants, *args)
        func.assert_has_calls(
            [call(*args, variant=v) for v in variants]*2
            + [call(*args, variant="b") for _ in range(6)]
        )
        psleep.assert_has_calls(
            [call(WAIT_TIME_SECONDS*NEXT_WAIT_TIME_FACTOR**i)
                for i in range(7)]
        )

    def test_no_variants(self, psleep):
        func = MagicMock()
        results = (None, 0)
        func.side_effect = results
        variants = (None,)
        args = (45, "aa")
        try_computations_with_variants_until_done(func, variants, *args)
        func.assert_has_calls([call(*args)]*2)
        psleep.assert_called_once_with(WAIT_TIME_SECONDS)


class AlmostUUIDTestCase(unittest.TestCase):
    def test_has_short_str_representation(self):
        uid = AlmostUUID()
        self.assertEqual(len(str(uid)), 5)
        self.assertLessEqual(set(str(uid)), set("0123456789abcdef"))

    def test_two_instances_have_same_str_representation(self):
        uid1 = AlmostUUID()
        uid2 = AlmostUUID()
        self.assertEqual(str(uid1), str(uid2))

    @patch("pacbio_data_processing.utils.uuid1")
    def test_comes_from_uuid1(self, puuid1):
        AlmostUUID._uuid = None
        puuid1.return_value = UUID('61fc3662-c488-11ec-af8b-ccf9e482fc17')
        uid = AlmostUUID()
        self.assertEqual(str(uid), "28cb7")
