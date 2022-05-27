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
from unittest.mock import Mock, patch
from pathlib import Path

from pacbio_data_processing.parameters import (
    BamFilteringParameters, SingleMoleculeAnalysisParameters,
)
from pacbio_data_processing.filters import (
    filter_mappings_binary, filter_mappings_ratio,
)
from pacbio_data_processing.constants import DEFAULT_MODIFICATION_TYPE
from pacbio_data_processing import __version__ as VERSION


class ParametersMixIn:
    def setUp(self):
        class FakeClInput:
            ...
        self.cl_input = FakeClInput()

    def test_has__cl_input_attribute(self):
        cl_input = {"q": 1, "xxd": "tt"}
        instance = self.ParametersClass(cl_input)
        self.assertEqual(instance._cl_input, cl_input)


class BamFilteringParametersTestCase(ParametersMixIn, unittest.TestCase):
    ParametersClass = BamFilteringParameters

    def test_some_attibutes_come_directly_from_cl(self):
        cl_input = Mock()
        instance = self.ParametersClass(cl_input)
        direct_attrs_from_cl = (
            "input_bam_file", "min_dna_seq_length",
            "min_subreads_per_molecule", "quality_threshold",
        )
        for attr in direct_attrs_from_cl:
            self.assertEqual(getattr(instance, attr), getattr(cl_input, attr))

    def test_out_bam_file_attribute(self):
        self.cl_input.input_bam_file = Path("a/b/c.bam")
        instance = self.ParametersClass(self.cl_input)
        self.assertEqual(instance.out_bam_file, Path("a/b/parsed.c.bam"))

    def test_limit_mappings_attribute_with_all_input_is_None(self):
        self.cl_input.mappings = "all"
        instance = self.ParametersClass(self.cl_input)
        self.assertEqual(instance.limit_mappings, None)

    def test_limit_mappings_attribute_taken_from_cl_if_not_all(self):
        self.cl_input.mappings = "whatever"
        instance = self.ParametersClass(self.cl_input)
        self.assertEqual(instance.limit_mappings, "whatever")

    def test_default_filter_mappings_attribute(self):
        self.cl_input.min_relative_mapping_ratio = 0.0
        instance = self.ParametersClass(self.cl_input)
        self.assertEqual(instance.filter_mappings, filter_mappings_binary)

    def test_filter_mappings_attribute_with_ratio(self):
        self.cl_input.min_relative_mapping_ratio = 0.1
        instance = self.ParametersClass(self.cl_input)
        self.assertEqual(instance.filter_mappings, filter_mappings_ratio)

    def test_min_relative_mapping_ratio_attribute_bounded(self):
        raw_values = (1.1, -8)
        validated_values = (1, 0)
        for raw, valid in zip(raw_values, validated_values):
            self.cl_input.min_relative_mapping_ratio = raw
            instance = self.ParametersClass(self.cl_input)
            self.assertEqual(instance.min_relative_mapping_ratio, valid)

    def test_correct_str(self):
        attrs = {
            "input_bam_file": Path("a/b"),
            "min_relative_mapping_ratio": 0.3,
            "min_dna_seq_length": 20,
            "min_subreads_per_molecule": 7,
            "quality_threshold": 45,
            "mappings": ["a", "c", "s"],
        }
        for a, v in attrs.items():
            setattr(self.cl_input, a, v)
        instance = self.ParametersClass(self.cl_input)
        expected_str = (
            "Filtering 'a/b' to produce 'a/parsed.b' with:\n"
            "  minimun DNA sequence length: 20\n"
            "  minimun subreads per molecule: 7\n"
            "  quality of sequencing: 45\n"
            "  mappings: ['a', 'c', 's']\n"
            "  min mapping ratio: 0.3\n"
        )
        self.assertEqual(str(instance), expected_str)


