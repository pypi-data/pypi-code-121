# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
from unittest import mock
import numpy as np
import pandas as pd

from shapelets.services.metadata_service import MetadataService
from shapelets.model import (
    MetadataType,
    MetadataCoordinates
)

metadata_json = {
    'sequence2': {
        'items': [
            {'name': 'GRP', 'value': {'type': 'STRING', 'string': 'the_group'}},
            {'name': 'SIZE', 'value': {'type': 'DOUBLE', 'double': 15.36}},
            {'name': 'EVENT', 'value': {'type': 'TIMESTAMP', 'timestamp': 1547251200000}},
            {
                'name': 'LOCALIZATION_COORDINATES',
                'value': {'type': 'COORDINATES', 'coordinates': 'eysbgktnqtgw'}
            }
        ]
    },
    'sequence1': {
        'items': [
            {'name': 'GRP', 'value': {'type': 'STRING', 'string': 'the_group'}},
            {'name': 'SIZE', 'value': {'type': 'DOUBLE', 'double': 12.12}},
            {'name': 'EVENT', 'value': {'type': 'TIMESTAMP', 'timestamp': 1547078400000}},
            {
                'name': 'LOCALIZATION_COORDINATES',
                'value': {'type': 'COORDINATES', 'coordinates': 'eytp2y0vbzqw'}
            }
        ]
    }
}


class MetadataServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.collection_mock = mock.Mock()
        self.collection_mock.collection_id = "c1"
        self.sequence_mock = mock.Mock()
        self.sequence_mock.sequence_id = "s1"
        self.sequence_mock.name = "sequence1"
        self.sequence2_mock = mock.Mock()
        self.sequence2_mock.sequence_id = "s2"
        self.sequence2_mock.name = "sequence2"

    @mock.patch('requests.get')
    def test_get_metadata(self, mock_get):
        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        response_mock.content.return_value = {"sequencesMetadata": metadata_json}
        mock_get.return_value = response_mock
        metadata_service = MetadataService("base_url", "cookies")
        metadata = metadata_service.get_metadata(self.collection_mock)
        expected_df = pd.DataFrame(
            [("sequence1",
              "the_group",
              12.12,
              np.datetime64("2019-01-10"),
              MetadataCoordinates(37.8709, -4.18472)),
             ("sequence2",
              "the_group",
              15.36,
              np.datetime64("2019-01-12"),
              MetadataCoordinates(36.7201600, -4.4203400))
             ],
            columns=["sequence", "GRP", "SIZE", "EVENT", "LOCALIZATION_COORDINATES"])
        expected_df = expected_df.set_index("sequence")
        pd.testing.assert_frame_equal(expected_df, metadata, check_like=True)
        mock_get.assert_called_with(
            "base_url/api/collections/c1/metadataItems",
            headers={'Content-type': 'application/json'},
            cookies="cookies",
            timeout=300,
            verify=False)

    @mock.patch('requests.post')
    def test_raw_upload(self, mock_post):
        response_mock = mock.MagicMock()
        response_mock.status_code = 200
        mock_post.return_value = response_mock
        metadata_mock = mock.MagicMock()
        metadata_mock.to_dict.return_value = {'a': 'b'}
        metadata_service = MetadataService("base_url", "cookies")
        metadata_service.add_metadata(self.collection_mock, self.sequence_mock, metadata_mock)
        metadata_mock.to_dict.assert_called_once()
        mock_post.assert_called_with(
            url="base_url/api/collections/c1/sequences/s1/metadata",
            headers={'Content-type': 'application/json'},
            cookies="cookies",
            data="{\"a\": \"b\"}",
            timeout=300,
            verify=False
        )

    @mock.patch('requests.post')
    def test_raw_upload_failure(self, mock_post):
        response_mock = mock.MagicMock()
        response_mock.status_code = 500
        mock_post.return_value = response_mock
        metadata_mock = mock.MagicMock()
        metadata_mock.to_dict.return_value = {'a': 'b'}
        metadata_service = MetadataService("base_url", "cookies")
        metadata_service.add_metadata(self.collection_mock, self.sequence_mock, metadata_mock)
        metadata_mock.to_dict.assert_called_once()
        mock_post.assert_called_with(
            url="base_url/api/collections/c1/sequences/s1/metadata",
            headers={'Content-type': 'application/json'},
            cookies="cookies",
            data="{\"a\": \"b\"}",
            timeout=300,
            verify=False
        )
        response_mock.raise_for_status.assert_called_once()

    @mock.patch('shapelets.services.metadata_service.MetadataService.add_metadata')
    @mock.patch('requests.post')
    def test_pandas_upload(self, mock_post, mock_add_metadata):
        response_mock = mock.MagicMock()
        response_mock.status_code.return_value = 200
        mock_post.return_value = response_mock
        fields = ["sequence", "grp", "size", "event", "pos"]
        df = pd.DataFrame(
            [("sequence1",
              "the_group",
              12.12,
              np.datetime64("2019-01-10"),
              MetadataCoordinates(37.8709, -4.18472)),
             ("sequence2",
              "the_group",
              15.36,
              np.datetime64("2019-01-12"),
              MetadataCoordinates(36.7201600, -4.4203400))
             ],
            columns=fields)
        df = df.set_index("sequence")
        metadata_service = MetadataService("base_url", "cookies")
        metadata_service.add_metadata_from_pandas(
            self.collection_mock,
            [self.sequence_mock, self.sequence2_mock],
            df)
        self.assertEqual(mock_add_metadata.call_count, 2)
        self.assertEqual(mock_add_metadata.call_args_list[0][0][0].collection_id, "c1")
        self.assertEqual(mock_add_metadata.call_args_list[0][0][1].sequence_id, "s1")
        self.assertEqual(mock_add_metadata.call_args_list[0][0][2].to_dict(), {
            "items": [
                {"name": "grp", "value": {"type": "STRING", "string": "the_group"}},
                {"name": "size", "value": {"type": "DOUBLE", "double": 12.12}},
                {"name": "event", "value": {"type": "TIMESTAMP", "timestamp": 1547078400000}},
                {"name": "pos", "value": {"type": "COORDINATES", "coordinates": "eytp2y0vbzqw"}}
            ]
        })
        self.assertEqual(mock_add_metadata.call_args_list[1][0][0].collection_id, "c1")
        self.assertEqual(mock_add_metadata.call_args_list[1][0][1].sequence_id, "s2")
        self.assertEqual(mock_add_metadata.call_args_list[1][0][2].to_dict(), {
            "items": [
                {"name": "grp", "value": {"type": "STRING", "string": "the_group"}},
                {"name": "size", "value": {"type": "DOUBLE", "double": 15.36}},
                {"name": "event", "value": {"type": "TIMESTAMP", "timestamp": 1547251200000}},
                {"name": "pos", "value": {"type": "COORDINATES", "coordinates": "eysbgktnqtgw"}}
            ]
        })

    @mock.patch('requests.post')
    def test_pandas_upload_fail_invalid_type(self, mock_post):
        response_mock = mock.MagicMock()
        response_mock.status_code.return_value = 200
        mock_post.return_value = response_mock
        fields = ["sequence", "grp", "size", "event", "pos"]
        df = pd.DataFrame(
            [("sequence1",
              "the_group",
              12.12,
              np.datetime64("2019-01-10"),
              MetadataType.GEOHASH)
             ],
            columns=fields)
        with self.assertRaisesRegex(Exception, "Non valid MetadataType.*'pos'"):
            metadata_service = MetadataService("base_url", "cookies")
            metadata_service.add_metadata_from_pandas(
                self.collection_mock, [self.sequence_mock], df)
