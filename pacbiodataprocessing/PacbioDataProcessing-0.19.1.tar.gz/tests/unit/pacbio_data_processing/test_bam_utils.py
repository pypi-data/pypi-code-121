#######################################################################
#
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

import unittest
from unittest.mock import patch, Mock, call, mock_open, MagicMock
from pathlib import Path
from collections import deque, namedtuple
from subprocess import CompletedProcess

from pacbio_data_processing.bam_utils import (
    write_one_molecule_bam, subreads_per_molecule, split_bam_file_in_molecules,
    gen_index_single_molecule_bams, join_gffs, count_subreads_per_molecule,
    Molecule, CircularDNAPosition, flag2strand
)
from pacbio_data_processing.cigar import Cigar


class ParseInputPartitionTestCase(unittest.TestCase):
    def test_normal_cases(self):
        ...


@patch("pacbio_data_processing.bam_utils.BamFile")
class WriteOneMoleculeBamTestCase(unittest.TestCase):
    def test_returns_name_of_written_file(self, pBamFile):
        out = write_one_molecule_bam([b"a22"], b"what", Path("p.cho"), "an")
        self.assertEqual(out, Path("p.an.cho"))

    def test_writes_bam(self, pBamFile):
        buf = Mock()
        with self.assertLogs(level="INFO") as cm:
            out = write_one_molecule_bam(buf, b"what", Path("p.cho"), "an")
        self.assertEqual(
            cm.output,
            [f"INFO:root:One-molecule BAM file written: {out}"]
        )
        pBamFile.assert_called_once_with(out, mode="w")
        pBamFile.return_value.write.assert_called_once_with(
            header=b"what", body=buf
        )
        buf.clear.assert_called_once_with()


@patch("pacbio_data_processing.bam_utils.write_one_molecule_bam")
class SubreadsPerMoleculeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        attrs = [f"a{_}" for _ in range(5)]
        attrs[3] = "zmw"

        class BamLine(namedtuple("BamLine", attrs)):
            @property
            def molecule_id(self):
                return self.zmw.split(b":")[-1]
        cls.BamLine = BamLine

    def setUp(self):
        self.one_mol_lines = [
            self.BamLine(4, 44, 444, b"zm:i:4567", 4444),
            self.BamLine(5, 55, 555, b"zm:i:4567", 5555),
            self.BamLine(6, 66, 666, b"zm:i:4567", 6666),
            self.BamLine(7, 77, 777, b"zm:i:4567", 7777),
        ]
        self.one_file = ["w4567"]
        self.one_mols = [Molecule(int(_[1:]), _) for _ in self.one_file]
        self.four_mols_lines = self.one_mol_lines + [
            self.BamLine(8, 88, 888, b"zm:i:8921", 8888),
            self.BamLine(9, 99, 999, b"zm:i:8921", 9999),
            self.BamLine(2, 22, 222, b"zm:i:8921", 2222),
            self.BamLine(1, 11, 111, b"zm:i:8921", 1111),
            self.BamLine(43, 4343, 434343, b"zm:i:43", 43434343),
            self.BamLine(3, 33, 333, b"zm:i:3333", 3333),
            self.BamLine(30, 3030, 303030, b"zm:i:3333", 30303030),
        ]
        self.four_files = ["w4567", "w8921", "w43", "w3333"]
        self.four_mols = [Molecule(int(_[1:]), _) for _ in self.four_files]
        self.two_files = ["w8921", "w3333"]
        self.two_mols = [Molecule(int(_[1:]), _) for _ in self.two_files]
        self.two_more_files = ["w4567", "w43"]

    def test_one_type_of_mol_which_is_in_todo(self, pwrite1molbam):
        pwrite1molbam.side_effect = self.one_file
        header = b"header"
        prefix = "file_name_prefix"
        lines = self.one_mol_lines
        todo = {_.id: _ for _ in self.one_mols}
        mols = list(subreads_per_molecule(lines, header, prefix, todo))
        pwrite1molbam.assert_called_once_with(
            deque(lines), header, prefix, 4567
        )
        self.assertEqual(mols, [(_.id, _) for _ in self.one_mols])

    def test_several_types_of_mol_which_are_in_todo(self, pwrite1molbam):
        pwrite1molbam.side_effect = self.four_files
        header = b"header"
        prefix = "file_name_prefix"
        lines = self.four_mols_lines
        todo = {_.id: _ for _ in self.four_mols}
        mols_files = list(subreads_per_molecule(lines, header, prefix, todo))
        pwrite1molbam.assert_has_calls(
            [
                call(deque(lines), header, prefix, 4567),
                call(deque(lines), header, prefix, 8921),
                call(deque(lines), header, prefix, 43),
                call(deque(lines), header, prefix, 3333),
            ]
        )
        self.assertEqual(mols_files, [(_.id, _) for _ in self.four_mols])

    def test_with_several_types_of_mol_not_all_in_todo(self, pwrite1molbam):
        todo = {_.id: _ for _ in self.two_mols}
        lines = {
            k: [
                _ for _ in self.four_mols_lines if str(k) in _[3].decode()
            ] for k in todo
        }
        memory = {}

        def pwrite_side_effect(buf, h, pref, molid):
            mem_item = memory.setdefault(molid, [])
            for line in buf:
                mem_item.append(line)
            return f"w{molid}"
        pwrite1molbam.side_effect = pwrite_side_effect
        header = b"header"
        prefix = "file_name_prefix"
        results = subreads_per_molecule(
            self.four_mols_lines, header, prefix, todo
        )
        list_results = list(results)
        self.assertTrue(len(list_results) <= len(todo))
        for mol_id in todo.keys():
            self.assertEqual(lines[mol_id], memory[mol_id])
        # The next one does not work (the buffer get mixed):
        # pwrite1molbam.assert_has_calls(
        #     [call(deque(lines[mol_id]), header, prefix, mol_id)
        #          for mol_id in todo.keys()]
        # )
        for mol_id, mol in list_results:
            self.assertEqual(mol.src_bam_path, "w"+str(mol_id))

    def test_with_empty_todo(self, pwrite1molbam):
        results = subreads_per_molecule(
            self.four_mols_lines, "head", "pref", {}
        )
        list_results = list(results)
        pwrite1molbam.assert_not_called()