class SingleMoleculeAnalysisParametersTestCase(
        ParametersMixIn, unittest.TestCase):
    ParametersClass = SingleMoleculeAnalysisParameters
    attrs_for_str_test = {
        "input_bam_file": Path("a/b.bam"),
        "fasta": Path("x.fasta"),
        "min_dna_seq_length": 20,
        "min_subreads_per_molecule": 7,
        "quality_threshold": 45,
        "mappings": ["a", "c", "s"],
        "molecule_column": 23,
        "ipd_model": None,
        "blasr_path": "blasr",
        "pbindex_path": "pbindex",
        "ipdsummary_path": "ipdSummary",
        "num_simultaneous_ipdsummarys": 8,
        "num_workers_per_ipdsummary": 3,
        "nprocs_blasr": 9,
        "partition": None,
        "aligned_CCS_bam_file": None,
        "CCS_bam_file": None,
        "keep_temp_dir": False,
        "modification_types": [DEFAULT_MODIFICATION_TYPE],
        "only_produce_methylation_report": False,
    }

    def make_instance(self, **kwargs):
        attrs = self.attrs_for_str_test.copy()
        attrs.update(kwargs)
        for a, v in attrs.items():
            setattr(self.cl_input, a, v)
        return self.ParametersClass(self.cl_input)

    def test_some_attibutes_come_directly_from_cl(self):
        cl_input = Mock()
        instance = self.ParametersClass(cl_input)
        direct_attrs_from_cl = ("input_bam_file", "fasta")
        for attr in direct_attrs_from_cl:
            self.assertEqual(getattr(instance, attr), getattr(cl_input, attr))

    def test_make_out_filename(self):
        instance = self.make_instance(input_bam_file=Path("x/c.bam"))
        self.assertEqual(
            instance._make_out_filename(suff=".col"),
            Path("x/sm-analysis.c.col")
        )
        self.assertEqual(
            instance._make_out_filename(suff=".cal", pref="moc."),
            Path("x/moc.sm-analysis.c.cal")
        )
        instance = self.make_instance(input_bam_file=Path("x/c"))
        self.assertEqual(
            instance._make_out_filename(suff=".col"),
            Path("x/sm-analysis.c.col")
        )

    def test_joint_gff_filename_attribute(self):
        instance = self.make_instance(input_bam_file=Path("a/b/c.bam"))
        # instance = self.ParametersClass(self.cl_input)
        self.assertEqual(
            instance.joint_gff_filename, Path("a/b/sm-analysis.c.gff"))

    def test_joint_gff_filename_attribute_with_partition(self):
        instance = self.make_instance(partition="6:7")
        self.assertEqual(
            instance.joint_gff_filename,
            Path("a/partition_6of7.sm-analysis.b.gff")
        )

    def test_one_line_per_mod_filename_attribute(self):
        instance = self.make_instance()
        self.assertEqual(
            instance.one_line_per_mod_filename,
            Path("a/sm-analysis.b.csv")
        )

    def test_one_line_per_mod_filename_attribute_with_partition(self):
        instance = self.make_instance(partition="2:3")
        self.assertEqual(
            instance.one_line_per_mod_filename,
            Path("a/partition_2of3.sm-analysis.b.csv")
        )

    def test_summary_report_html_filename_attribute(self):
        instance = self.make_instance(input_bam_file=Path("a/b/c.bam"))
        self.assertEqual(
            instance.summary_report_html_filename,
            Path("a/b/summary.sm-analysis.c.html")
        )

    def test_summary_report_html_filename_attribute_with_partition(self):
        instance = self.make_instance(partition="6:7")
        self.assertEqual(
            instance.summary_report_html_filename,
            Path("a/summary.partition_6of7.sm-analysis.b.html")
        )

    @patch("pacbio_data_processing.parameters.Path")
    @patch("pacbio_data_processing.parameters.SingleMoleculeAnalysisParameters"
           "._resolve_model_from_resources")
    def test_ipd_model_attribute(self, presolve, pPath):
        model_name = "some-model"
        model_path = Mock()
        model_path.is_file.return_value = True
        presolve.return_value = model_path
        self.cl_input.ipd_model = model_name
        pPath.return_value.is_file.return_value = False
        instance = self.ParametersClass(self.cl_input)
        self.assertEqual(instance.ipd_model, model_path)
        presolve.assert_called_once_with(model_name)

    @patch("pacbio_data_processing.parameters.Path")
    def test_ipd_model_attribute_if_raw_input_exists_as_path(self, pPath):
        model_name = "some-model"
        self.cl_input.ipd_model = model_name
        pPath.return_value.is_file.return_value = True
        instance = self.ParametersClass(self.cl_input)
        self.assertEqual(
            instance.ipd_model,
            pPath.return_value
        )
        pPath.assert_called_once_with(f"{model_name}")

    def test_ipd_model_attribute_is_None_if_not_given(self):
        self.cl_input.ipd_model = None
        instance = self.ParametersClass(self.cl_input)
        self.assertIs(instance.ipd_model, None)

    @patch("pacbio_data_processing.parameters.Path")
    @patch("pacbio_data_processing.parameters.SingleMoleculeAnalysisParameters"
           "._resolve_model_from_resources")
    def test_ipd_model_attribute_if_missing_model_file(
            self, presolve, pPath):
        model_name = "some-model"
        model_path = Mock()
        model_path.is_file.return_value = False
        presolve.return_value = model_path
        self.cl_input.ipd_model = model_name
        pPath.return_value.is_file.return_value = False
        instance = self.ParametersClass(self.cl_input)
        self.assertEqual(instance.ipd_model, None)

    def test_correct_default_str(self):
        instance = self.make_instance()
        expected_str = (
            f"Starting 'sm-analysis' (version {VERSION}) with:\n"
            "  Input BAM file:  'a/b.bam'\n"
            "  Reference file:  'x.fasta'\n"
            "  ipd program:  'ipdSummary'\n"
            "  # ipd program instances:  8\n"
            "  # workers per ipd instance:  3\n"
            "  modification types:  ['m6A']\n"
            "  aligner:  'blasr'\n"
            "  # workers blasr:  9\n"
            "  indexer:  'pbindex'\n"
            # "  Minimun DNA sequence length: 20\n"
            # "  Minimun subreads per molecule: 7\n"
            # "  Quality of sequencing: 45\n"
            # "  Mappings: ['a', 'c', 's']\n"
            # "  Minimun mapping ratio: 0.3\n"
        )
        self.assertEqual(str(instance), expected_str)

    @patch("pacbio_data_processing.parameters."
           "SingleMoleculeAnalysisParameters.ipd_model")
    def test_ipd_model_included_to_str_if_given(self, pipd_model):
        instance = self.make_instance()
        instance = self.ParametersClass(self.cl_input)
        instance.ipd_model = "my-model"
        self.assertIn("ipd model:  my-model\n", str(instance))

    @patch("pacbio_data_processing.parameters."
           "SingleMoleculeAnalysisParameters.ipd_model")
    def test_str_logs_error_if_ipd_model_given_but_not_found(self, pipd_model):
        model_name = "some-model"
        instance = self.make_instance(ipd_model=model_name)
        instance.ipd_model = None
        with self.assertLogs() as cm:
            str(instance)
        self.assertEqual(
            cm.output,
            [f"ERROR:root:Model '{model_name}' not found. Using default model"]
        )

    @patch("pacbio_data_processing.parameters.importlib.resources.files")
    def test_resolve_model_from_resources(self, pfiles):
        model_name = "my-name"
        pfiles.return_value = Path("/what/ever")
        model_path = f"/what/ever/resources/{model_name}.npz.gz"
        instance = self.ParametersClass(self.cl_input)
        model = instance._resolve_model_from_resources(model_name)
        self.assertEqual(model, Path(model_path))

    def test_partition_not_included_to_str_if_None(self):
        instance = self.make_instance()
        self.assertNotIn("partition:", str(instance))
        self.assertEqual(instance.partition, None)

    def test_partition_included_in_str_if_given(self):
        instance = self.make_instance(partition="5:19")
        self.assertIn("partition:  5 of 19\n", str(instance))

    def test_parttion_value(self):
        instance = self.make_instance(partition="1:2")
        self.assertEqual(instance.partition, (1, 2))

    def test_partition_is_validated(self):
        for wrong in ("5", "::", "9 of 59", "10:9", "a:b", "1:I0"):
            instance = self.make_instance(partition=wrong)
            self.assertNotIn("partition:", str(instance))

    def test_aligned_CCS_bam_file_not_included_to_str_if_None(self):
        instance = self.make_instance()
        instance.aligned_CCS_bam_file = None
        self.assertNotIn("aligned CCS bam file:", str(instance))

    def test_aligned_CCS_bam_file_included_to_str_if_given(self):
        instance = self.make_instance()
        instance.aligned_CCS_bam_file = Path("ca/ca/de/va/ca")
        self.assertIn(
            "aligned CCS bam file:  'ca/ca/de/va/ca'\n", str(instance))

    def test_CCS_bam_file_not_included_to_str_if_None(self):
        instance = self.make_instance()
        instance.CCS_bam_file = None
        self.assertNotIn("CCS bam file:", str(instance))

    def test_CCS_bam_file_included_to_str_if_given(self):
        instance = self.make_instance()
        instance.CCS_bam_file = Path("ca/ca/de/va/ca")
        self.assertIn(
            "CCS bam file:  'ca/ca/de/va/ca'\n", str(instance))

    def test_keep_temp_dir_included_to_str_if_True(self):
        instance = self.make_instance()
        self.assertNotIn("keep temp dir:  yes", str(instance))
        instance = self.make_instance(keep_temp_dir=True)
        self.assertIn("keep temp dir:  yes", str(instance))

    def test_only_produce_methylation_report_included_to_str_if_True(self):
        instance = self.make_instance()
        self.assertNotIn(
            "only produce methylation report:  yes", str(instance))
        instance = self.make_instance(only_produce_methylation_report=True)
        self.assertIn("only produce methylation report:  yes", str(instance))
