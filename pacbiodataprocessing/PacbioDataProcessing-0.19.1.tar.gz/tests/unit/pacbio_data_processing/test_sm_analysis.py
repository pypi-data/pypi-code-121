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
from unittest.mock import patch, Mock, mock_open, call, MagicMock
from collections import namedtuple, Counter
from pathlib import Path

from pacbio_data_processing.sm_analysis import (
    _main, main_cl, SingleMoleculeAnalysis, add_to_own_output,
    generate_CCS_file, map_molecules_with_highest_sim_ratio, MethylationReport,
    METHYLATION_REPORT_HEADER, match_methylation_states_m6A,
)
from pacbio_data_processing.bam_utils import Molecule
from pacbio_data_processing.errors import SMAPipelineError
from pacbio_data_processing.constants import BLASR_PREF


TEST_DATA_GFF1 = """##gff-version 3
##source ipdSummary v2.0
##source-commandline ipdSummary tmpojno574_/sample.23.bam --reference eco000913_3.fasta --identify m6A --numWorkers 4 --gff tmpojno574_/sample.23.bam.gff
##sequence-region U00096.3 1 4641652
U00096.3        kinModCall      modified_base   1742174 1742174 22      -       .       coverage=5;context=CCTTCCGGTTTCAAATTACGATCCACCACCGCAAAATAGGT;IPDRatio=3.08
U00096.3        kinModCall      m6A     1742233 1742233 21      +       .       coverage=8;context=TATCGGTTCGAAAAAAACCGATCTGAATGTTGATCCCTGGA;IPDRatio=5.01;identificationQv=4
U00096.3        kinModCall      m6A     1742234 1742234 23      -       .       coverage=7;context=ATCCAGGGATCAACATTCAGATCGGTTTTTTTCGAACCGAT;IPDRatio=3.11;identificationQv=5
U00096.3        kinModCall      m6A     1742245 1742245 20      +       .       coverage=8;context=AAAAACCGATCTGAATGTTGATCCCTGGATTAATAAATATA;IPDRatio=4.43;identificationQv=3
U00096.3        kinModCall      modified_base   1742246 1742246 23      -       .       coverage=7;context=ATATATTTATTAATCCAGGGATCAACATTCAGATCGGTTTT;IPDRatio=2.91
"""  # noqa: E501

TEST_DATA_GFF2 = """##gff-version 3
##source ipdSummary v2.0
##source-commandline ipdSummary tmpojno574_/sample.28.bam --reference eco000913_3.fasta --identify m6A --numWorkers 4 --gff tmpojno574_/sample.28.bam.gff
##sequence-region U00096.3 1 4641652
U00096.3        kinModCall      modified_base   1346310 1346310 28      -       .       coverage=55;context=GGTTATGTGAAGATTACACAGGGTTGAAAGAACACGACGTC;IPDRatio=1.78
U00096.3        kinModCall      modified_base   1346312 1346312 21      -       .       coverage=55;context=TCGGTTATGTGAAGATTACACAGGGTTGAAAGAACACGACG;IPDRatio=1.51
U00096.3        kinModCall      modified_base   1346322 1346322 33      +       .       coverage=55;context=TTTCAACCCTGTGTAATCTTCACATAACCGATTGAAGCGTT;IPDRatio=1.75
U00096.3        kinModCall      modified_base   1346387 1346387 21      -       .       coverage=57;context=TGCTGAGCAGGTAGTTTCTGAAGCACATTCCGCAATAGTGA;IPDRatio=1.49
U00096.3        kinModCall      modified_base   1346403 1346403 27      -       .       coverage=54;context=CACACGGGCTTTCCTTTGCTGAGCAGGTAGTTTCTGAAGCA;IPDRatio=1.61
"""  # noqa: E501

TEST_DATA_GFF3 = """##gff-version 3
##source ipdSummary v2.0
##source-commandline ipdSummary tmpojno574_/sample.140.bam --reference eco000913_3.fasta --identify m6A --numWorkers 4 --gff tmpojno574_/sample.140.bam.gff
##sequence-region U00096.3 1 4641652
U00096.3        kinModCall      m5A     2148145 2148145 115     +       .       coverage=59;context=AGGCGGTGATTGGTCGTCCGATCAACTTCCAGGGGCTGGGC;IPDRatio=5.40;identificationQv=113
U00096.3        kinModCall      modified_base   2148145 2148145 23      -       .       coverage=31;context=GCCCAGCCCCTGGAAGTTGATCGGACGACCAATCACCGCCT;IPDRatio=5.83
U00096.3        kinModCall      m6A     2148146 2148146 68      -       .       coverage=35;context=CGCCCAGCCCCTGGAAGTTGATCGGACGACCAATCACCGCC;IPDRatio=6.38;identificationQv=51
U00096.3        kinModCall      modified_base   2148188 2148188 30      -       .       coverage=57;context=CGCGTTCCAGAATCCCTTGCGCCTGGGTGTTTGCTTCATCA;IPDRatio=1.63
U00096.3        kinModCall      modified_base   2148249 2148249 39      -       .       coverage=59;context=AGCCCAGCCGCGACCGGCTCGTACTGGAATACCACGTCCCT;IPDRatio=1.82
"""  # noqa: E501


def nested_split(data):
    return [line.split() for line in data]


@patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis")
@patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysisParameters")
@patch("pacbio_data_processing.sm_analysis.config_logging")
class MainFunctionTestCase(unittest.TestCase):
    def setUp(self):
        self.conf = MagicMock()

    def test_logging_configured_according_to_user_input(
            self, pconfig_logging, pSingleMoleculeAnalysisParameters,
            pSingleMoleculeAnalysis):
        _main(self.conf)
        pconfig_logging.assert_called_once_with(self.conf.verbose)

    def test_creates_SingleMoleculeAnalysisParameters_instance(
            self, pconfig_logging, pSingleMoleculeAnalysisParameters,
            pSingleMoleculeAnalysis):
        _main(self.conf)
        pSingleMoleculeAnalysisParameters.assert_called_once_with(self.conf)

    def test_reports_parameters(
            self, pconfig_logging, pSingleMoleculeAnalysisParameters,
            pSingleMoleculeAnalysis):
        pSingleMoleculeAnalysisParameters.return_value.__str__.return_value = (
            "a nine o seven")
        with self.assertLogs() as cm:
            _main(self.conf)
        self.assertEqual(cm.output, ["INFO:root:a nine o seven"])

    def test_creates_SingleMoleculeAnalysis_instance(
            self, pconfig_logging, pSingleMoleculeAnalysisParameters,
            pSingleMoleculeAnalysis):
        _main(self.conf)
        pSingleMoleculeAnalysis.assert_called_once_with(
            pSingleMoleculeAnalysisParameters.return_value)

    def test_calls_SingleMoleculeAnalysis(
            self, pconfig_logging, pSingleMoleculeAnalysisParameters,
            pSingleMoleculeAnalysis):
        _main(self.conf)
        pSingleMoleculeAnalysis.return_value.assert_called_once_with()


@patch("pacbio_data_processing.sm_analysis._main")
@patch("pacbio_data_processing.sm_analysis.parse_cl")
class MainClFunctionTestCase(unittest.TestCase):
    def test_parses_cl(
            self, pparse_cl, pmain):
        main_cl()
        pparse_cl.assert_called_once_with()

    def test_calls_main(
            self, pparse_cl, pmain):
        main_cl()
        pmain.assert_called_once_with(pparse_cl.return_value)


class HighLevelErrorsTestCase(unittest.TestCase):
    @patch("pacbio_data_processing.sm_analysis.parse_cl")
    def test_main_cl_does_not_crashes_if_exception(self, pparse_cl):
        pparse_cl.side_effect = Exception("ji ji")
        with self.assertLogs() as cm:
            main_cl()
        self.assertEqual(cm.output, ["CRITICAL:root:ji ji"])