@patch("pacbio_data_processing.bam_utils.BamFile")
@patch("pacbio_data_processing.bam_utils.subreads_per_molecule")
class SplitBamFileInMoleculesTestCase(unittest.TestCase):
    def test_uses_subreads_per_molecule(
            self, psubreads_per_molecule, pBamFile):
        args = (Path("/tmp/my.bam"), "/tmp/mywork", {123, 1000})
        list(split_bam_file_in_molecules(*args))
        psubreads_per_molecule.assert_called_once_with(
            pBamFile("my.bam").body, pBamFile("my.bam").header,
            Path("/tmp/mywork/my.bam"), {123, 1000}
        )

    def test_splitted_bam_file_yielded_and_logged(
            self, psubreads_per_molecule, pBamFile):
        mol_ids = [1, 2, 3]
        files = ["a", "b", "c"]
        mols = [Molecule(i, j) for i, j in zip(mol_ids, files)]
        psubreads_per_molecule.return_value = zip(mol_ids, mols)
        results = split_bam_file_in_molecules(
            Path("/tmp/my.bam"), "/tmp/mywork", {1, 2, 3})
        with self.assertLogs(level="DEBUG") as cm:
            for result, (mol_id, mol) in zip(results, zip(mol_ids, mols)):
                self.assertEqual(result, (mol_id, mol))
                self.assertIn(
                    f"DEBUG:root:BAM file '{mol.src_bam_path}' generated",
                    cm.output
                )


