# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
from datetime import datetime
import numpy as np
import pytz

from shapelets.model import MetadataType, MetadataItem, MetadataCoordinates


class MetadataItemTest(unittest.TestCase):
    def test_to_dict_str(self):
        expected = {"name": "the_name", "value": {"type": "STRING", "string": "the_value"}}
        item = MetadataItem(MetadataType.STRING, "the_name", "the_value")
        self.assertEqual(item.to_dict(), expected)

    def test_to_dict_float(self):
        expected = {"name": "the_name", "value": {"type": "DOUBLE", "double": 12.32}}
        item = MetadataItem(MetadataType.DOUBLE, "the_name", 12.32)
        self.assertEqual(item.to_dict(), expected)

    def test_to_dict_timestamp(self):
        dt = np.datetime64("2019-01-10")
        value = MetadataItem.adapt_value_out(MetadataType.TIMESTAMP, dt)
        self.assertTrue(isinstance(value, dict))
        self.assertTrue(value.get('timestamp'))
        timestamp_value = int(dt.astype("datetime64[ms]").astype("uint64"))
        self.assertEqual(value['timestamp'], timestamp_value)
        expected = {
            "name": "the_name",
            "value": {"type": "TIMESTAMP", "timestamp": value['timestamp']}
        }
        item = MetadataItem(MetadataType.TIMESTAMP, "the_name", dt)
        self.assertEqual(item.to_dict(), expected)
        item = MetadataItem(MetadataType.TIMESTAMP, "the_name", np.datetime64("2019-01-10"))
        self.assertEqual(item.to_dict(), expected)

    def test_to_dict_coordinates(self):
        expected = {
            "name": "the_name",
            "value": {"type": "COORDINATES", "coordinates": "eytp2y0vbzqw"}
        }
        coordinates = MetadataCoordinates(37.8709, -4.18472)
        item = MetadataItem(MetadataType.GEOHASH, "the_name", coordinates)
        self.assertEqual(item.to_dict(), expected)

    def test_from_dict_str(self):
        expected = {"name": "the_name", "value": {"type": "STRING", "string": "the_value"}}
        item = MetadataItem.from_dict(expected)
        self.assertEqual(item.metadata_type, MetadataType.STRING)
        self.assertEqual(item.name, "the_name")
        self.assertEqual(item.value, "the_value")

    def test_from_dict_float(self):
        expected = {"name": "the_name", "value": {"type": "DOUBLE", "double": 12.32}}
        item = MetadataItem.from_dict(expected)
        self.assertEqual(item.metadata_type, MetadataType.DOUBLE)
        self.assertEqual(item.name, "the_name")
        self.assertEqual(item.value, 12.32)

    def test_from_dict_timestamp(self):
        expected = {"name": "the_name", "value": {"type": "TIMESTAMP", "timestamp": 1547078400000}}
        item = MetadataItem.from_dict(expected)
        self.assertEqual(item.metadata_type, MetadataType.TIMESTAMP)
        self.assertEqual(item.name, "the_name")
        self.assertEqual(item.value, datetime(year=2019, month=1, day=10))

    def test_from_dict_coordinates(self):
        expected = {
            "name": "the_name",
            "value": {"type": "COORDINATES", "coordinates": "eytp2y0vbzqw"}
        }
        item = MetadataItem.from_dict(expected)
        self.assertEqual(item.metadata_type, MetadataType.GEOHASH)
        self.assertEqual(item.name, "the_name")
        self.assertEqual(item.value.lat, 37.8709)
        self.assertEqual(item.value.lon, -4.18472)