class SingleMoleculeAnalysisTestCase(unittest.TestCase):
    def setUp(self):
        self.params = Mock()
        self.params.fasta = "/tmp/my.fasta"
        self.params.only_produce_methylation_report = False
        self.params.one_line_per_mod_filename = "/tmp/hello"
        self.params.CCS_bam_file = Path("/tmp/what/ccs.bam")
        with (patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._ensure_input_bam_aligned") as pensure,
              patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._ensure_ccs_bam_aligned") as pensure_ccs,
              patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._create_references") as pcreate_refs,
              patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._init_summary") as pinit_summary,
              patch("pacbio_data_processing.sm_analysis.Blasr") as pblasr,
              patch("pacbio_data_processing.sm_analysis.CCS") as pccs):
            self.sma = SingleMoleculeAnalysis(self.params)
        self.pensure_input_bam_aligned = pensure
        self.pensure_ccs_bam_aligned = pensure_ccs
        self.pcreate_refs = pcreate_refs
        self.pinit_summary = pinit_summary
        self.pblasr = pblasr
        self.pccs = pccs

    def set_reference(self):
        with patch("pacbio_data_processing.sm_analysis.DNASeq") as pDNASeq:
            self.sma._create_references()
        self.pDNASeq = pDNASeq

    def test_instance_has_attribute_parameters(self):
        self.assertEqual(self.params, self.sma.parameters)

    def test_instance_called__ensure_input_bam_aligned(self):
        self.pensure_input_bam_aligned.assert_called_once_with()

    def test_instance_called__ensure_ccs_bam_aligned(self):
        self.pensure_ccs_bam_aligned.assert_called_once_with()

    def test_instance_calls_create_references(self):
        self.pcreate_refs.assert_called_once_with()

    def test_instance_calls_init_summary(self):
        self.pinit_summary.assert_called_once_with()

    def test_instance_sets_blasr(self):
        self.pblasr.assert_called_once_with(self.params.blasr_path)
        self.assertEqual(
            self.sma.blasr,
            self.pblasr.return_value
        )

    def test_instance_sets_ccs(self):
        self.pccs.assert_called_once_with("ccs")
        self.assertEqual(
            self.sma.ccs,
            self.pccs.return_value
        )

    def test_create_references(self):
        self.set_reference()
        self.assertEqual(
            self.sma.reference["straight"],
            self.pDNASeq.from_fasta.return_value
        )
        self.assertEqual(self.sma.fasta["straight"], Path(self.params.fasta))
        pi_shifted = (
            self.pDNASeq.from_fasta.return_value.pi_shifted.return_value)
        self.assertEqual(self.sma.reference["pi-shifted"], pi_shifted)
        pi_shifted_path = Path("/tmp/pi-shifted.my.fasta")
        pi_shifted.write_fasta.assert_called_once_with(str(pi_shifted_path))
        self.assertEqual(self.sma.fasta["pi-shifted"], pi_shifted_path)

    def test_init_summary(self):
        self.set_reference()
        with patch("pacbio_data_processing.sm_analysis.SummaryReport"
                   ) as psummary_report:
            self.sma._init_summary()
            psummary_report.assert_called_once_with(
                self.sma.input_bam_file, self.sma.reference["straight"]
            )
            self.assertEqual(
                self.sma.summary_report, psummary_report.return_value
            )

    def test_all_tasks_enabled_if_not_opmr(self):
        self.assertTrue(self.sma._do_split_bam)
        self.assertTrue(self.sma._do_filter_molecules)
        self.assertTrue(self.sma._do_collect_statistics)
        self.assertTrue(self.sma._do_generate_indices)
        self.assertTrue(self.sma._do_ipd_analysis)
        self.assertTrue(self.sma._do_create_own_output)
        self.assertTrue(self.sma._do_produce_methylation_report)

    def test_most_tasks_disabled_if_opmr(self):
        self.params.only_produce_methylation_report = True
        self.sma._set_tasks()
        self.assertTrue(self.sma._do_split_bam)
        self.assertTrue(self.sma._do_filter_molecules)
        self.assertTrue(self.sma._do_collect_statistics)
        self.assertFalse(self.sma._do_generate_indices)
        self.assertFalse(self.sma._do_ipd_analysis)
        self.assertFalse(self.sma._do_create_own_output)
        self.assertTrue(self.sma._do_produce_methylation_report)

    def _test_some_tasks_disabled_if_using_backup_dir(self):
        """

        Write me! (once resuming from temp dir is possible)


        """
        ...

    @patch(
        "pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
        "_backup_temp_dir_if_needed")
    @patch("pacbio_data_processing.sm_analysis.time.time")
    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
           "_dump_results")
    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
           "_fix_positions")
    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
           "_ipd_analysis")
    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
           "_generate_indices")
    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
           "_collect_statistics")
    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
           "_filter_molecules")
    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
           "_split_bam")
    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
           "_select_molecules")
    def test_main_procedure(
            self, pselect_molecules, psplit_bam, pfilter_molecules,
            pcollect_statistics, pgen_indices, pipd_analysis, pfix_positions,
            pdump_results, ptime, pbackup_temp_dir_if_needed):
        ptime.side_effect = (123456.000, 124460.503, 124557.0)
        with self.assertLogs() as cm:
            self.sma()
        pselect_molecules.assert_called_once_with()
        psplit_bam.assert_called_once_with()
        pfilter_molecules.assert_called_once_with()
        pcollect_statistics.assert_called_once_with()
        pgen_indices.assert_called_once_with()
        pipd_analysis.assert_called_once_with()
        pfix_positions.assert_called_once_with()
        pdump_results.assert_called_once_with()
        pbackup_temp_dir_if_needed.assert_called_once_with()
        self.assertEqual(
            cm.output,
            ["INFO:root:Execution time (wall clock time): 1004.50 s = 0.28 h"]
        )

    def test_partition_attribute(self):
        with (patch("pacbio_data_processing.sm_analysis.Partition") as pPart,
              patch("pacbio_data_processing.sm_analysis.BamFile") as pBamFile):
            self.assertEqual(self.sma.partition, pPart.return_value)
            self.sma.partition  # To ensure it is cached...
            pPart.assert_called_once_with(
                self.params.partition,
                pBamFile.return_value
                )
            pBamFile.assert_called_once_with(self.sma.input_bam_file)

    @patch(
        "pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
        "._keep_only_pishifted_molecules_crossing_origin")
    @patch(
        "pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
        "._crosscheck_molecules_in_partition_with_ccs")
    @patch(
        "pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
        "._collect_suitable_molecules_from_ccs")
    @patch(
        "pacbio_data_processing.sm_analysis"
        ".map_molecules_with_highest_sim_ratio")
    def test_select_molecules_creates_set_of_molecule_ids(
            self, pmap_molecules, pcollect, pcrosscheck, pkeep_only):
        self.sma.partition = {3, 4, 5, 6}
        self.sma.aligned_input_bam_file = self.sma.input_bam_file
        self.sma.aligned_ccs_bam_file = Path("blasr.ccs.w4.bam")
        StraightBam = Mock(all_molecules={1, 4, 5, 6, 7})
        PIShiftedBam = Mock(all_molecules={3, 4, 6, 8})
        self.sma.aligned_input_bam_file = {
            "straight": self.sma.input_bam_file,
            "pi-shifted": "whatever"
        }
        with patch("pacbio_data_processing.sm_analysis.BamFile") as pBamFile:
            pBamFile.side_effect = (StraightBam, PIShiftedBam)
            self.sma._select_molecules()
        self.assertEqual(self.sma._molecule_ids_todo["straight"], {4, 5, 6})
        self.assertEqual(self.sma._molecule_ids_todo["pi-shifted"], {3, 4, 6})

    @patch(
        "pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
        "._keep_only_pishifted_molecules_crossing_origin")
    @patch(
        "pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
        "._crosscheck_molecules_in_partition_with_ccs")
    @patch(
        "pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
        "._collect_suitable_molecules_from_ccs")
    @patch("pacbio_data_processing.sm_analysis.BamFile")
    def test_select_molecules_maps_collects_filters_out_and_crosschecks(
            self, pBamFile, pcollect_molecules, pcrosscheck, pkeep_only):
        self.sma.aligned_input_bam_file = {
            "straight": self.sma.input_bam_file,
            "pi-shifted": "whatever"
        }
        self.sma._select_molecules()
        pcollect_molecules.assert_called_once_with()
        pkeep_only.assert_called_once_with(pcollect_molecules.return_value)
        pcrosscheck.assert_called_once_with(pkeep_only.return_value)

    @patch("pacbio_data_processing.sm_analysis.split_bam_file_in_molecules")
    def test__split_bam_calls_generator_and_sets_attribute(
            self, psplit_bam):
        Wdir = namedtuple("Wdir", ["name"])
        wdir = "a/nnn3.3"
        self.sma._workdir = Wdir(name=wdir)
        self.sma._molecules_todo = {
            55: Molecule(55),
            80: Molecule(80),
            7474: Molecule(7474),
            8884: Molecule(8884)
        }
        for mol_id in 55, 80, 7474:
            mol = self.sma._molecules_todo[mol_id]
            mol.variant = "straight"
            mol.src_bam_path = "straight.bam"
        omol = self.sma._molecules_todo[8884]
        omol.variant = "pi-shifted"
        omol.src_bam_path = "pi-shifted.bam"
        self.sma.aligned_input_bam_file["straight"] = "straight.bam"
        self.sma.aligned_input_bam_file["pi-shifted"] = "pi-shifted.bam"
        psplit_bam.side_effect = (iter([55, 80, 7474]), iter([8884]))
        self.sma._split_bam()
        psplit_bam.assert_has_calls([
            call("straight.bam", wdir,
                 {_: self.sma._molecules_todo[_] for _ in (55, 80, 7474)}),
            call("pi-shifted.bam", wdir,
                 {_: self.sma._molecules_todo[_] for _ in (8884,)}),
        ])
        self.assertEqual(
            list(self.sma._per_molecule_bam_generator),
            [55, 80, 7474, 8884]
        )

    @patch("pacbio_data_processing.sm_analysis.split_bam_file_in_molecules")
    def test__split_bam_only_sets_empty_generator_if_disabled(
            self, psplit_bam):
        self.sma._do_split_bam = False
        self.sma._split_bam()
        psplit_bam.assert_not_called()
        self.assertEqual(list(self.sma._per_molecule_bam_generator), [])

    @patch("pacbio_data_processing.sm_analysis.cleanup_molecules")
    def test__filter_molecules_calls_cleanup_molecules(
            self, pcleanup_molecules):
        self.sma._per_molecule_bam_generator = (
            (_, Molecule(_)) for _ in range(5)
        )
        self.sma._molecules_todo = {_: Molecule(_) for _ in range(5)}
        pcleanup_molecules.return_value = (
            (_, Molecule(_)) for _ in range(5)
        )
        self.sma.summary_report = Mock()
        with self.assertLogs() as cm:
            self.sma._filter_molecules()
        pcleanup_molecules.assert_called_once_with(
            self.sma._per_molecule_bam_generator
        )
        self.assertEqual(
            list(self.sma._filtered_molecules_generator),
            list((_, Molecule(_)) for _ in range(5))
        )
        self.assertEqual(
            cm.output,
            ["INFO:root:[filter] Sieving molecules from input BAM "
             "before the IPD analysis"]
        )

    @patch("pacbio_data_processing.sm_analysis.cleanup_molecules")
    def test__filter_molecules_updates_molecules_todo_and_summary_report(
            self, pcleanup_molecules):
        mols_todo = {4: Molecule(4), 5: Molecule(5),
                     6: Molecule(6), 9: Molecule(9)}
        self.sma._molecules_todo = mols_todo
        self.sma._per_molecule_bam_generator = iter(
            [(k, k) for k, v in mols_todo.items()]
        )
        pcleanup_molecules.return_value = iter(
            [(4, Molecule(4)), (6, Molecule(6))]
        )
        self.sma.summary_report = Mock()
        self.sma._filter_molecules()
        self.assertEqual(
            self.sma._molecules_todo,
            {4: Molecule(4), 6: Molecule(6)}
        )
        self.assertEqual(self.sma.summary_report.filtered_out_mols, {5, 9})

    @patch("pacbio_data_processing.sm_analysis.cleanup_molecules")
    def test__filter_molecules_does_nothing_if_disabled(
            self, pcleanup_molecules):
        self.sma._molecules_todo = {_: Molecule(_) for _ in range(8)}
        self.sma._per_molecule_bam_generator = range(4)
        self.sma._do_filter_molecules = False
        self.sma.summary_report = Mock()
        self.sma._filter_molecules()
        pcleanup_molecules.assert_not_called()
        self.assertEqual(
            self.sma._filtered_molecules_generator,
            self.sma._per_molecule_bam_generator
        )
        self.assertEqual(self.sma.summary_report.filtered_out_mols, set())

    @patch("pacbio_data_processing.sm_analysis.BamFile")
    @patch("pacbio_data_processing.sm_analysis.count_subreads_per_molecule")
    def test__collect_statistics_sets_subreads_from_filtered_data(
            self, pcount_subreads, pBamFile):
        self.sma._filtered_molecules_generator = iter(
            (
                (1, Molecule(1, "a")),
                (2, Molecule(2, "b")),
                (3, Molecule(3, "c"))
            )
        )
        bam_a, bam_b, bam_c = Mock(), Mock(), Mock()
        pBamFile.side_effect = (bam_a, bam_b, bam_c)
        pcount_subreads.side_effect = [
            {1: Counter({"+": 3, "-": 5}), 11: Counter({"+": 23, "-": 9})},
            {2: Counter({"+": 13, "-": 15}), 22: Counter({"+": 43})},
            {1: Counter({"+": 2, "-": 7}), 3: Counter({"+": 23, "-": 25})},
        ]
        self.sma._collect_statistics()
        stats = self.sma.filtered_bam_statistics
        self.assertEqual(
            dict(stats["subreads"]),
            {
                1: Counter({"+": 5, "-": 12}),
                2: Counter({"+": 13, "-": 15}),
                3: Counter({"+": 23, "-": 25}),
                11: Counter({"+": 23, "-": 9}),
                22: Counter({"+": 43}),
            }
        )
        pBamFile.assert_has_calls([call("a"), call("b"), call("c")])
        pcount_subreads.assert_has_calls(
            [call(bam_a), call(bam_b), call(bam_c)]
        )

    @patch("pacbio_data_processing.sm_analysis.count_subreads_per_molecule")
    def test__collect_statistics_sets_empty_dictlike_attr_if_disabled(
            self, pcount_subreads):
        self.sma._do_collect_statistics = False
        self.sma._collect_statistics()
        stats = self.sma.filtered_bam_statistics
        self.assertEqual(dict(stats["subreads"]), {})
        pcount_subreads.assert_not_called()

    @patch("pacbio_data_processing.sm_analysis.BamFile")
    @patch("pacbio_data_processing.sm_analysis.count_subreads_per_molecule")
    def test__collect_statistics_restores_filtered_molecules_generator(
            self, pcount_subreads, pBamFile):
        self.sma._filtered_molecules_generator = iter(
            ((1, Molecule(1, "f")), (2, Molecule(2, "c")))
        )
        self.sma._collect_statistics()
        self.assertEqual(
            list(self.sma._filtered_molecules_generator),
            [(1, Molecule(1, "f")), (2, Molecule(2, "c"))]
        )

    @patch("pacbio_data_processing.sm_analysis.gen_index_single_molecule_bams")
    def test__generate_indices_calls_generator_and_sets_attribute(
            self, pindex_bams):
        molecules = (7, 9, "hello", "IT's", "me")
        self.sma._filtered_molecules_generator = molecules
        self.sma._generate_indices()
        pindex_bams.assert_called_once_with(
            molecules, self.params.pbindex_path)
        self.assertEqual(
            self.sma._indexed_molecules_generator,
            pindex_bams.return_value
        )

    @patch("pacbio_data_processing.sm_analysis.gen_index_single_molecule_bams")
    def test__generate_indices_does_nothing_if_disabled(
            self, pindex_bams):
        self.sma._do_generate_indices = False
        self.sma._generate_indices()
        pindex_bams.assert_not_called()

    @patch("pacbio_data_processing.sm_analysis.multi_ipd_summary")
    def test__ipd_analysis_calls_generator_and_sets_attribute(
            self, pmulti_ipd_summary):
        molecules = (9, "hello", "iT's", 43, "me")
        self.sma._indexed_molecules_generator = molecules
        self.sma._ipd_analysis()
        pmulti_ipd_summary.assert_called_once_with(
            molecules,
            self.sma.parameters.fasta,
            self.sma.parameters.ipdsummary_path,
            self.sma.parameters.num_simultaneous_ipdsummarys,
            self.sma.parameters.num_workers_per_ipdsummary,
            self.sma.parameters.modification_types,
            self.sma.parameters.ipd_model
        )
        self.assertEqual(
            self.sma._ipd_processed_molecules,
            pmulti_ipd_summary.return_value
        )

    @patch("pacbio_data_processing.sm_analysis.multi_ipd_summary")
    def test__ipd_analysis_does_nothing_if_disabled(
            self, pmulti_ipd_summary):
        self.sma._do_ipd_analysis = False
        self.sma._ipd_analysis()
        pmulti_ipd_summary.assert_not_called()

    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
           "._fix_positions_in_molecules")
    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
           "._fix_positions_in_gffs")
    def test_fix_positions_delegates_to_aux_methods(
            self, pfix_gffs, pfix_mols):
        self.sma._fix_positions()
        pfix_gffs.assert_called_once_with()
        pfix_mols.assert_called_once_with()

    @patch("pacbio_data_processing.sm_analysis.pishift_back_positions_in_gff")
    def test_fix_positions_in_gffs_if_undefined_ipd_processed_molecules(
            self, pshift):
        self.sma._fix_positions_in_gffs()
        pshift.assert_not_called()

    @patch("pacbio_data_processing.sm_analysis.pishift_back_positions_in_gff")
    def test_fix_positions_in_gffs_if_ipd_processed_molecules(
            self, pshift):
        mols = [Molecule(_) for _ in range(5)]
        for idx in range(0, 5, 2):
            mols[idx].gff_path = f"{idx}.gff"
        for idx in range(5):
            if idx in (2, 4):
                mols[idx].variant = "pi-shifted"
            else:
                mols[idx].variant = "straight"
        self.sma._ipd_processed_molecules = zip(range(5), mols)
        self.sma._fix_positions_in_gffs()
        pshift.assert_has_calls(
            [call(f"{idx}.gff") for idx in (2, 4)]
        )
        self.assertEqual(pshift.call_count, 2)

    def test_fix_positions_in_molecules(self):
        todo = {i: Molecule(i) for i in range(5)}
        for i in range(5):
            mol = todo[i]
            mol.reference = "A"*57
            if i in (0, 1, 4):
                mol.variant = "straight"
            else:
                mol.variant = "pi-shifted"
            mol.start = 10*i+1
        self.sma._molecules_todo = todo
        self.sma._fix_positions_in_molecules()
        for i in range(5):
            mol = todo[i]
            if i in (0, 1, 4):
                self.assertEqual(int(mol.start), 10*i+1)
            elif i == 2:
                self.assertEqual(int(mol.start), 49)
            elif i == 3:
                self.assertEqual(int(mol.start), 2)

    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
           ".produce_methylation_report")
    @patch("pacbio_data_processing.sm_analysis.add_to_own_output")
    @patch("pacbio_data_processing.sm_analysis.join_gffs")
    def test__dump_results(
            self, pjoin_gffs, padd_to_own_output, pproduce_methylation_report):
        gffs = (3, "m", {3})
        self.sma.summary_report = Mock()
        self.sma._ipd_processed_molecules = gffs
        self.sma._molecules_todo = {"", "45", "wwww2"}
        self.sma._dump_results()
        pjoin_gffs.assert_called_once_with(
            gffs, self.sma.parameters.joint_gff_filename)
        padd_to_own_output.assert_called_once_with(
            pjoin_gffs.return_value,
            self.sma.parameters.one_line_per_mod_filename,
            self.sma.parameters.modification_types,
        )
        pproduce_methylation_report.assert_called_once_with()
        self.assertEqual(
            self.sma.summary_report.raw_detections,
            self.sma.parameters.one_line_per_mod_filename
        )
        self.assertEqual(
            self.sma.summary_report.gff_result,
            self.sma.parameters.joint_gff_filename
        )
        self.sma.summary_report.save.assert_called_once_with(
            self.sma.parameters.summary_report_html_filename
        )

    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
           ".produce_methylation_report")
    @patch("pacbio_data_processing.sm_analysis.add_to_own_output")
    @patch("pacbio_data_processing.sm_analysis.join_gffs")
    def test__dump_results_skips_joint_gffs_and_own_output_if_disabled(
            self, pjoin_gffs, padd_to_own_output, pproduce_methylation_report):
        self.sma._do_create_own_output = False
        self.sma.summary_report = Mock()
        self.sma._dump_results()
        pjoin_gffs.assert_not_called()
        padd_to_own_output.assert_not_called()

    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
               ".produce_methylation_report")
    @patch("pacbio_data_processing.sm_analysis.add_to_own_output")
    @patch("pacbio_data_processing.sm_analysis.join_gffs")
    def test__dump_results_skips_methylation_report_if_disabled(
            self, pjoin_gffs, padd_to_own_output, pproduce_methylation_report):
        self.sma._do_produce_methylation_report = False
        self.sma._ipd_processed_molecules = Mock()
        self.sma.summary_report = Mock()
        self.sma._dump_results()
        pproduce_methylation_report.assert_not_called()

    @patch("pacbio_data_processing.sm_analysis.shutil.copytree")
    def test_backup_temp_dir_if_needed_copies_temp_dir(
            self, pcopytree):
        Wdir = namedtuple("Wdir", ["name"])
        wdir = "/a/csqe.3"
        self.sma._workdir = Wdir(name=wdir)
        self.sma.parameters.keep_temp_dir = True
        self.sma.parameters.partition = None
        self.sma._backup_temp_dir_if_needed()
        pcopytree.assert_called_once_with(Path(wdir), Path("/a/csqe.3.backup"))
        pcopytree.reset_mock()
        self.sma.parameters.partition = (1, 7)
        self.sma._backup_temp_dir_if_needed()
        pcopytree.assert_called_once_with(
            Path(wdir), Path("/a/csqe.3-partition_1of7.backup"))

    @patch("pacbio_data_processing.sm_analysis.shutil.copytree")
    def test_backup_temp_dir_if_needed_logs(
            self, pcopytree):
        tmpdir = Path("csqe")
        backup = Path("csqe.backup")
        self.sma.parameters.partition = None
        self.sma._workdir = tmpdir
        with self.assertLogs(level="DEBUG") as cm:
            self.sma._backup_temp_dir_if_needed()
        self.assertEqual(
            cm.output, [f"DEBUG:root:Copied temporary dir to: '{backup}'"])

    @patch("pacbio_data_processing.sm_analysis.shutil.copytree")
    def test_backup_temp_dir_if_needed_does_nothing_if_not_needed(
            self, pcopytree):
        self.sma.parameters.keep_temp_dir = False
        self.sma._backup_temp_dir_if_needed()
        pcopytree.assert_not_called()

    @patch("pacbio_data_processing.sm_analysis.TemporaryDirectory")
    def test_workdir_attribute(self, ptempdir):
        wdir1 = self.sma.workdir
        wdir2 = self.sma.workdir
        ptempdir.assert_called_once_with(dir=".")
        self.assertEqual(wdir1, ptempdir.return_value)
        self.assertEqual(wdir1, wdir2)

    @patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
               "_discard_molecules_with_seq_mismatch")
    @patch("pacbio_data_processing.sm_analysis"
               ".map_molecules_with_highest_sim_ratio")
    def test_collect_suitable_molecules_from_ccs(
            self, pmap_molecules, pdiscard):
        straight_map = {i: Molecule(i) for i in range(5)}
        pishifted_map = {i: Molecule(i) for i in range(0, 10, 2)}
        pmap_molecules.side_effect = (straight_map, pishifted_map)
        def discard(x):
            mols = {}
            for k, v in x.items():
                if v.variant == "straight":
                    if k<3:
                        mols[k] = v
                elif v.variant == "pi-shifted":
                    if k<7:
                        mols[k] = v
            return mols
        pdiscard.side_effect = discard
        self.sma.aligned_ccs_bam_file = {
            "straight": Path("ecco_fatto.bam"),
            "pi-shifted": Path("pi.ecco_fatto.bam"),
        }
        self.sma.reference = {
            "straight": "S"*10,
            "pi-shifted": "π"*10
        }
        self.sma.summary_report = Mock()
        with self.assertLogs(level="DEBUG") as cm:
            mols = self.sma._collect_suitable_molecules_from_ccs()
        self.assertEqual(len(mols), 5)
        for mol_id in range(3):
            self.assertEqual(mols[mol_id].variant, "straight")
            self.assertEqual(mols[mol_id].reference, "S"*10)
        for mol_id in range(4, 8, 2):
            self.assertEqual(mols[mol_id].variant, "pi-shifted")
            self.assertEqual(mols[mol_id].reference, "π"*10)
        pmap_molecules.assert_has_calls(
            [call(Path("ecco_fatto.bam")), call(Path("pi.ecco_fatto.bam"))]
        )
        self.assertEqual(
            cm.output,
            [
                ("INFO:root:Generating molecules "
                 "mapping from aligned CCS file"),
                ("DEBUG:root:ccs lines (aligned): 5 molecules found"),
                ("INFO:root:Generating molecules "
                 "mapping from pi-shifted aligned CCS file"),
                ("DEBUG:root:ccs lines (pi-shifted aligned): 5 molecules "
                     "found"),
                ("INFO:root:Molecule 8 discarded due to DNA sequence "
                     "mismatch with reference"),
                ("INFO:root:Molecule 3 discarded due to DNA sequence "
                     "mismatch with reference"),
            ]
        )
        self.assertEqual(self.sma.summary_report.mols_dna_mismatches, {3, 8})
        self.assertEqual(
            self.sma.summary_report.mols_used_in_aligned_ccs,
            set(range(5))|set(range(0, 10, 2))
        )

    def test_disable_pi_shifted_analysis(self):
        with self.assertLogs() as cm:
            self.sma._disable_pi_shifted_analysis()
        self.assertEqual(
            cm.output,
            ["WARNING:root:...therefore the pi-shifted analysis is disabled"]
        )
        self.assertEqual(self.sma.variants, ("straight",))

    @patch("pacbio_data_processing.sm_analysis.BamFile")
    @patch("pacbio_data_processing.sm_analysis.Path")
    def test_exists_pi_shifted_variant_from_aligned_input(
            self, pPath, pBamFile):
        combinations = {
            (True, True): self.assertTrue,
            (True, False): self.assertFalse,
            (False, True): self.assertFalse,
        }
        for (aligned, exists), method in combinations.items():
            pBamFile.return_value.is_aligned = aligned
            pPath.return_value.exists.return_value = exists
            method(self.sma._exists_pi_shifted_variant_from_aligned_input())
            pBamFile.assert_called_once_with(
                self.sma.aligned_input_bam_file["pi-shifted"])
            pPath.assert_called_once_with(
                self.sma.aligned_input_bam_file["pi-shifted"])
            pBamFile.reset_mock()
            pPath.reset_mock()

    @patch("pacbio_data_processing.sm_analysis."
           "try_computations_with_variants_until_done")
    def test_CCS_bam_file_attribute(self, ptry):
        self.sma.CCS_bam_file
        ptry.assert_called_once_with(
            generate_CCS_file,
            (None,),
            self.sma.ccs,
            self.sma.input_bam_file,
            self.sma.parameters.CCS_bam_file
        )
        self.assertEqual(
            self.sma.CCS_bam_file,
            self.sma.parameters.CCS_bam_file
        )
        # Check that we can write the attribute:
        self.sma.input_bam_file = Path("/tmp/cuchi.bam")
        expected_ccs = Path("/tmp/ccs.cuchi.bam")
        ptry.reset_mock()
        self.sma.CCS_bam_file = None
        ptry.assert_called_once_with(
            generate_CCS_file,
            (None,),
            self.sma.ccs,
            self.sma.input_bam_file,
            self.sma.CCS_bam_file
        )
        self.assertEqual(
            expected_ccs,
            self.sma.CCS_bam_file
        )


