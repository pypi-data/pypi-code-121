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

import unittest
from unittest.mock import patch, call, PropertyMock, MagicMock, mock_open
from subprocess import PIPE

from pacbio_data_processing.bam import (
    _BamFileSamtools, _BamFilePysam, BamFile, pack_lines, set_pysam_verbosity,
)
from pacbio_data_processing.constants import (
    SAMTOOLS_GET_HEADER, SAMTOOLS_GET_BODY, SAMTOOLS_WRITE_BAM,
)


class _BamFileSamtoolsTestCase(unittest.TestCase):
    @patch("pacbio_data_processing.bam.subprocess.run")
    def test_read_header(self, prun):
        in_bam_file = "something"
        b = _BamFileSamtools(in_bam_file)
        header = b._read_header()
        prun.assert_called_once_with(
            SAMTOOLS_GET_HEADER+(in_bam_file,), capture_output=True)
        self.assertEqual(header, prun.return_value.stdout)

    @patch("pacbio_data_processing.bam.subprocess.Popen")
    def test_read_body(self, pPopen):
        data = [
            ["a", "2", "++-+"],
            ["vion", "22", "*"],
            ["jj/", "112509", "--"],
        ]
        pPopen.return_value.stdout = iter(" ".join(_) for _ in data)
        b = _BamFileSamtools("a file")
        body = b._read_body()
        for actual, expected in zip(body, data):
            self.assertEqual(tuple(actual), tuple(expected))
        pPopen.assert_called_once_with(
            SAMTOOLS_GET_BODY+("a file",), stdout=PIPE)

    @patch("pacbio_data_processing.bam.open")
    @patch("pacbio_data_processing.bam.subprocess.Popen")
    def test_write(self, pPopen, popen):
        # This is a very ugly test. It is strongly coupled to the
        # implementation
        # Alternatively, I could have played with files created by samtools.
        # But I think it would have led me to write a similarly ugly test.
        #
        # The way this test is written now allows me to use Popen
        # in the implementation as a context manager or simply calling
        # it and calling close in the end.
        pPopen.return_value.__enter__.return_value = pPopen.return_value
        header = b"ff @a x [8,9]"
        data = [
            [b"a", b"2", b"++-+"],
            [b"vion", b"22", b"*"],
            [b"jj/", b"112509", b"--"],
        ]
        body_gen = iter(b"\t".join(_)+b"\n" for _ in data)
        expected_calls = [call(header)]+[call(_) for _ in body_gen]
        b = _BamFileSamtools("a file")  # , mode="w")
        b._write(header=header, body=data)
        popen.assert_called_once_with("a file", "wb")
        file_output = popen().__enter__.return_value
        pPopen.assert_called_once_with(
            SAMTOOLS_WRITE_BAM, stdin=PIPE, stdout=file_output)
        pPopen.return_value.stdin.write.assert_has_calls(expected_calls)
        try:
            pPopen.return_value.stdin.close.assert_called_once_with()
        except AssertionError:
            pPopen.return_value.__exit__.assert_called_once_with(
                None, None, None)


