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

import unittest

from pacbio_data_processing.cigar import Cigar


class CigarTestCase(unittest.TestCase):
    def setUp(self):
        self.cigars = (
            "23=", "9=1I57=1I8=1I103=",
            "16=1X55=1X3=1X2=1X16=1X2=1D72=", "198=3S"
        )
        self.expected_lists = (
            ["23="],
            ["9=", "1I", "57=", "1I", "8=", "1I", "103="],
            ["16=", "1X", "55=", "1X", "3=", "1X", "2=", "1X",
             "16=", "1X", "2=", "1D", "72="],
            ["198=", "3S"],
        )
        self.expected_lens = (1, 7, 13, 2)
        self.number_pb_diffs = (0, 3, 6, 3)
        self.number_diff_items = (0, 3, 6, 1)
        self.number_diff_types = (0, 1, 2, 1)
        self.number_pbs = (23, 180, 171, 201)
        self.diff_ratios = (0, 3/180, 6/171, 3/201)

    def test_is_iterable(self):
        for incigar, expected_list in zip(self.cigars, self.expected_lists):
            cigar = Cigar(incigar)
            self.assertEqual(list(cigar), expected_list)

    def test_has_len(self):
        for incigar, expected_len in zip(self.cigars, self.expected_lens):
            cigar = Cigar(incigar)
            self.assertEqual(len(cigar), expected_len)

    def test_number_pb_diffs(self):
        for incigar, expected_pb_diffs in zip(
                self.cigars, self.number_pb_diffs):
            cigar = Cigar(incigar)
            self.assertEqual(cigar.number_pb_diffs, expected_pb_diffs)

    def test_number_diff_items(self):
        for incigar, expected in zip(self.cigars, self.number_diff_items):
            cigar = Cigar(incigar)
            self.assertEqual(cigar.number_diff_items, expected)

    def test_number_diff_types(self):
        for incigar, expected in zip(self.cigars, self.number_diff_types):
            cigar = Cigar(incigar)
            self.assertEqual(cigar.number_diff_types, expected)

    def test_number_pbs(self):
        for incigar, expected in zip(self.cigars, self.number_pbs):
            cigar = Cigar(incigar)
            self.assertEqual(cigar.number_pbs, expected)

    def test_diff_ratio(self):
        for incigar, expected in zip(self.cigars, self.diff_ratios):
            cigar = Cigar(incigar)
            self.assertEqual(cigar.diff_ratio, expected)

    def test_sim_ratio(self):
        for incigar, expected in zip(self.cigars, self.diff_ratios):
            cigar = Cigar(incigar)
            self.assertEqual(cigar.sim_ratio, 1-expected)

    def test_repr(self):
        for incigar in self.cigars:
            expected = f"Cigar('{incigar}')"
            cigar = Cigar(incigar)
            self.assertEqual(repr(cigar), expected)

    def test_equality(self):
        a = Cigar("8=4S")
        b = Cigar("8=4S")
        c = Cigar("12=")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