@patch("pacbio_data_processing.sm_analysis.time.sleep")
@patch("pacbio_data_processing.sm_analysis.generate_CCS_file")
@patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
       "_exists_pi_shifted_variant_from_aligned_input")
@patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
       "_disable_pi_shifted_analysis")
@patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis."
       "_align_bam_if_no_candidate_found")
@patch("pacbio_data_processing.sm_analysis.BamFile")
class EnsureInputBamAlignedTestCase(unittest.TestCase):
    def create_sma_and_keep_logs(self, params):
        params.fasta = "le.fasta"
        with (patch("pacbio_data_processing.sm_analysis.DNASeq"),
              patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._ensure_ccs_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis.SummaryReport")):
            with self.assertLogs() as cm:
                sma = SingleMoleculeAnalysis(params)
        return sma, cm

    def test_if_input_bam_aligned_and_pi_shifted_not_found(
            self, pBamFile, palign_if, pdisable, pexists, pgen_ccs, psleep):
        pBamFile.return_value.is_aligned = True
        pexists.return_value = False
        params = Mock()
        inbams = ("/tmp/one.bam", "/tmp/blasr.one.bam")
        for inbam in inbams:
            params.input_bam_file = inbam
            sma, cm = self.create_sma_and_keep_logs(params)
            palign_if.assert_not_called()
            pdisable.assert_called_once_with()
            self.assertEqual(sma.aligned_input_bam_file["straight"], inbam)
            self.assertEqual(
                sma.aligned_input_bam_file["pi-shifted"], None)
            self.assertEqual(
                cm.output,
                ["INFO:root:The input BAM is aligned",
                 "INFO:root:...but no pi-shifted aligned version of the input "
                 "BAM was found."
                 ]
            )
            pdisable.reset_mock()

    def test_if_input_bam_aligned_and_pi_shifted_found(
            self, pBamFile, palign_if, pdisable, pexists, pgen_ccs, psleep):
        pBamFile.return_value.is_aligned = True
        pexists.return_value = True
        params = Mock()
        inbam = "/tmp/one.bam"
        pi_shifted = "/tmp/pi-shifted.blasr.one.bam"
        params.input_bam_file = inbam
        sma, cm = self.create_sma_and_keep_logs(params)
        palign_if.assert_not_called()
        pdisable.assert_not_called()
        self.assertEqual(sma.aligned_input_bam_file["straight"], inbam)
        self.assertEqual(sma.aligned_input_bam_file["pi-shifted"], pi_shifted)
        self.assertEqual(
            cm.output,
            ["INFO:root:The input BAM is aligned",
             ("INFO:root:...a possible pi-shifted aligned version of the "
              f"input BAM was found: '{pi_shifted}'. It will be used.")
             ]
        )

    def test_logs_and_delegates_if_not_aligned_and_blasr_runs(
            self, pBamFile, palign_if, pdisable, pexists, pgen_ccs, psleep):
        pBamFile.return_value.is_aligned = False
        params = Mock()
        inbam = "/tmp/one.bam"
        params.input_bam_file = inbam
        sma, cm = self.create_sma_and_keep_logs(params)
        pdisable.assert_not_called()
        palign_if.assert_has_calls(
            [call(pBamFile.return_value, "input", variant="straight"),
             call(pBamFile.return_value, "input", variant="pi-shifted")]
        )
        self.assertEqual(
            cm.output,
            ["INFO:root:The input BAM is NOT aligned"]
        )

    def test_logs_and_delegates_until_blasr_runs_if_not_aligned(
            self, pBamFile, palign_if, pdisable, pexists, pgen_ccs, psleep):
        pBamFile.return_value.is_aligned = False
        params = Mock()
        inbam = "/tmp/one.bam"
        params.input_bam_file = inbam
        blasr_trials = {
            "straight": iter([None, "whatever"]),
            "pi-shifted": iter([None, None, None, "something"])
        }

        def align_if(inbam, bam_type, variant):
            return next(blasr_trials[variant])
        palign_if.side_effect = align_if
        sma, cm = self.create_sma_and_keep_logs(params)
        pdisable.assert_not_called()
        palign_if.assert_has_calls(
            [call(pBamFile.return_value, "input", variant="straight"),
             call(pBamFile.return_value, "input", variant="pi-shifted"),
             call(pBamFile.return_value, "input", variant="straight"),
             call(pBamFile.return_value, "input", variant="pi-shifted"),
             call(pBamFile.return_value, "input", variant="pi-shifted"),
             call(pBamFile.return_value, "input", variant="pi-shifted")
             ]
        )
        psleep.assert_has_calls([call(10), call(20), call(40)])
        self.assertEqual(
            cm.output,
            ["INFO:root:The input BAM is NOT aligned"]
        )


@patch("pacbio_data_processing.sm_analysis.generate_CCS_file")
@patch("pacbio_data_processing.sm_analysis.Path.exists")
@patch("pacbio_data_processing.sm_analysis.BamFile")
class AlignBamIfNoCandidateFoundTestCase(unittest.TestCase):
    def setUp(self):
        params = Mock()
        params.fasta = "le.fasta"
        params.CCS_bam_file = "/tmp/ccs.one.bam"
        self.inbam = "/tmp/one.bam"
        self.aligned_bam_name = {
            "straight": f"/tmp/{BLASR_PREF}one.bam",
            "pi-shifted": f"/tmp/pi-shifted.{BLASR_PREF}one.bam",
        }
        self.aligned_generic_name = {
            "straight": "aligned",
            "pi-shifted": "pi-shifted aligned",
        }
        params.input_bam_file = self.inbam
        self.params = params

    def create_sma_and_keep_logs(self):
        with (patch("pacbio_data_processing.sm_analysis.DNASeq"),
              patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._ensure_input_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis.generate_CCS_file"),
              patch("pacbio_data_processing.sm_analysis.SummaryReport"),
              patch("pacbio_data_processing.sm_analysis.Blasr")):
            sma = SingleMoleculeAnalysis(self.params)
        sma.blasr = MagicMock()
        return sma

    def test_sets_attr_if_theres_correct_aligned_file(
            self, pBamFile, pexists, pgen_ccs):
        input_bam = Mock()
        aligned_bam = Mock()
        other_bam = Mock()
        other_bam.bam_file_name = "/tmp/other.bam"

        def ipavo(bam):
            if bam == input_bam:
                return True
            return False
        aligned_bam.is_plausible_aligned_version_of.side_effect = ipavo
        pexists.return_value = True

        def create_BamFile(path):
            "This implicitly ensures that the correct BamFile is created"
            if path in self.aligned_bam_name.values():
                return aligned_bam
            else:
                return other_bam
        pBamFile.side_effect = create_BamFile
        sma = self.create_sma_and_keep_logs()
        input_bam.bam_file_name = sma.input_bam_file
        bam_type = "input"
        for variant, aligned_bam_name in self.aligned_bam_name.items():
            aligned_generic_name = self.aligned_generic_name[variant]
            with self.assertLogs() as cm:
                res = sma._align_bam_if_no_candidate_found(
                    input_bam, bam_type, variant)
            sma.blasr.assert_not_called()
            self.assertEqual(
                sma.aligned_input_bam_file[variant], aligned_bam_name)
            self.assertEqual(
                cm.output,
                [(f"INFO:root:...but a possible {aligned_generic_name} version"
                  f" of the {bam_type} BAM was found: '{aligned_bam_name}'. "
                  "It will be used.")]
            )
            self.assertEqual(res, aligned_bam_name)

    def test_calls_blasr_if_missing_aligned_file(
            self, pBamFile, pexists, pgen_ccs):
        pexists.return_value = False
        sma = self.create_sma_and_keep_logs()
        bam_type = "input"
        for variant, aligned_bam_name in self.aligned_bam_name.items():
            aligned_generic_name = self.aligned_generic_name[variant]
            inbam = Mock()
            inbam.bam_file_name = sma.input_bam_file
            with self.assertLogs() as cm:
                res = sma._align_bam_if_no_candidate_found(
                    inbam, bam_type, variant)
            sma.blasr.assert_called_once_with(
                Path(inbam.bam_file_name),
                sma.fasta[variant],
                Path(aligned_bam_name),
                self.params.nprocs_blasr
            )
            self.assertEqual(
                sma.aligned_input_bam_file[variant], aligned_bam_name)
            self.assertEqual(
                cm.output,
                [(f"INFO:root:...since no {aligned_generic_name} "
                  f"version of the {bam_type} BAM was found, one has been "
                  f"produced and it will be used: '{aligned_bam_name}'")
                 ]
            )
            sma.blasr.reset_mock()
            self.assertEqual(res, aligned_bam_name)

    def test_calls_blasr_if_input_not_aligned_and_not_aligned_file_found(
            self, pBamFile, pexists, pgen_ccs):
        input_bam = Mock()
        aligned_bam = Mock()
        aligned_bam.bam_file_name = "whatever.bam"
        aligned_bam.is_plausible_aligned_version_of.return_value = False
        pBamFile.return_value = aligned_bam
        pexists.return_value = True
        sma = self.create_sma_and_keep_logs()
        input_bam.bam_file_name = sma.input_bam_file
        bam_type = "input"
        for variant, aligned_bam_name in self.aligned_bam_name.items():
            aligned_generic_name = self.aligned_generic_name[variant]
            with self.assertLogs() as cm:
                res = sma._align_bam_if_no_candidate_found(
                    input_bam, bam_type, variant)
            sma.blasr.assert_called_once_with(
                Path(input_bam.bam_file_name),
                sma.fasta[variant],
                Path(aligned_bam_name),
                self.params.nprocs_blasr
            )
            self.assertEqual(
                sma.aligned_input_bam_file[variant], aligned_bam_name)
            self.assertEqual(
                cm.output,
                [(f"INFO:root:...since no {aligned_generic_name} version "
                  "of the input BAM was found, one has been produced and "
                  f"it will be used: '{aligned_bam_name}'")
                 ]
            )
            sma.blasr.reset_mock()
            self.assertEqual(res, aligned_bam_name)

    def test_when_blasr_cannot_run_it_returns_None(
            self, pBamFile, pexists, pgen_ccs):
        input_bam = Mock()
        aligned_bam = Mock()
        aligned_bam.bam_file_name = self.params.CCS_bam_file
        pBamFile.return_value = aligned_bam
        pexists.return_value = False
        sma = self.create_sma_and_keep_logs()
        sma.blasr.return_value = None
        input_bam.bam_file_name = sma.input_bam_file
        bam_type = "input"
        for variant, aligned_bam_name in self.aligned_bam_name.items():
            res = sma._align_bam_if_no_candidate_found(
                input_bam, bam_type, variant)
            sma.blasr.assert_called_once_with(
                Path(input_bam.bam_file_name),
                sma.fasta[variant],
                Path(aligned_bam_name),
                self.params.nprocs_blasr
            )
            self.assertEqual(
                sma.aligned_input_bam_file[variant], aligned_bam_name)
            sma.blasr.reset_mock()
            self.assertIs(res, None)


class EnsureCCSBamAlignedTestCase(unittest.TestCase):
    def setUp(self):
        self.params = Mock()
        self.params.input_bam_file = "whatever.bam"
        self.params.fasta = "mysweet.fasta"
        self.params.CCS_bam_file = None
        self.params.aligned_CCS_bam_file = None
        with (patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._ensure_input_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis."
                    "SingleMoleculeAnalysis._ensure_ccs_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis.DNASeq"),
              patch("pacbio_data_processing.sm_analysis.SingleMolecule"
                    "Analysis._init_summary")):
            self.sma = SingleMoleculeAnalysis(self.params)
        self.sma.summary_report = Mock()

    @patch("pacbio_data_processing.sm_analysis.BamFile")
    @patch("pacbio_data_processing.sm_analysis."
           "try_computations_with_variants_until_done")
    def test_logs_and_delegates(self, ptry_computations, pBamFile):
        self.sma.CCS_bam_file = Path("ccss.bam")
        with self.assertLogs() as cm:
            with patch("pacbio_data_processing.sm_analysis.generate_CCS_file"):
                self.sma._ensure_ccs_bam_aligned()
        self.assertIn(
            (
                "INFO:root:The methylation analysis requires aligned CCS "
                "files --for all variants-- to proceed. Trying to get "
                "them..."
            ),
            cm.output
        )
        ptry_computations.assert_has_calls(
            [call(self.sma._align_bam_if_no_candidate_found, self.sma.variants,
                  pBamFile.return_value, "ccs")]
        )
        pBamFile.assert_called_once()
        self.assertEqual(Path(pBamFile.call_args[0][0]), Path("ccss.bam"))
        self.assertEqual(
            self.sma.summary_report.aligned_ccs_bam_files,
            self.sma.aligned_ccs_bam_file
        )