class _BamFilePysamTestCase(unittest.TestCase):
    @patch("pacbio_data_processing.bam.pysam.AlignmentFile")
    def test_ralignment_file(self, pAlignmentFile):
        in_bam = "something"
        b = _BamFilePysam(in_bam)
        self.assertEqual(b._ralignment_file, pAlignmentFile.return_value)
        pAlignmentFile.assert_called_once_with(in_bam, "rb", check_sq=False)

    @patch("pacbio_data_processing.bam.pysam.AlignmentFile")
    def test_read_header(self, pAlignmentFile):
        in_bam = "something"
        b = _BamFilePysam(in_bam)
        header = b._read_header()
        pAlignmentFile.assert_called_once_with(in_bam, "rb", check_sq=False)
        self.assertEqual(
            header,
            str(pAlignmentFile.return_value.header).encode()
        )

    @patch("pacbio_data_processing.bam.pysam.AlignmentFile")
    def test_read_body(self, pAlignmentFile):
        data = [
            ["a", "2", "*0"],
            ["vion", "22", "*"],
            ["jj/", "112609", "--"],
        ]
        mocked_data = [
            MagicMock() for _ in data
        ]
        for md, d in zip(mocked_data, data):
            md.to_string.return_value = " ".join(d)
        pAlignmentFile.return_value = iter(mocked_data)
        b = _BamFilePysam("a file")
        body = list(b._read_body())
        # to ensure that we actually loop later, ie, that there is data:
        # self.assertEqual(len(body), len(data))
        for actual, expected in zip(body, data):
            self.assertEqual(
                tuple(actual),
                tuple(_.encode() for _ in expected)
            )

    @patch("pacbio_data_processing.bam.pysam.AlignmentHeader")
    @patch("pacbio_data_processing.bam.pysam.AlignedSegment")
    @patch("pacbio_data_processing.bam.pysam.AlignmentFile")
    def test_write(self, pAlignmentFile, pAlignedSegment, pAlignmentHeader):
        # This is a very ugly test. It is strongly coupled to the
        # implementation
        # Alternatively, I could have played with files created by samtools.
        # But I think it would have led me to write a similarly ugly test.
        #
        # The way this test is written now allows me to use Popen
        # in the implementation as a context manager or simply calling
        # it and calling close in the end.
        pAlignmentFile.return_value.__enter__.return_value = (
            pAlignmentFile.return_value)
        bheader = b"this is a fake header\n\n"
        header = pAlignmentHeader.from_text.return_value
        data = [
            [b"a", b"2", b"++-+"],
            [b"vion", b"22", b"*"],
            [b"jj/", b"112509", b"--"],
        ]
        data2write = iter((b"\t".join(_)).decode() for _ in data)
        def paligned_segments_factory(item, header):
            for idata in data:
                packed = (b"\t".join(idata)).decode()
                if item == packed:
                    break
            else:
                raise ValueError
            return packed

        pAlignedSegment.fromstring.side_effect = paligned_segments_factory
        expected_calls = [call(_) for _ in data2write]
        b = _BamFilePysam("a file")
        b._write(header=bheader, body=data)
        pAlignmentHeader.from_text.assert_called_once_with(
            bheader.decode().rstrip()+"\n")
        pAlignmentFile.assert_called_once_with(
            "a file", "wb", header=header)
        pAlignmentFile.return_value.write.assert_has_calls(expected_calls)
        try:
            pAlignmentFile.return_value.close.assert_called_once_with()
        except AssertionError:
            pAlignmentFile.return_value.__exit__.assert_called_once_with(
                None, None, None)

    @patch("pacbio_data_processing.bam.set_pysam_verbosity")
    def test__set_pysam_verbosity_makes_call_and_sets_attr_if_needed(
            self, pset_verbosity):
        self.assertFalse(_BamFilePysam._PYSAM_VERBOSITY_SET)
        b = _BamFilePysam("j")
        pset_verbosity.assert_called_once_with()
        self.assertTrue(_BamFilePysam._PYSAM_VERBOSITY_SET)

    @patch("pacbio_data_processing.bam.set_pysam_verbosity")
    def test__set_pysam_verbosity_makes_no_call_if_another_instance_created(
            self, pset_verbosity):
        b = _BamFilePysam("j")
        pset_verbosity.reset_mock()
        c = _BamFilePysam("jh")
        pset_verbosity.assert_not_called()
        self.assertTrue(_BamFilePysam._PYSAM_VERBOSITY_SET)


class BamFileTestCase(unittest.TestCase):
    def test_real_subject_attribute(self):
        bam_file_name = "what!?"
        b = BamFile(bam_file_name)
        self.assertTrue(isinstance(b._real_subject, _BamFilePysam))

    @patch("pacbio_data_processing.bam._BamFilePysam")
    def test_attributes_are_delegated_to_real_subject(self, pBamFilePysam):
        b = BamFile("a.bam")
        b._real_subject.some_attribute = "bingo!"
        self.assertEqual(
            b.some_attribute, "bingo!")

    # @patch("pacbio_data_processing.bam.subprocess")
    @patch("pacbio_data_processing.bam.pysam")
    def test_read_mode(self, psp):
        b = BamFile("/dev/zero", mode="r")
        b.header
        b.body
        with self.assertRaises(AttributeError):
            b.write

    def test_write_mode(self):
        b = BamFile("/dev/null", mode="w")
        b.write
        with self.assertRaises(AttributeError):
            b.header
        with self.assertRaises(AttributeError):
            b.body

    def test_other_modes_not_allowed(self):
        with self.assertRaises(ValueError) as cm:
            BamFile("ss", mode="x")
        self.assertEqual(str(cm.exception), "invalid mode: 'x'")


