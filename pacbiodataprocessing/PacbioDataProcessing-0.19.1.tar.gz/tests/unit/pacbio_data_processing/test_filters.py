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
from unittest.mock import patch, PropertyMock, call, MagicMock
from collections import deque, namedtuple
import itertools

from pacbio_data_processing.filters import (
    filter_seq_len, filter_enough_data_per_molecule, empty_buffer,
    filter_quality, filter_mappings_binary, filter_mappings_ratio,
    cleanup_molecules
)
from pacbio_data_processing.bam_utils import Molecule
from pacbio_data_processing.constants import (
    DNA_SEQ_COLUMN, QUALITY_COLUMN, STANDARD_MIN_QUAL, STANDARD_MIN_DNA_LEN,
    STANDARD_MAPPINGS_RATIO, STANDARD_MIN_NUM_SUBREADS,
    STANDARD_ACCEPTED_MAPPINGS,
)


def make_BamLine(ncols, mol_col):
    attrs = [f"a{_}" for _ in range(ncols)]
    attrs[mol_col] = "zmw"

    class BamLine(namedtuple("BamLine", attrs)):
        @property
        def molecule_id(self):
            return self.zmw.split(b":")[-1]

        @property
        def flag(self) -> int:
            return int(self[1])

    return BamLine


class FilterSeqLenTestCase(unittest.TestCase):
    def setUp(self):
        data = []
        for num in range(20, 30, 5):
            for i in range(3):
                data.append(
                    tuple("x" for _ in range(DNA_SEQ_COLUMN))+("a"*num,)
                )
        self.data = data

    def test_all_passes(self):
        out_data = list(filter_seq_len(self.data, 19))
        self.assertEqual(self.data, out_data)

    def test_all_refused(self):
        out_data = list(filter_seq_len(self.data, 35))
        self.assertEqual([], out_data)

    def test_half_passes(self):
        out_data = list(filter_seq_len(self.data, 23))
        self.assertEqual(self.data[3:], out_data)


class FilterEnoughDataPerMoleculeTestCase(unittest.TestCase):
    def test_all_lines_with_equal_chosen_column(self):
        BamLine = make_BamLine(10, 8)
        indata = []
        for r in range(20):
            item = [str(i+r) for i in range(10)]
            item[8] = b"zm:i:x"
            if r % 2:
                flag = b"0"
            else:
                flag = b"16"
            item[1] = flag
            indata.append(BamLine(*item))
        self.assertEqual(
            indata,
            list(filter_enough_data_per_molecule(indata, 10))
        )

    def test_half_lines_with_equal_chosen_column(self):
        BamLine = make_BamLine(10, 3)
        indata = []
        for r in range(20):
            item = [str(i+r) for i in range(10)]
            if r < 10:
                new = b"zm:i:x"
            else:
                new = b"zm:i:y"
            item[3] = new
            if r % 2:
                flag = b"0"
            else:
                flag = b"16"
            item[1] = flag
            indata.append(BamLine(*item))
        self.assertEqual(
            indata,
            list(filter_enough_data_per_molecule(indata, 10))
        )

    def test_mixed_shorter_seqs_dont_pass(self):
        BamLine = make_BamLine(10, 7)
        indata = []
        for r in range(20):
            item = [str(i+r) for i in range(10)]
            if r < 5 or (r >= 10 and r < 15):
                new = b"zm:i:x"
            else:
                new = b"zm:i:y"
            item[7] = new
            indata.append(BamLine(*item))
        self.assertEqual(
            [],
            list(filter_enough_data_per_molecule(indata, 10))
        )

    def test_only_long_enough_seq_passes(self):
        BamLine = make_BamLine(10, 2)
        indata = []
        for r in range(20):
            item = [str(i+r) for i in range(10)]
            if r > 4 and r < 18:
                new = b"zm:i:x"
            else:
                new = b"zm:i:y"
            item[2] = new
            if r % 2:
                flag = b"0"
            else:
                flag = b"16"
            item[1] = flag
            indata.append(BamLine(*item))
        self.assertEqual(
            indata[5:18],
            list(filter_enough_data_per_molecule(indata, 10))
        )

    def test_mols_with_data_in_both_strand_passes(self):
        ncols = 10
        BamLine = make_BamLine(ncols, 3)
        indata = []
        for r in range(20):
            item = [str(i+r) for i in range(ncols)]
            if r % 2:
                flag = b"0"
            else:
                flag = b"16"
            item[1] = flag
            item[3] = b"xm:i:100"
            indata.append(BamLine(*item))
        self.assertEqual(
            indata, list(filter_enough_data_per_molecule(indata, 20))
        )

    def test_mols_with_data_in_only_one_strand_doesnt_pass(self):
        ncols = 10
        BamLine = make_BamLine(ncols, 3)
        for f0, f1 in [(b"0", b"16"), (b"16", b"0")]:
            indata = []
            for r in range(20):
                item = [str(i+r) for i in range(ncols)]
                item[1] = f0
                item[3] = b"xm:i:100"
                indata.append(BamLine(*item))
            self.assertEqual(
                [], list(filter_enough_data_per_molecule(indata, 10))
            )
            item = [str(i+20) for i in range(ncols)]
            item[1] = f1
            item[3] = b"xm:i:100"
            indata.append(BamLine(*item))
            self.assertEqual(
                indata, list(filter_enough_data_per_molecule(indata, 10))
            )

    def test_empty_buffer_with_no_data(self):
        self.assertEqual(list(empty_buffer([], 23, {"+", "-"})), [])

    def test_empty_buffer_with_enough_data(self):
        data = deque(range(10))
        self.assertEqual(list(data), list(empty_buffer(data, 9, {"+", "-"})))
        self.assertEqual(len(data), 0)

    def test_empty_buffer_with_not_enough_data(self):
        data = deque(range(10))
        self.assertEqual([], list(empty_buffer(data, 11, {"+", "-"})))
        self.assertEqual(len(data), 0)