class DiscardMoleculesWithSeqMismatchTestCase(unittest.TestCase):
    def setUp(self):
        self.params = Mock()
        self.params.input_bam_file = "whatever.bam"
        self.params.fasta = "mysweet.fasta"
        self.params.CCS_bam_file = None
        self.params.aligned_CCS_bam_file = None
        with (patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._ensure_input_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis."
                    "SingleMoleculeAnalysis._ensure_ccs_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis.DNASeq"),
              patch("pacbio_data_processing.sm_analysis.SingleMolecule"
                    "Analysis._init_summary")):
            self.sma = SingleMoleculeAnalysis(self.params)
        self.sma.reference = {
            "straight": "hfdkeindnajegkajswiwew",
            "pi-shifted": "abcdefghijklmn"
        }
        self.molecules_in_ccs = {
            12: Molecule(12, None, tuple(["x"]*3+[b"4"]+["x"]*5+[b"keind"])),
            23: Molecule(23, None, tuple(["x"]*3+[b"8"]+["x"]*5+[b"pan"])),
            56: Molecule(56, None, tuple(["x"]*3+[b"12"]+["x"]*5+[b"egk"])),
            63: Molecule(63, None, tuple(["x"]*3+[b"5"]+["x"]*5+[b"efgh"])),
            90: Molecule(90, None, tuple(["x"]*3+[b"10"]+["x"]*5+[b"gdh"])),
        }
        for i in (12, 23, 56):
            self.molecules_in_ccs[i].variant = "straight"
        for i in (63, 90):
            self.molecules_in_ccs[i].variant = "pi-shifted"
        self.good_mols = {12, 56, 63}

    def test_mismatching_molecules_removed_and_logged(self):
        after_discard = self.sma._discard_molecules_with_seq_mismatch(
            self.molecules_in_ccs)
        self.assertEqual(set(after_discard.keys()), self.good_mols)