class ReadableBamFileTestCase(unittest.TestCase):
    """This test case ensures that BamFiles created with 'r' mode
    behave as they should.
    I have supplied in most tests a _read_body function (a la monkey
    patch) that in production is provided by another class (either
    _BamFileSamtools or other) to decouple the process of getting
    the data in the file from the behaviour of the ReadableBamFile
    class itself.

    Instead of using _ReadableBamFile, I create instances of
    BamFile. The reason: the _ReadableBamFile/_WritableBamFile
    is one possible implementation for the functionality of
    BamFile's.
    """
    def test_header(self):
        b = BamFile("/dev/zero", mode="r")
        b._read_header = lambda: "xheaderd"
        self.assertEqual(b.header, "xheaderd")

    def test_body(self):
        b = BamFile("/dev/zero", mode="r")
        data = [(b"a", b"zm:i:3"), (b"aa", b"zm:i:cuate")]
        b._read_body = lambda: iter(data)
        for i, line in enumerate(b.body):
            self.assertEqual(tuple(line), data[i])

    def test_iter_is_alias_for_body(self):
        with patch(
                "pacbio_data_processing.bam._ReadableBamFile.body",
                new_callable=PropertyMock):
            b = BamFile("/dev/zero", mode="r")
            self.assertEqual(iter(b), b.body)

    def test_molecule_column(self):
        data = [
            [(b"sd", b"xm:i:23", b"AATG", b"zm:i:78", b"~~~~")],
            [(b"sd", b"xm:i:23", b"AATG", b"4=", b"zm:i:78", b"~~~~")],
        ]
        cols = (3, 4)
        for datum, col in zip(data, cols):
            b = BamFile("/dev/zero", mode="r")
            b._read_body = lambda: iter(datum)
            self.assertEqual(b.molecule_column, col)

    def test_returned_lines_have_molecule_id(self):
        data = [
            (b"sd", b"xm:i:23", b"AATG", b"4=", b"zm:i:78", b"~~~~"),
            (b"sd", b"xm:i:23", b"ACTAG", b"5=", b"zm:i:94", b"~~~~"),
        ]
        mols = (b"78", b"94")
        b = BamFile("/dev/zero", mode="r")
        b._read_body = lambda: iter(data)
        body = list(b.body)
        self.assertEqual(len(body), len(data))
        for line, mol_id in zip(body, mols):
            self.assertEqual(line.molecule_id, mol_id)

    def test_returned_lines_have_flag(self):
        data = [
            (b"sd", b"23", b"AATG", b"4=", b"zm:i:78", b"~~~~"),
            (b"sd", b"342", b"ACTAG", b"5=", b"zm:i:94", b"~~~~"),
        ]
        flags = (23, 342)
        b = BamFile("/dev/zero", mode="r")
        b._read_body = lambda: iter(data)
        body = list(b.body)
        self.assertEqual(len(body), len(data))
        for line, flag in zip(body, flags):
            self.assertEqual(line.flag, flag)

    def test_BamLine_has_right_properties(self):
        b = BamFile("/dev/zero", mode="r")
        b.num_columns = 7
        b.molecule_column = 4
        raw_line = list(range(0, 14, 2))
        raw_line[4] = b"zm:i:8"
        raw_line[1] = b"5"
        line = b._BamLine(*raw_line)
        self.assertEqual(line.molecule_id, b"8")
        self.assertEqual(line.flag, 5)

    def test_num_items(self):
        data = [
            (b"sd", b"xm:i:23", b"AATG", b"4=", b"zm:i:78", b"~~~~"),
            (b"j", b"xm:i:256", b"AATGCZ", b"6=", b"zm:i:78", b"~~~~~~"),
            (b"sd", b"xm:i:23", b"ACTAG", b"5=", b"zm:i:94", b"~~~~"),
        ]
        b = BamFile("/dev/zero", mode="r")
        b._read_body = lambda: iter(data)
        self.assertEqual(b.num_items, {"subreads": 3, "molecules": 2})

    def test_num_molecules(self):
        r = BamFile("/dev/zero", mode="r")
        r.num_items = {"subreads": 334332, "molecules": 245}
        self.assertEqual(r.num_molecules, 245)

    def test_num_subreads(self):
        r = BamFile("/dev/zero", mode="r")
        r.num_items = {"subreads": 33432, "molecules": 245}
        self.assertEqual(r.num_subreads, 33432)

    def test_len(self):
        r = BamFile("/dev/zero", mode="r")
        r.num_items = {"subreads": 1512, "molecules": 24}
        self.assertEqual(len(r), 1512)

    def test_all_molecules(self):
        data = [
            (b"sd", b"xm:i:23", b"AATG", b"4=", b"zm:i:78", b"~~~~"),
            (b"j", b"xm:i:256", b"AATGCZ", b"6=", b"zm:i:78", b"~~~~~~"),
            (b"sd", b"xm:i:23", b"ACTAG", b"5=", b"zm:i:94", b"~~~~"),
            (b"af", b"xm:i:23", b"ACTAG", b"5=", b"zm:i:97", b"~~~~"),
        ]
        b = BamFile("/dev/zero", mode="r")
        b._read_body = lambda: iter(data)
        mol_ids = [b"78", b"94", b"97"]
        for mol_id, expected_mol_id in zip(b.all_molecules, mol_ids):
            self.assertEqual(mol_id, expected_mol_id)

    def test_is_aligned(self):
        data = [
            [(b"sd", b"xm:i:23", b"AATG", b"78", b"zm:i:2", b"~~~~"),
             (b"sd", b"xm:i:25", b"AATG", b"278", b"zm:i:4", b"~~~~")
            ],
            [(b"sd", b"xm:i:23", b"AATG", b"123", b"zm:i:78", b"~~~~"),
             (b"sd", b"xm:i:28", b"AATG", b"0", b"zm:i:78", b"~~~~"),
             (b"sd", b"xm:i:28", b"AATG", b"240", b"zm:i:78", b"~~~~")
            ],
        ]
        aligned = (True, False)
        for datum, res in zip(data, aligned):
            b = BamFile("/dev/zero", mode="r")
            b._read_body = lambda: iter(datum)
            self.assertEqual(b.is_aligned, res)

    def test_is_plausible_aligned_version_of_True_if_all_ok(self):
        with patch(
                "pacbio_data_processing.bam._ReadableBamFile.all_molecules",
                new_callable=PropertyMock) as mall_molecules:
            mall_molecules.side_effect = (
                iter([1, 4, 5, 19]), iter([1, 4, 5, 19]),
                iter([3, 4, 19]), iter([3, 4, 5, 19])
            )
            candidate = BamFile("dont.bam")
            candidate.is_aligned = True
            other = BamFile("other.bam")
            other.is_aligned = False
            for _ in range(2):
                self.assertTrue(
                    candidate.is_plausible_aligned_version_of(other)
                )

    def test_is_plausible_aligned_version_of_False_if_unaligned(self):
        candidate = BamFile("dont.bam")
        candidate.is_aligned = False
        other = BamFile("other.bam")
        self.assertFalse(
            candidate.is_plausible_aligned_version_of(other)
        )

    def test_is_plausible_aligned_version_of_False_if_other_aligned(self):
        candidate = BamFile("dont.bam")
        candidate.is_aligned = True
        other = BamFile("other.bam")
        other.is_aligned = True
        self.assertFalse(
            candidate.is_plausible_aligned_version_of(other)
        )

    def test_is_plausible_aligned_version_of_False_if_mols_mismatch(self):
        with patch(
                "pacbio_data_processing.bam._ReadableBamFile.all_molecules",
                new_callable=PropertyMock) as mall_molecules:
            mall_molecules.side_effect = (
                iter([1, 4, 5]), iter([423, 533, 1329]),
                iter([1, 3, 4]), iter([3, 4, 5, 19])
            )
            candidate = BamFile("dont.bam")
            candidate.is_aligned = True
            other = BamFile("other.bam")
            other.is_aligned = False
            for _ in range(2):
                self.assertFalse(
                    candidate.is_plausible_aligned_version_of(other)
                )

    def test_md5sum_body(self):
        data = [
            [], [(b"sd", b"xm:i:23", b"AATG", b"zm:i:78", b"~~~~")]
        ]
        md5s = (
            "d41d8cd98f00b204e9800998ecf8427e",
            "7606a24d20a2f22269f6967d0f72d684"
        )
        for datum, md5 in zip(data, md5s):
            b = BamFile("/dev/zero", mode="r")
            b._read_body = lambda: iter(datum)
            self.assertEqual(b.md5sum_body, md5)

    def test_full_md5sum(self):
        expected_md5 = "84f6bf10d84c171a2630a153ac12411b"
        b = BamFile("test.bam", mode="r")
        mopen = mock_open(read_data=b"sda\n")
        with patch("pacbio_data_processing.bam.open", mopen):
            md5sum = b.full_md5sum
        self.assertEqual(md5sum, expected_md5)
        mopen.assert_called_once_with("test.bam", "rb")

    @patch("pacbio_data_processing.bam.Path")
    def test_size_in_bytes(self, pPath):
        b = BamFile("fake.bam", mode="r")
        pPath.return_value.stat.return_value.st_size = 567
        self.assertEqual(b.size_in_bytes, 567)


