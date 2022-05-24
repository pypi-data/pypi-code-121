# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
from unittest import mock

from shapelets.model import SequenceMetadata


class SequenceMetadataTest(unittest.TestCase):
    def test_to_dict1(self):
        item1 = mock.MagicMock()
        item1.to_dict.return_value = {'a': 'b'}
        item2 = mock.Mock()
        item2.to_dict.return_value = {'x': 'y'}
        sequence_metadata = SequenceMetadata([item1, item2])
        self.assertEqual(sequence_metadata.to_dict(), {'items': [{'a': 'b'}, {'x': 'y'}]})
        item1.to_dict.assert_called_once()
        item2.to_dict.assert_called_once()

    @mock.patch('shapelets.model.metadata_item.MetadataItem.from_dict')
    def test_to_dict2(self, mock_item):
        item1 = mock.MagicMock()
        item2 = mock.MagicMock()
        mock_item.side_effect = [item1, item2]
        s = SequenceMetadata.from_dict({'items': [{'a': 'b'}, {'x': 'y'}]})
        self.assertEqual(len(s.items), 2)
        mock_item.assert_has_calls([mock.call({'a': 'b'}), mock.call({'x': 'y'})])