class CrosscheckMoleculesInPartitionWithCcsTestCase(unittest.TestCase):
    def setUp(self):
        self.params = Mock()
        self.params.input_bam_file = "whatever.bam"
        self.params.fasta = "mysweet.fasta"
        self.params.CCS_bam_file = None
        self.params.aligned_CCS_bam_file = None
        with (patch("pacbio_data_processing.sm_analysis."
                    "SingleMoleculeAnalysis._ensure_input_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis."
                    "SingleMoleculeAnalysis._ensure_ccs_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis.DNASeq"),
              patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._init_summary")):
            self.sma = SingleMoleculeAnalysis(self.params)
        self.original_molecules_in_ccs = {
            12: ["a"], 23: ["v"], 44: ["ss"], 56: ["z"], 123: ("cuate"),
        }
        self.molecules_in_ccs = self.original_molecules_in_ccs.copy()
        self.sma._molecule_ids_todo = {
            "straight": {b"23", b"56", b"97"},
            "pi-shifted": {b"123"},
        }
        self.expected_mols = {23, 56, 123}
        self.unexpected_mols = {12, 44, 97}

    def test_molecules_todo_crosschecked_with_ccs(self):
        self.sma._crosscheck_molecules_in_partition_with_ccs(
            self.molecules_in_ccs)
        for mol_id in self.expected_mols:
            self.assertEqual(
                self.sma._molecules_todo[mol_id],
                self.original_molecules_in_ccs[mol_id]
            )
        for mol_id in self.unexpected_mols:
            self.assertNotIn(mol_id, self.sma._molecules_todo)


class KeepOnlyPIShiftedMoleculesCrossingOriginTestCase(unittest.TestCase):
    def setUp(self):
        self.params = Mock()
        self.params.input_bam_file = "whatever.bam"
        self.params.fasta = "mysweet.fasta"
        self.params.CCS_bam_file = None
        self.params.aligned_CCS_bam_file = None
        with (patch("pacbio_data_processing.sm_analysis.SingleMoleculeAnalysis"
                    "._ensure_input_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis."
                    "SingleMoleculeAnalysis._ensure_ccs_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis.DNASeq"),
              patch("pacbio_data_processing.sm_analysis.SingleMolecule"
                    "Analysis._init_summary")):
            self.sma = SingleMoleculeAnalysis(self.params)
        best_ccs_line = [b"", b"", b"", b"", b"", b"", b"", b"", b"",
                         b"1234", b""]
        mol_ids = (101, 102, 201, 202, 301, 302)
        self.all_mols = {_: Molecule(_, "", best_ccs_line) for _ in mol_ids}
        for mol_id in mol_ids:
            mol = self.all_mols[mol_id]
            mol.reference = "1234567890a"
            if mol_id < 200:
                mol.start = 4
            elif mol_id < 300:
                mol.start = 1
            else:
                mol.start = 6
            if mol_id % 2 == 0:
                mol.variant = "pi-shifted"
            else:
                mol.variant = "straight"
        self.good_mol_ids = {101, 102, 201, 301}

    def test_taken_molecules(self):
        mols = self.sma._keep_only_pishifted_molecules_crossing_origin(
            self.all_mols)
        self.assertEqual(set(mols.keys()), self.good_mol_ids)


@patch("pacbio_data_processing.sm_analysis.csv.writer")
@patch("pacbio_data_processing.sm_analysis.open", create=True)
class AddToOwnOutputTestCase(unittest.TestCase):
    def setUp(self):
        self.gffs = [
            Path("sample.23.gff"),
            Path("sample.28.gff"),
            Path("sample.140.gff")
        ]
        self.mock_open_instances = [
            mock_open().return_value,
            mock_open(read_data=TEST_DATA_GFF1).return_value,
            mock_open(read_data=TEST_DATA_GFF2).return_value,
            mock_open(read_data=TEST_DATA_GFF3).return_value,
        ]
        self.m6A_rows = [
            ["23", "m6A", "1742233", "21", "+", "8",
             "TATCGGTTCGAAAAAAACCGATCTGAATGTTGATCCCTGGA", "5.01", "4"],
            ["23", "m6A", "1742234", "23", "-", "7",
             "ATCCAGGGATCAACATTCAGATCGGTTTTTTTCGAACCGAT", "3.11", "5"],
            ["23", "m6A", "1742245", "20", "+", "8",
             "AAAAACCGATCTGAATGTTGATCCCTGGATTAATAAATATA", "4.43", "3"],
            ["140", "m6A", "2148146", "68", "-", "35",
             "CGCCCAGCCCCTGGAAGTTGATCGGACGACCAATCACCGCC", "6.38", "51"],
        ]
        self.m5A_rows = [
            ["140", "m5A", "2148145", "115", "+", "59",
             "AGGCGGTGATTGGTCGTCCGATCAACTTCCAGGGGCTGGGC", "5.40", "113"],
        ]

    def test_logs_expected_msg(self, mopen, mwriter):
        with self.assertLogs() as cm:
            add_to_own_output(
                ["ij.8.jul.cat"],
                "output_file.csv",
                ["hack", "heck"])
        self.assertEqual(
            cm.output,
            ["INFO:root:Own output 'output_file.csv' created"]
        )

    def test_creates_csvwriter(self, mopen, mwriter):
        mopen_write = mock_open()
        my_mopen = mock_open(read_data="s s djf g oeo eo eo eo e oeo 9")
        mopen.side_effect = [mopen_write.return_value, my_mopen.return_value]
        add_to_own_output([], "output_file.csv", ["hack", "heck"])
        mopen.assert_called_once_with("output_file.csv", "a")
        mwriter.assert_called_once_with(
            mopen_write.return_value, delimiter=",")

    def test_writes_proper_data(self, mopen, mwriter):
        mopen.side_effect = self.mock_open_instances
        add_to_own_output(self.gffs, "output_file.csv", ["m6A"])
        mwriter.return_value.writerow.assert_has_calls(
            [call(_) for _ in self.m6A_rows]
        )
        self.assertEqual(mwriter.return_value.writerow.call_count, 4)

    def test_various_modification_types(self, mopen, mwriter):
        mopen.side_effect = self.mock_open_instances
        add_to_own_output(self.gffs, "output_file.csv", ["m5A", "m6A"])
        mwriter.return_value.writerow.assert_has_calls(
            [call(_) for _ in self.m6A_rows[:-1]
             + self.m5A_rows+self.m6A_rows[-1:]]
        )
        self.assertEqual(mwriter.return_value.writerow.call_count, 5)


@patch("pacbio_data_processing.sm_analysis.MethylationReport")
@patch(
    "pacbio_data_processing.sm_analysis.map_molecules_with_highest_sim_ratio")
class ProduceMethylationReportTestCase(unittest.TestCase):
    """This test case is fully mocked up: its purpose is to
    ensure that the actual routines are properly called."""

    def setUp(self):
        self.params = Mock()
        self.params.only_produce_methylation_report = False
        self.params.one_line_per_mod_filename = "some.csv"
        self.params.modification_types = ["m6A"]
        self.params.input_bam_file = "whatever.bam"
        self.params.fasta = "mysweet.fasta"
        with (patch("pacbio_data_processing.sm_analysis.BamFile"),
              patch("pacbio_data_processing.sm_analysis.SingleMolecule"
                    "Analysis._ensure_ccs_bam_aligned"),
              patch("pacbio_data_processing.sm_analysis.DNASeq"),
              patch("pacbio_data_processing.sm_analysis.SingleMolecule"
                    "Analysis._init_summary")):
            self.sma = SingleMoleculeAnalysis(self.params)
        self.sma._molecules_todo = None
        self.sma._molecules_in_ccs = {"2": (2, 4)}
        self.sma.filtered_bam_statistics = {"subreads": {"c": Counter()}}
        self.sma.summary_report = Mock()

    def test_methylation_report_instance_created(
            self, pmap_molecules, pMethylationReport):
        self.params.modification_types = ["s", 8, "m00"]
        self.sma._molecules_todo = {2, "d", (1,)}
        self.sma.filtered_bam_statistics = {"subreads": {"a": Counter()}}
        self.sma.produce_methylation_report()
        pMethylationReport.assert_called_once_with(
            detections_csv="some.csv",
            molecules={2, "d", (1,)},
            modification_types=["s", 8, "m00"],
            filtered_bam_statistics=self.sma.filtered_bam_statistics,
        )

    def test_methylation_report_instances_save_called_and_summary_updated(
            self, pmap_molecules, pMethylationReport):
        self.sma.produce_methylation_report()
        pMethylationReport.return_value.save.assert_called_once_with()
        self.assertEqual(
            self.sma.summary_report.methylation_report,
            pMethylationReport.return_value.csv_name
        )

    def test_log_msg_with_file_name_if_report_correctly_generated(
            self, pmap_molecules, pMethylationReport):
        pMethylationReport.return_value.PRELOG = "abcd"
        pMethylationReport.return_value.csv_name = "mr.csv"
        with self.assertLogs() as cm:
            self.sma.produce_methylation_report()
        self.assertIn(
            "INFO:root:abcd Results saved to file 'mr.csv'", cm.output
        )


class GenerateCCSFileTestCase(unittest.TestCase):
    def setUp(self):
        ccs_bam = MagicMock()
        ccs_bam.__str__.return_value = "missing.pdp"
        ccs_bam.exists.side_effect = (False, True)
        self.ccs_bam = ccs_bam
        self.ccs = MagicMock()

    def test_output_created_succesfully(self):
        self.ccs.return_value = 0
        with self.assertLogs() as cm:
            result = generate_CCS_file(self.ccs, Path("in.bam"), self.ccs_bam)
        self.ccs.assert_called_once_with(Path("in.bam"), self.ccs_bam)
        self.assertEqual(
            [("WARNING:root:Aligned CCS file cannot be produced "
              "without CCS file. Trying to produce it...")],
            cm.output
        )
        self.assertEqual(result, self.ccs_bam)

    def test_ccs_program_could_not_be_called(self):
        self.ccs.return_value = None
        with self.assertLogs() as cm:
            result = generate_CCS_file(self.ccs, Path("in.bam"), self.ccs_bam)
        self.ccs.assert_called_once_with(Path("in.bam"), self.ccs_bam)
        self.assertEqual(
            [("WARNING:root:Aligned CCS file cannot be produced "
              "without CCS file. Trying to produce it...")],
            cm.output
        )
        self.assertEqual(result, None)

    def test_output_created_but_ccs_returning_error(self):
        self.ccs.return_value = 1
        with self.assertLogs() as cm:
            result = generate_CCS_file(self.ccs, Path("in.bam"), self.ccs_bam)
        self.ccs.assert_called_once_with(Path("in.bam"), self.ccs_bam)
        self.assertEqual(
            [("WARNING:root:Aligned CCS file cannot be produced "
              "without CCS file. Trying to produce it..."),
             (f"ERROR:root:Although the file '{self.ccs_bam}' has been "
              "generated, there was an error."),
             ("ERROR:root:It is advisable to check the correctness of "
              "the generated ccs file.")
             ],
            cm.output
        )
        self.assertEqual(result, self.ccs_bam)

    def test_output_not_created(self):
        self.ccs.return_value = 1
        with self.assertLogs() as cm:
            result = generate_CCS_file(self.ccs, Path("in.bam"), self.ccs_bam)
        self.ccs.assert_called_once_with(Path("in.bam"), self.ccs_bam)
        self.assertEqual(
            [("WARNING:root:Aligned CCS file cannot be produced "
              "without CCS file. Trying to produce it..."),
             (f"ERROR:root:Although the file '{self.ccs_bam}' has been "
              "generated, there was an error."),
             ("ERROR:root:It is advisable to check the correctness of "
              "the generated ccs file.")
             ],
            cm.output
        )
        self.assertEqual(result, self.ccs_bam)

    def test_if_ccs_file_exists_program_not_called(self):
        self.ccs_bam.exists.side_effect = (True, True)
        with self.assertLogs(level="DEBUG") as cm:
            result = generate_CCS_file(self.ccs, "in.bam", self.ccs_bam)
        self.ccs.assert_not_called()
        self.assertNotIn(
            (
                "WARNING:root:Aligned CCS file cannot be produced "
                "without CCS. Trying to produce it..."
            ),
            cm.output
        )
        self.assertIn(
            (
                f"DEBUG:root:CCS file '{self.ccs_bam}' found. Skipping its "
                "computation."
            ),
            cm.output
        )
        self.assertEqual(result, self.ccs_bam)

    def test_raises_if_ccs_file_not_done_after_program_call(self):
        self.ccs.return_value = 0
        self.ccs_bam.exists.side_effect = (False, False)
        with self.assertRaises(SMAPipelineError) as e:
            with self.assertLogs() as cm:
                generate_CCS_file(self.ccs, "in.bam", self.ccs_bam)
        self.assertEqual(
            cm.output,
            [("WARNING:root:Aligned CCS file cannot be produced "
              "without CCS file. Trying to produce it..."),
             f"CRITICAL:root:CCS BAM file '{self.ccs_bam}' "
             "could not be produced."]
        )
        self.assertEqual(
            str(e.exception),
            ("The Single Molecule Analysis cannot proceed without a CCS BAM "
             "file. Aborting.")
        )


@patch("pacbio_data_processing.sm_analysis.BamFile")
class MapMoleculesWithHighestSimRatioTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        attrs = [f"a{_}" for _ in range(19)]
        attrs[16] = "zmw"

        class BamLine(namedtuple("BamLine", attrs)):
            @property
            def molecule_id(self):
                return self.zmw.split(b":")[-1]
        cls.BamLine = BamLine

    def test_calls_bamfile(self, pBamFile):
        map_molecules_with_highest_sim_ratio("my.bam")
        pBamFile.assert_called_once_with("my.bam")

    def test_simple_dict_returned_with_simple_data(self, pBamFile):
        proto_bam_data = [
           " ".join(
               [f"{_}"]*5+[f"{_+1}="]+[f"x{_}d"]*10+[f"dd:dd:{_+1}"]+2*["fg"]
           ).encode() for _ in range(5)
        ]
        bam_data = [self.BamLine(*_) for _ in nested_split(proto_bam_data)]
        pBamFile.return_value.body = iter(bam_data)
        expected_dict = {
            _+1: Molecule(_+1, "juan.bam", bam_data[_]) for _ in range(5)
        }
        result = map_molecules_with_highest_sim_ratio("juan.bam")
        self.assertEqual(result, expected_dict)

    def test_subread_with_best_cigar_chosen(self, pBamFile):
        proto_bam_data = [
            " ".join(
                [f"{_}"]*5+[f"{_+1}={_+1}X"]+[f"x{_}d"]*10
                + ["dd:dd:105"] + 2*["fg"]
            ).encode() for _ in range(2)
        ] + [
            " ".join(
                [f"{_}"]*5+[f"{_+1}={3+1-_}D"]+[f"x{_}d"]*10
                + ["dd:dd:1050"] + 2*["fg"]
            ).encode() for _ in range(3)
        ]
        bam_data = [self.BamLine(*_) for _ in nested_split(proto_bam_data)]
        pBamFile.return_value.body = iter(bam_data)
        expected_dict = {
            105: Molecule(105, "juan.bam", bam_data[0]),
            1050: Molecule(1050, "juan.bam", bam_data[4]),
        }
        self.assertEqual(
            map_molecules_with_highest_sim_ratio("juan.bam"), expected_dict)


class MethylationReportTestCase(unittest.TestCase):
    REFERENCE = (
        "CATTGATCCCGGCACCAGGCTGCACGACGTTAACGATGATAAGACCAATAATCAGCGCGATG"
        "GTACT"
        + "A"*50 +
        "AAGTTCGGGCAAATGTTATCAACCCGCCGCGATCTTTTTCCACCGCATATTGCCGATCAGCT"
        "GGCGTTATTGCAGGACAAAGTTGCTCCGTTTGATGGCAAGCTGGCGAAGCAGCAGATTGAAGC"
        "TGCAATGGGCGGCTTGCCGGTAGAAGCGTGGTTTGACGATTTTGAAATCAAGCCGCTGGCTTC"
        "TGCTTCTATCGCCCAGGTTCATACCGCGCGATTGAAATCGAATGGTAAAGAGGTGGTGATTAA"
        "AGTCATCCGCCCGGATATTTTGCCGGTTATTAAAGCGGATCTGAAACTTATCTACCGTCTGGC"
        "TCGCTGGGTGCCGCGTTT"
        + "C"*50 +
        "AAAGGATCTGTAATTAGTCGACCAGCGGATCGAATGTTATAATACGCGCCAATAAAAACGGC"
        "TCAGATCTTCATCTGCCA"
        + "G"*50 +
        "ATTGCATCTGTAATTAGTCGACCAGCGGATGGAATGTTATAATACGCGCCAATTGCAACGGC"
        "TCAACTCAGCTCCTGCCA"
        + "T"*50 +
        "CTGGTCTTTCGCCTGATCGGCGTAAACCGCTACCGCTTTCGCATCAAGCGTTGCCGGACGTT"
    )

    MOLECULE_LINES = {
        350: (
            b"m54099_200711_014004/350/ccs", b"16", b"U00096.3",
            b"118", b"254", b"332=", b"*", b"0", b"0",
            (b"AAGTTCGGGCAAATGTTATCAACCCGCCGCGATCTTTTTCCACCGCATATTGCCGATCAGCT"
             b"GGCGTTATTGCAGGACAAAGTTGCTCCGTTTGATGGCAAGCTGGCGAAGCAGCAGATTGAAGC"
             b"TGCAATGGGCGGCTTGCCGGTAGAAGCGTGGTTTGACGATTTTGAAATCAAGCCGCTGGCTTC"
             b"TGCTTCTATCGCCCAGGTTCATACCGCGCGATTGAAATCGAATGGTAAAGAGGTGGTGATTAA"
             b"AGTCATCCGCCCGGATATTTTGCCGGTTATTAAAGCGGATCTGAAACTTATCTACCGTCTGGC"
             b"TCGCTGGGTGCCGCGTTT"),
            b"~"*100+b"1234567890qwertyuiopasdfghjklzxcvbnm,.-<>;"+b"~"*200,
            b"RG:Z:3d1638a6", b"ec:f:60", b"np:i:60", b"rq:f:1",
            b"sn:B:f,5.47248,10.074,6.52768,11.3767", b"zm:i:350",
            b"AS:i:-1660", b"NM:i:0"
        ),
        401: (
            b"m54099_200711_014004/401/ccs", b"16", b"U00096.3",
            b"500", b"254", b"80=", b"*", b"0", b"0",
            (b"AAAGGATCTGTAATTAGTCGACCAGCGGATCGAATGTTATAATACGCGCCAATAAAAACGGC"
             b"TCAGATCTTCATCTGCCA"),
            b"~"*30+b"+"*10+b"'"*10+b"Q"*10+b"_"*10+b"="*10,
            b"RG:Z:3d1638a6", b"ec:f:60", b"np:i:60", b"rq:f:1",
            b"sn:B:f,5.47248,10.074,6.52768,11.3767", b"zm:i:401",
            b"AS:i:-1660", b"NM:i:0"
        ),
        405: (
            b"m54099_200711_014004/405/ccs", b"16", b"U00096.3",
            b"630", b"254", b"80=", b"*", b"0", b"0",
            (b"ATTGCATCTGTAATTAGTCGACCAGCGGATGGAATGTTATAATACGCGCCAATTGCAACGGC"
             b"TCAACTCAGCTCCTGCCA"),
            b"~"*80,
            b"RG:Z:3d1638a6", b"ec:f:60", b"np:i:60", b"rq:f:1",
            b"sn:B:f,5.47248,10.074,6.52768,11.3767", b"zm:i:405",
            b"AS:i:-1660", b"NM:i:0"
        ),
        456: (
            b"m54099_200711_014004/456/ccs", b"16", b"U00096.3",
            b"760", b"254", b"129=", b"*", b"0", b"0",
            (b"CTGGTCTTTCGCCTGATCGGCGTAAACCGCTACCGCTTTCGCATCAAGCGTTGCCGGACGTT"
             b"CATTGATCCCGGCACCAGGCTGCACGACGTTAACGATGATAAGACCAATAATCAGCGCGATG"
             b"GTACT"),
            b"~"*100+b"}"*29,
            b"RG:Z:3d1638a6", b"ec:f:60", b"np:i:60", b"rq:f:1",
            b"sn:B:f,5.30539,9.67227,6.35734,11.0005", b"zm:i:456",
            b"AS:i:-645", b"NM:i:0"
        ),
    }
    IPD_METHYLATIONS = [
        ("401", "m6A", "506", "52", "-", "25",
         "TGAAGCTGATCAGAAGGGTGATCCGAAGTGGGATCTACGAG", "5.31", "34"),
        ("401", "m6A", "528", "61", "+", "24",
         "CACTTCGGATCACCCTTCTGATCAGCTTCACTACCTTCCAC", "7.16", "39"),
        ("401", "m6A", "529", "41", "-", "25",
         "TGTGGAAGGTAGTGAAGCTGATCAGAAGGGTGATCCGAAGT", "6.68", "13"),
        ("405", "m4C", "636", "23", "+", "99",
         "GCAGCTACGGTTTCGATTTCCTCCACCGGCGCATTTTCCAG", "1.42", "11"),
        ("405", "m6A", "640", "41", "-", "25",
         "TGTGGAAGGTAGTGAAGCTGATAAGAAGGGTGCTCCGAAGT", "2.68", "8"),
        ("456", "m6A", "775", "25", "+", "9",
         "CTATGCTTTGCGCTGCCACGATCGCGACATAGATCCCACAT", "6.81", "10"),
        ("456", "m6A", "6", "27", "+", "7",
         "CTGCCACGATCGCGACATAGATCCCACATCGGATCGCGCAA", "6.82", "5"),
        ("456", "m4C", "818", "47", "-", "17",
         "CTGCCACGATCGCGACATAGATCCCACATCGGATCGCGCAA", "16.82", "52"),
        ("461", "m6A", "192", "22", "-", "15",
         "TGATCGTTGCCGCGCATAGCAATGCCCGGCAGGACAGAGCA", "2.45", "3"),
        ("461", "m6A", "191", "24", "+", "15",
         "CATTGCTATGCGCGGCAACGATCACGTCCTAGATCCCGCAT", "3.51", "3"),
        ("461", "m6A", "196", "23", "-", "15",
         "GATGCGGGATCTAGGACGTGATCGTTGCCGCGCATAGCAAT", "3.20", "4"),
        ("461", "m6A", "195", "25", "+", "15",
         "CGGCAACGATCACGTCCTAGATCCCGCATCGGATCACGCTT", "4.10", "4"),
        ("461", "m4C", "204", "72", "-", "88",
         "TGATCGTTGCCGCGCATAGCAATGCCCGGCAGGACAGAGCA", "12.45", "33"),
        ("507", "m6A", "440", "110", "+", "128",
         "GGTTAGGCACCAGGCTGCACGATCGATAAGACCAATAATCA", "19.33", "58"),
        ("507", "m6A", "441", "109", "-", "132",
         "GGTTAGGCACCAGGCTGCACGATCGATAAGACCAATAATCA", "17.46", "47"),
    ]
    METHYLATIONS_PER_MOLECULE = [
        (
            "350",
            ("AAGTTCGGGCAAATGTTATCAACCCGCCGCGATCTTTTTCCACCGCATATTGCCGATCAGCT"
             "GGCGTTATTGCAGGACAAAGTTGCTCCGTTTGATGGCAAGCTGGCGAAGCAGCAGATTGAAGC"
             "TGCAATGGGCGGCTTGCCGGTAGAAGCGTGGTTTGACGATTTTGAAATCAAGCCGCTGGCTTC"
             "TGCTTCTATCGCCCAGGTTCATACCGCGCGATTGAAATCGAATGGTAAAGAGGTGGTGATTAA"
             "AGTCATCCGCCCGGATATTTTGCCGGTTATTAAAGCGGATCTGAAACTTATCTACCGTCTGGC"
             "TCGCTGGGTGCCGCGTTT"),
            "118", "449", "332", "25", "27", "5.4", "88.3", "1", "3",
            "148,172,406", "0", "0,0,0", "", "", "", "", "", "", ""
        ),
        (
            "401",
            ("AAAGGATCTGTAATTAGTCGACCAGCGGATCGAATGTTATAATACGCGCCAATAAAAA"
             "CGGCTCAGATCTTCATCTGCCA"), "500", "579",
            "80", "120", "120", "0.1", "54.1", "1", "3",
            "504,527,565", "2", "-,f,0", "40.6", "51.3", "5.31", "6.38",
            "13.0", "28.7", "25"
        ),
        (
            "405",
            ("ATTGCATCTGTAATTAGTCGACCAGCGGATGGAATGTTATAATACGCGCCAATTGCAACGGC"
             "TCAACTCAGCTCCTGCCA"),
            "630", "709", "80", "89", "88", "74.0", "93.0",
            "1", "0", "", "", "", "", "", "", "", "", "", ""
        ),
        (
            "456",
            ("CTGGTCTTTCGCCTGATCGGCGTAAACCGCTACCGCTTTCGCATCAAGCGTTGCCGGACG"
             "TTCATTGATCCCGGCACCAGGCTGCACGACGTTAACGATGATAAGACCAATAATCAGCGCG"
             "ATGGTACT"),
            "760", "67", "129", "50", "149", "71.6", "92.8",
            "1", "2", "774,5", "2", "+,+", "22.9", "26.0", "6.81", "6.81",
            "4.1", "7.5", "8"

        ),
    ]

    SUBREADS_PER_MOLECULE = {
        350: {"+": 25, "-": 27},
        401: {"+": 120, "-": 120},
        405: {"+": 89, "-": 88},
        456: {"+": 50, "-": 149},
    }

    @classmethod
    def setUpClass(cls):
        """Tasks performed in this method:
        1) Prepare a reference sequence"""
        cls.MOLECULES = {}
        for idx, l in cls.MOLECULE_LINES.items():
            mol = Molecule(idx, "", l)
            mol.reference = cls.REFERENCE
            mol.had_processing_problems = False
            cls.MOLECULES[idx] = mol

        # What is all the rest doing!?
        # mols = [
        #     (idx, cls.MOLECULES[idx]) for idx in
        #     ("456", "350", "401", "405")
        # ]
        # seqs = []
        # prev = 0
        # for idx, mol in mols:
        #     current = int(mol[3].decode())-1
        #     if idx == "507":
        #         seq = mol[9].decode()
        #         seq = seq[:10]+seq[11:]
        #     else:
        #         seq = mol[9].decode()
        #     seqs.append("?"*(current-prev))
        #     seqs.append(seq)
        #     prev = current+len(seq)

    def test_sets_some_attributes(self):
        mr = MethylationReport(
            detections_csv="a/b/c.csv",
            molecules={2:None},
            modification_types=["m6A"],
        )
        self.assertEqual(str(mr.csv_name), "a/b/methylation.c.csv")
        self.assertIs(mr.filtered_bam_statistics, None)
        self.assertEqual(mr._molecules, {2:None})

    def test_modification_types_get_validated(self):
        mr = MethylationReport(
            detections_csv="some.csv", molecules={},
            modification_types=["m6A"]
        )
        self.assertEqual(mr.modification_types, ["m6A"])
        mr = MethylationReport(
            detections_csv="some.csv", molecules={},
            modification_types=["?"]
        )
        self.assertEqual(mr.modification_types, [])
        mr = MethylationReport(
            detections_csv="some.csv", molecules={},
            modification_types=["?", "m6A"]
        )
        self.assertEqual(mr.modification_types, ["m6A"])

    def test_emits_log_message_for_each_invalid_modification_type(self):
        with self.assertLogs() as cm:
            MethylationReport(
                detections_csv="some.csv", molecules={},
                modification_types=["?", "m6A", "m4C"]
            )
        template = (
            "[methylation report] modifications of type '{mod}' will be "
            "ignored"
        )
        self.assertEqual(
            cm.output,
            ["WARNING:root:"+template.format(mod="?"),
             "WARNING:root:"+template.format(mod="m4C")]
        )

    @patch("pacbio_data_processing.sm_analysis.csv.reader")
    @patch("pacbio_data_processing.sm_analysis.csv.writer")
    @patch("pacbio_data_processing.sm_analysis.MethylationReport."
           "_write_molecules")
    @patch("pacbio_data_processing.sm_analysis.open")
    def test_save_writes_header_and_calls_write_molecules(
            self, mopen, pwrite_molecules, pwriter, preader):
        mopen_write = mock_open()
        mopen_read = mock_open(read_data="")
        mopen.side_effect = [mopen_read.return_value, mopen_write.return_value]
        mr = MethylationReport(
            detections_csv="a/b/c.csv", molecules={},
            modification_types=["m6A"],
        )
        mr.save()
        mopen.assert_has_calls(
            [call(Path("a/b/c.csv")), call(mr.csv_name, "w")])
        preader.assert_called_once_with(
            mopen_read().__enter__(), delimiter=',')
        pwriter.assert_called_once_with(
            mopen_write().__enter__(), delimiter=';')
        pwriter.return_value.writerow.assert_called_once_with(
            METHYLATION_REPORT_HEADER)
        pwrite_molecules.assert_called_once_with(
            preader.return_value, pwriter.return_value)

    def test_write_molecules_writes_one_line_per_expected_molecule(self):
        reader = MagicMock()
        writer = MagicMock()
        reader.__iter__ = MagicMock(return_value=iter(self.IPD_METHYLATIONS))
        mr = MethylationReport(
            detections_csv="a/b/c.csv", molecules=self.MOLECULES,
            modification_types=["m6A"]
        )
        mr.filtered_bam_statistics = {"subreads": self.SUBREADS_PER_MOLECULE}
        mr._write_molecules(reader, writer)
        writer.writerow.assert_has_calls(
            [call(_) for _ in self.METHYLATIONS_PER_MOLECULE]
        )
        self.assertEqual(
            len(writer.writerow.mock_calls),
            len(self.METHYLATIONS_PER_MOLECULE)
        )

    def test_write_molecules_doesnt_write_molecules_without_methylations(self):
        reader = MagicMock()
        writer = MagicMock()
        reader.__iter__ = MagicMock(return_value=iter(self.IPD_METHYLATIONS))
        mr = MethylationReport(
            detections_csv="a/b/c.csv", molecules=self.MOLECULES,
            modification_types=["m6A"]
        )
        mr._write_molecules(reader, writer)
        for c in writer.writerow.mock_calls:
            self.assertNotEqual(c[1][0][0], "461")

    def test_write_molecules_doesnt_write_molecules_with_problems(self):
        reader = MagicMock()
        writer = MagicMock()
        reader.__iter__ = MagicMock(return_value=iter(self.IPD_METHYLATIONS))
        self.MOLECULES[350].had_processing_problems = True
        mr = MethylationReport(
            detections_csv="a/b/c.csv", molecules=self.MOLECULES,
            modification_types=["m6A"]
        )
        mr._write_molecules(reader, writer)
        for c in writer.writerow.mock_calls:
            self.assertNotEqual(c[1][0][0], "350")
        self.MOLECULES[350].had_processing_problems = False


class MatchMethylationStatesTestCase(unittest.TestCase):
    def test_returns_zero_if_no_matching_state(self):
        for ipd_meth_states in ({}, {5: "-"}):
            self.assertEqual(
                match_methylation_states_m6A(5, ipd_meth_states), "0")

    def test_returns_plus_or_minus_if_one_match(self):
        in_ipd_meth_states = [
            {24: "-"},
            {14: "+"},
            {82: "+", 84: "-"}
        ]
        expected_results = ["-", "+", "-"]
        plus_positions = [23, 14, 83]
        for i, ipd_meth_states in enumerate(in_ipd_meth_states):
            pos = plus_positions[i]
            expected = expected_results[i]
            with self.subTest(pos=pos):
                self.assertEqual(
                    match_methylation_states_m6A(pos, ipd_meth_states),
                    expected
                )

    def test_returns_f_if_two_matches(self):
        in_ipd_meth_states = [
            {24: "-", 23: "+"},
            {14: "+", 15: "-"},
            {83: "+", 84: "-", 87: "+"}
        ]
        plus_positions = [23, 14, 83]
        for i, ipd_meth_states in enumerate(in_ipd_meth_states):
            pos = plus_positions[i]
            with self.subTest(pos=pos):
                self.assertEqual(
                    match_methylation_states_m6A(pos, ipd_meth_states), "f"
                )