class WritableBamFileTestCase(unittest.TestCase):
    """This test case ensures that BamFiles created with 'w'
    mode behave as they should.
    I have supplied a _write monkey patched attribute that in
    production is provided by another class (either
    _BamFileSamtools or other) to decouple the writing of data
    from the behaviour of the _WritableBamFile class itself.

    Instead of using _WritableBamFile, I create instances of
    BamFile. The reason: the _ReadableBamFile/_WritableBamFile
    is one possible implementation for the functionality of
    BamFile's.
    """
    def test_write(self):
        b = BamFile("/dev/zero", mode="w")
        b._write = MagicMock()
        b.write(header="my head", body="my body")
        b._write.assert_called_once_with(header="my head", body="my body")


class PackLinesTestCase(unittest.TestCase):
    def test_pack_lines(self):
        body = [(b"a", b"33"), (b"-l-", b"o")]
        for raw, packed in zip(body, pack_lines(body)):
            self.assertEqual(b"\t".join(raw)+b"\n", packed)


@patch("pacbio_data_processing.bam.pysam.set_verbosity")
class SetPysamVerbosity(unittest.TestCase):
    def test_sets_verbosity_in_pysam(self, pset_verbosity):
        set_pysam_verbosity()
        pset_verbosity.assert_called_once_with(0)

    def test_protection_against_failures_in_set_verbosity(
            self, pset_verbosity):
        pset_verbosity.side_effect = (
            AttributeError("module 'pysam' has no attribute 'set_verbosity'"),
            TypeError(),
            Exception("Hello. It's me")
        )
        with self.assertLogs() as cm:
            set_pysam_verbosity()
            set_pysam_verbosity()
            set_pysam_verbosity()
        self.assertEqual(
            cm.output,
            [
                ("ERROR:root:module 'pysam' has no attribute 'set_verbosity'. "
                 "You might see some non-critical error messages from pysam."
                ),
                ("ERROR:root:'pysam.set_verbosity' failed. It looks like pysam"
                 " changed its API. Continuing without setting the verbosity. "
                 "You might see some non-critical error messages from pysam."
                ),
                ("ERROR:root:Unexpected error calling 'pysam.set_verbosity':\n"
                 "Hello. It's me\nContinuing without setting the verbosity. "
                 "You might see some non-critical error messages from pysam."
                ),
            ]
        )