@patch("pacbio_data_processing.bam_utils.subprocess.run")
class GenIndexSingleMoleculeBamsTestCase(unittest.TestCase):
    def setUp(self):
        self.program = MagicMock()
        self.program.__str__.return_value = "/path/to/pbindex"
        self.program.name = "pbindex"
        self.mols = [
            (23, Molecule(23, "w/some.23.bam")),
            (234, Molecule(234, "h/some.234.bam")),
            (236, Molecule(236, "/tmp/some.236.bam"))
        ]
        self.files = [_[1].src_bam_path for _ in self.mols]

    def test_calls_underlying_program(self, prun):
        prun.return_value = CompletedProcess((self.program, "<file>"), 0)
        result = list(gen_index_single_molecule_bams(self.mols, self.program))
        prun.assert_has_calls(
            [call((str(self.program), _), capture_output=True
                  ) for _ in self.files]
        )
        self.assertEqual(self.mols, result)

    def test_logs_and_doesnt_yield_if_error(self, prun):
        expected_retcodes = (0, 0, 1)
        run_results = [
            CompletedProcess((self.program, m[1].src_bam_path), ret)
            for m, ret in zip(self.mols, expected_retcodes)
        ]
        prun.side_effect = run_results
        run_results[-1].stderr = b"BOOM!!!\n"
        with self.assertLogs(level="DEBUG") as cm:
            result = list(
                gen_index_single_molecule_bams(self.mols, self.program)
            )
        self.assertEqual(
            ["ERROR:root:[pbindex] Molecule 236 could not be processed",
             "DEBUG:root:[pbindex] The reported error was:",
             "DEBUG:root:[pbindex]     'BOOM!!!'"],
            cm.output
        )
        self.assertEqual(len(result), 2)
        for molid, mol in result:
            self.assertNotEqual(molid, 236)
            self.assertFalse(mol.had_processing_problems)
        self.assertTrue(self.mols[2][1].had_processing_problems)


class JoinGffsTestCase(unittest.TestCase):
    def test_writes_new_file(self):
        # A bit smoky test
        infiles = ("one.gff", "three.gff", "seven.gff")
        molecules = [Molecule(i) for i in (1, 3, 7)]
        for m, f in zip(molecules, infiles):
            m.gff_path = f
        wunits = ((m.id, m) for m in molecules)
        results_file = "results.gff"
        data = "jose chu\nletón\nalberto\ncadiscos\n"
        with patch(
                "pacbio_data_processing.bam_utils.open",
                mock_open(read_data=data)
                ) as m:
            result_gen = join_gffs(wunits, results_file)
            handle = m()
            for result, infile in zip(result_gen, infiles):
                self.assertEqual(result, infile)
            handle.write.assert_has_calls([call(data) for _ in infiles])
            m.assert_has_calls([call(results_file, 'w')])


class FakeBam:
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        Line = namedtuple("BamLine", ("molecule_id", "flag"))
        for item in self.data:
            yield Line(*item)


class CountSubreadsPerMoleculeTestCase(unittest.TestCase):
    FAKE_BAM_DATA = [
        (b"26", b"0"),
        (b"26", b"256"),
        (b"26", b"16"),
        (b"26", b"272"),
        (b"26", b"256"),
        (b"26", b"272"),
        (b"211", b"0"),
        (b"211", b"256"),
        (b"211", b"256"),
        (b"267", b"16"),
        (b"267", b"272"),
        (b"267", b"272"),
        (b"267", b"272"),
        (b"548", b"0"),
        (b"548", b"4"),
    ]

    def test_returned_data_is_groupped_by_strand_orientation(self):
        bam = FakeBam(self.FAKE_BAM_DATA)
        count = count_subreads_per_molecule(bam)
        self.assertEqual(count[26]["+"], 3)
        self.assertEqual(count[26]["-"], 3)
        self.assertEqual(count[211]["+"], 3)
        self.assertEqual(count[211]["-"], 0)
        self.assertEqual(count[267]["+"], 0)
        self.assertEqual(count[267]["-"], 4)
        self.assertEqual(count[548]["+"], 1)
        self.assertEqual(count[548]["-"], 0)
        self.assertEqual(count[548]["?"], 1)