class FilterQualityThresholdTestCase(unittest.TestCase):
    def test_all_lines_taken_if_th_low_enough(self):
        indata = []
        for r in range(20):
            item = [str(i+r) for i in range(10)]
            item[QUALITY_COLUMN] = "50"
            indata.append(item)
        self.assertEqual(indata, list(filter_quality(indata, 49)))

    def test_no_lines_taken_if_th_too_high(self):
        indata = []
        for r in range(20):
            item = [str(i+r) for i in range(10)]
            item[QUALITY_COLUMN] = "49"
            indata.append(item)
        self.assertEqual([], list(filter_quality(indata, 50)))

    def test_only_taken_lines_with_high_enough_quality(self):
        indata = []
        for r in range(20):
            item = [str(i+r) for i in range(10)]
            if r % 2:
                item[QUALITY_COLUMN] = "50"
            indata.append(item)
        self.assertEqual(
            [_ for _ in indata if _[QUALITY_COLUMN] == "50"],
            list(filter_quality(indata, 40))
        )


class FilterMappingsBinaryTestCase(unittest.TestCase):
    def test_all_passes_if_no_mappings_given(self):
        indata = []
        for r in range(20):
            item = [str(i+r).encode() for i in range(10)]
            indata.append(item)
        self.assertEqual(indata, list(filter_mappings_binary(indata, None)))

    def test_only_takes_whats_asked(self):
        indata = []
        for r in range(20):
            item = [str(i+r).encode() for i in range(10)]
            indata.append(item)
        self.assertEqual(
            [list(str(_).encode() for _ in range(1, 11))],
            list(filter_mappings_binary(indata, ("2",)))
        )
        self.assertEqual(
            [list(str(_+j).encode() for _ in range(10)) for j in (2, 4, 6)],
            list(filter_mappings_binary(indata, ("3", "5", "7")))
        )

    def test_accepts_third_param_to_meet_API(self):
        filter_mappings_binary([], None, 0)


TEST_LINES_1 = [
    [b"first", b"0"]+[b"x" for _ in range(22)]+[b"zm:i:15"] for _ in range(10)
]

TEST_LINES_2 = [
    [b"first", b"1"]+[b"x" for _ in range(22)]+[b"zm:i:15"] for _ in range(10)
]

TEST_LINES_3 = [
    [b"first", b"2"]+[b"x" for _ in range(22)]+[b"zm:i:15"] for _ in range(10)
]


class FilterMappingRatioTestCase(unittest.TestCase):
    def setUp(self):
        self.BamLine = make_BamLine(25, 24)

    def test_yields_all_items_if_all_mappings_match(self):
        test_lines = (
            [self.BamLine(*_) for _ in TEST_LINES_1],
            [self.BamLine(*_) for _ in TEST_LINES_2],
            [self.BamLine(*_) for _ in TEST_LINES_1+TEST_LINES_2]
        )
        test_mappings = (["0"], ["1"], ["0", "1"])
        expected = test_lines
        for input_lines, mappings, wished_result in zip(
                test_lines, test_mappings, expected):
            with self.subTest(
                    lines=input_lines, mappings=mappings,
                    expect=wished_result):
                lines = filter_mappings_ratio(input_lines, mappings, 1)
                self.assertEqual(list(lines), wished_result)

    def test_yields_no_items_if_mappings_do_not_match(self):
        lines = filter_mappings_ratio(
            [self.BamLine(*_) for _ in TEST_LINES_1], ["1"], 1)
        self.assertEqual(list(lines), [])

    def test_yields_all_items_with_matching_mappings_if_enough_ratio(self):
        ratios = 0.3, 0.2, 0.1
        test_lines = [
            self.BamLine(*_) for _ in TEST_LINES_1+TEST_LINES_2+TEST_LINES_3]
        for ratio in ratios:
            with self.subTest(ratio=ratio):
                lines = filter_mappings_ratio(test_lines, ["1"], ratio)
                self.assertEqual(list(lines), test_lines)

    def test_yields_items_after_ratio_threshold(self):
        ratios = 0.8, 0.3, 0.9
        test_lines = [
            self.BamLine(*_) for _ in 4*TEST_LINES_1+TEST_LINES_2+TEST_LINES_1]
        test_mappings = (
            ["0"],
            ["0", "16"],
        )
        all_expected = (
            test_lines, test_lines, test_lines, test_lines, [], []
        )
        for (ratio, mappings), expected in zip(
                itertools.product(ratios, test_mappings), all_expected):
            with self.subTest(mappings=mappings, ratio=ratio):
                lines = filter_mappings_ratio(test_lines, mappings, ratio)
                self.assertEqual(list(lines), expected)


