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
from unittest.mock import patch, Mock

from pacbio_data_processing.bam_file_filter import main, BamFilter
from pacbio_data_processing.filters import (
    filter_seq_len, filter_enough_data_per_molecule, filter_quality,
)


@patch("pacbio_data_processing.bam_file_filter.BamFilter")
@patch("pacbio_data_processing.bam_file_filter.BamFilteringParameters")
@patch("pacbio_data_processing.bam_file_filter.config_logging")
@patch("pacbio_data_processing.bam_file_filter.parse_cl")
class MainFunctionTestCase(unittest.TestCase):
    def test_parses_cl(
            self, pparse_cl, pconfig_logging, pBamFilteringParameters,
            pBamFilter):
        main()
        pparse_cl.assert_called_once_with()

    def test_logging_configured_according_to_user_input(
            self, pparse_cl, pconfig_logging, pBamFilteringParameters,
            pBamFilter):
        main()
        pconfig_logging.assert_called_once_with(
            pparse_cl.return_value.verbose)

    def test_creates_BamFilteringParameters_instance(
            self, pparse_cl, pconfig_logging, pBamFilteringParameters,
            pBamFilter):
        main()
        pBamFilteringParameters.assert_called_once_with(
            pparse_cl.return_value)

    def test_reports_parameters(
            self, pparse_cl, pconfig_logging, pBamFilteringParameters,
            pBamFilter):
        pBamFilteringParameters.return_value.__str__.return_value = "2o9"
        with self.assertLogs() as cm:
            main()
        self.assertEqual(cm.output, ["INFO:root:2o9"])

    def test_creates_BamFilter_instance(
            self, pparse_cl, pconfig_logging, pBamFilteringParameters,
            pBamFilter):
        main()
        pBamFilter.assert_called_once_with(
            pBamFilteringParameters.return_value)

    def test_calls_BamFilter(
            self, pparse_cl, pconfig_logging, pBamFilteringParameters,
            pBamFilter):
        main()
        pBamFilter.return_value.assert_called_once_with()


class HighLevelErrorsTestCase(unittest.TestCase):
    @patch("pacbio_data_processing.bam_file_filter.parse_cl")
    def test_main_does_not_crashes_if_exception(self, pparse_cl):
        pparse_cl.side_effect = Exception("ji ji")
        with self.assertLogs() as cm:
            main()
        self.assertIn("CRITICAL:root:ji ji", cm.output)


class BamFilterTestCase(unittest.TestCase):
    def setUp(self):
        self.params = Mock()
        self.params.min_dna_seq_length = 0
        self.params.min_subreads_per_molecule = 1
        self.params.molecule_column = 24
        self.params.quality_threshold = 0
        self.params.limit_mappings = None
        self.params.filter_mappings = Mock()
        self.params.min_relative_mapping_ratio = 0.0
        self.b = BamFilter(self.params)

    def test_instance_has_attribute_input_parameters(self):
        self.assertEqual(self.params, self.b.input_parameters)

    @patch("pacbio_data_processing.bam_file_filter.BamFilter._write_output")
    @patch("pacbio_data_processing.bam_file_filter.BamFilter._apply_filters")
    @patch("pacbio_data_processing.bam_file_filter.BamFile")
    def test_main_procedure(self, pBamFile, papply_filters, pwrite_output):
        self.b()
        pBamFile.assert_called_once_with(self.params.input_bam_file)
        papply_filters.assert_called_once_with(pBamFile.return_value.body)
        pwrite_output.assert_called_once_with(
            pBamFile.return_value.header, papply_filters.return_value)

    @patch("pacbio_data_processing.bam_file_filter.BamFile")
    def test_write_output_dumps_given_data(self, pBamFile):
        header = "a jeder"
        body = "a body"
        self.b._write_output(header, body)
        pBamFile.assert_called_once_with(
            self.params.out_bam_file, mode="w"
        )
        pBamFile.return_value.write.assert_called_once_with(
            header=header, body=body)

    def test_apply_filters_does_nothing_if_no_filter_active(self):
        body = [(b"a", b"33"), (b"-l-", b"o")]
        for raw, filtered in zip(body, self.b._apply_filters(body)):
            self.assertEqual(raw, filtered)

    def test_no_filter_active_by_default(self):
        self.assertEqual(len(self.b.filters), 0)

    def test_apply_filters_with_one_filter(self):
        filter1 = Mock()
        args1 = (23,)
        self.b.filters = [(filter1,)+args1]
        lines = ["-", "g d", "a b c f d"]
        expected = ["f1"+_ for _ in lines]
        filter1.return_value = expected
        self.assertEqual(
            list(self.b._apply_filters(lines)), expected
        )
        filter1.assert_called_once_with(lines, *args1)

    def test_filter_seq_len_active_if_min_dna_seq_length(self):
        self.params.min_dna_seq_length = 10
        bam_filter = BamFilter(self.params)
        self.assertIn((filter_seq_len, 10), bam_filter.filters)

    def test_filter_seq_len_inactive_under_threshold(self):
        self.params.min_dna_seq_length = 0
        bam_filter = BamFilter(self.params)
        for f, *rest in bam_filter.filters:
            self.assertNotEqual(f, filter_seq_len)

    def test_filter_enough_data_per_molecule_if_min_subreads_per_molecule(
            self):
        self.params.min_subreads_per_molecule = 17
        bam_filter = BamFilter(self.params)
        self.assertIn(
            (filter_enough_data_per_molecule, 17),
            bam_filter.filters
        )

    def test_filter_enough_data_per_molecule_inactive_under_threshold(self):
        self.params.min_subreads_per_molecule = 1
        bam_filter = BamFilter(self.params)
        for f, *rest in bam_filter.filters:
            self.assertNotEqual(f, filter_enough_data_per_molecule)

    def test_filter_quality_active_if_quality_threshold(self):
        self.params.quality_threshold = 112
        bam_filter = BamFilter(self.params)
        self.assertIn((filter_quality, 112), bam_filter.filters)

    def test_filter_quality_inactive_under_threshold(self):
        self.params.quality_threshold = 0
        bam_filter = BamFilter(self.params)
        for f, *rest in bam_filter.filters:
            self.assertNotEqual(f, filter_quality)

    def test_filter_mappings_active_if_limit_mappings(self):
        self.params.limit_mappings = ("a", "aa")
        self.params.min_relative_mapping_ratio = 0.5
        bam_filter = BamFilter(self.params)
        self.assertIn(
            (self.params.filter_mappings, ("a", "aa"), 0.5),
            bam_filter.filters
        )

    def test_filter_mappings_inactive_if_no_mappings(self):
        self.params.limit_mappings = None
        bam_filter = BamFilter(self.params)
        for f, *rest in bam_filter.filters:
            self.assertNotEqual(f, self.params.filter_mappings)