class MoleculeTestCase(unittest.TestCase):
    def setUp(self):
        self.example = Molecule(
            19, None,
            (b"", b"", b"", b"516", b"6=", b"",
                 b"", b"", b"", b"CGATCG", b"!~w~+Q")
        )

    def test_creation(self):
        m = Molecule(56)
        self.assertEqual(m.id, 56)
        self.assertEqual(m.src_bam_path, None)
        self.assertEqual(m._best_ccs_line, None)
        self.assertEqual(m.gff_path, None)

        m = Molecule(23, "/tmp/funny_path")
        self.assertEqual(m.id, 23)
        self.assertEqual(m.src_bam_path, "/tmp/funny_path")
        self.assertEqual(m._best_ccs_line, None)
        self.assertEqual(m.gff_path, None)

        m = Molecule(129, Path("/tmp/funny_path"))
        self.assertEqual(m.id, 129)
        self.assertEqual(m.src_bam_path, Path("/tmp/funny_path"))
        self.assertEqual(m._best_ccs_line, None)
        self.assertEqual(m.gff_path, None)

        m = Molecule(9, "h", (b"g", b"45"))
        self.assertEqual(m.id, 9)
        self.assertEqual(m.src_bam_path, "h")
        self.assertEqual(m._best_ccs_line, (b"g", b"45"))
        self.assertEqual(m.gff_path, None)

    def test_cigar_atribute(self):
        m = Molecule(9, None, (b"", b"", b"", b"", b"", b"15="))
        self.assertEqual(m.cigar, Cigar("15="))

    def test_dna_attribute(self):
        self.assertEqual(self.example.dna, "CGATCG")

    def test_length(self):
        self.assertEqual(len(self.example), 6)

    def test_start_attribute(self):
        self.assertEqual(self.example.start, CircularDNAPosition(515))
        self.example.start = CircularDNAPosition(1023)
        self.assertEqual(self.example.start, CircularDNAPosition(1023))

    def test_end_attribute(self):
        self.example.reference = "?"*519
        self.assertEqual(self.example.end, CircularDNAPosition(2, 519))
        self.example.start = CircularDNAPosition(510, 519)
        self.assertEqual(self.example.end, CircularDNAPosition(516, 519))

    def test_ascii_quals(self):
        self.assertEqual(self.example.ascii_quals, "!~w~+Q")

    def test_has_default_reference(self):
        self.assertEqual(self.example.reference, "")

    def test_find_gatc_positions(self):
        dnas = [
            b"",
            b"AGCGATGATAGAT",
            b"GATCGATC",
            b"GGATACGATCCTGATCGAACGATCT",
        ]
        expected_positions = [
            [],
            [],
            [CircularDNAPosition(_) for _ in (0, 4)],
            [CircularDNAPosition(_) for _ in (6, 12, 20)],
        ]
        starts = [1]*4
        for dna, positions, start in zip(dnas, expected_positions, starts):
            self.example._best_ccs_line = [b"", b"", b"", f"{start}".encode(),
                b"6=", b"", b"", b"", b"", dna, b""]
            self.assertEqual(self.example.find_gatc_positions(), positions)
        ref = "CGATCTAAATTTGGGCCCGGATACGATCCTGATCGAA"
        self.example.reference = ref
        self.example.start = 18
        self.assertEqual(
            self.example.find_gatc_positions(),
            [CircularDNAPosition(_, len(ref)) for _ in (24, 30, 1)]
        )

    def test_is_crossing_origin(self):
        self.example.reference = "?"*519
        self.assertTrue(self.example.is_crossing_origin())
        self.example.start -= 10
        self.assertFalse(self.example.is_crossing_origin())
        self.example.start += 9
        self.assertTrue(self.example.is_crossing_origin())
        self.example.start = 256
        self.assertTrue(self.example.is_crossing_origin(ori_pi_shifted=True))

    def test_pi_shift_back(self):
        self.example.reference = "?"*519
        self.example.start = CircularDNAPosition(100, 519)
        self.example.pi_shift_back()
        self.assertEqual(self.example.start, CircularDNAPosition(359, 519))

    def test_had_processing_problems(self):
        m = Molecule(9, None, (b"", b"", b"", b"", b"", b"15="))
        self.assertFalse(m.had_processing_problems)


class Flag2StrandTestCase(unittest.TestCase):
    def test_direct(self):
        for flag in (0, 256):
            self.assertEqual("+", flag2strand(flag))

    def test_reverse(self):
        for flag in (16, 272):
            self.assertEqual("-", flag2strand(flag))

    def test_unknown(self):
        for flag in (4, 8, 512):
            self.assertEqual("?", flag2strand(flag))