@patch("pacbio_data_processing.filters.filter_enough_data_per_molecule")
@patch("pacbio_data_processing.filters.filter_mappings_binary")
@patch("pacbio_data_processing.filters.filter_mappings_ratio")
@patch("pacbio_data_processing.filters.filter_quality")
@patch("pacbio_data_processing.filters.filter_seq_len")
@patch("pacbio_data_processing.filters.BamFile")
class CleanUpMoleculesTestCase(unittest.TestCase):
    def test_operations(
            self, pBamFile, pfilter_seq_len, pfilter_quality,
            pfilter_mappings_ratio, pfilter_mappings_binary,
            pfilter_enough_data_per_molecule):
        molecules = (
            (112, Molecule(112, "a.bam")),
        )
        lines_fn = iter((1, 2))
        pfilter_enough_data_per_molecule.return_value = lines_fn
        fake_bams = {"r": MagicMock(), "w": MagicMock()}
        def side_effect(*args, **kwargs):
            mode = kwargs.get("mode")
            if mode == "w":
                return fake_bams["w"]
            return fake_bams["r"]
        pBamFile.side_effect = side_effect
        res = tuple(cleanup_molecules(iter(molecules)))
        pBamFile.assert_has_calls(
            [call(molecules[0][1].src_bam_path),
                 call(molecules[0][1].src_bam_path, mode="w")],
            any_order=True
        )
        fake_bams["w"].write.assert_called_once_with(
            header=fake_bams["r"].header,
            body=[1, 2]
        )
        pfilter_seq_len.assert_called_once_with(
            fake_bams["r"].body, STANDARD_MIN_DNA_LEN)
        pfilter_quality.assert_called_once_with(
            pfilter_seq_len.return_value, STANDARD_MIN_QUAL)
        pfilter_mappings_ratio.assert_called_once_with(
            pfilter_quality.return_value, STANDARD_ACCEPTED_MAPPINGS,
            STANDARD_MAPPINGS_RATIO)
        pfilter_mappings_binary.assert_called_once_with(
            pfilter_mappings_ratio.return_value, STANDARD_ACCEPTED_MAPPINGS)
        pfilter_enough_data_per_molecule.assert_called_once_with(
            pfilter_mappings_binary.return_value, STANDARD_MIN_NUM_SUBREADS)
        self.assertEqual(res, molecules)

    def test_discard_filenames_that_dont_pass_all_filters(
            self, pBamFile, pfilter_seq_len, pfilter_quality,
            pfilter_mappings_ratio, pfilter_mappings_binary,
            pfilter_enough_data_per_molecule):
        molecules = (
            (1, Molecule(1, "a.bam")),
            (2, Molecule(2, "2.bam")),
            (4, Molecule(4, "3.bam"))
        )
        lines_fn = (iter((1, 2)), iter(()), iter((3, 4)))
        pfilter_enough_data_per_molecule.side_effect = lines_fn
        res = tuple(cleanup_molecules(iter(molecules)))
        self.assertEqual(
            res, (
                (1, Molecule(1, "a.bam")),
                (4, Molecule(4, "3.bam"))
            )
        )
        # pBamFile.return_value.write.assert_has_calls(
        #     ...
        # )

    def test_logs_msg_with_result(
            self, pBamFile, pfilter_seq_len, pfilter_quality,
            pfilter_mappings_ratio, pfilter_mappings_binary,
            pfilter_enough_data_per_molecule):
        molecules = (
            (256, Molecule(256, "good.bam")),
            (332, Molecule(332, "bad.bam"))
        )
        lines_fn = (iter((1, 2)), iter(()))
        pall_molecules = PropertyMock()
        pall_molecules.side_effect = (iter([b"256"]), iter([b"332"]))
        type(pBamFile.return_value).all_molecules = pall_molecules
        pfilter_enough_data_per_molecule.side_effect = lines_fn
        with self.assertLogs(level="DEBUG") as cm:
            res = tuple(cleanup_molecules(iter(molecules)))
        self.assertEqual(
            cm.output,
            ["DEBUG:root:[filter]  Molecule '332' rejected"]
        )
