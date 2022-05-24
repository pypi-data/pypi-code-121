# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

from shapelets.model import (
    Sequence,
    SequenceAxis,
    AxisTypeEnum
)


class SequenceTest(unittest.TestCase):
    def test_axis_deserialization(self):
        axis_info = {
            'name': None,
            'type': 'io.shapelets.model.density.RegularOrdinalAxis',
            'starts': 1524864000,
            'ends': 1524874000,
            'every': 1000,
            'units': ''
        }
        axis = SequenceAxis.from_dict(axis_info)
        self.assertEqual(axis, SequenceAxis(AxisTypeEnum.ORDINAL, 1524864000, 1000))

    def test_sequence_deserialization(self):
        received = [
            {
                'id': 'ac0456b1-1cbb-4e61-b9fb-de6811237789',
                'parentIds': ['ac0456b1-1cbb-4e61-b9fb-de6811237789'],
                'name': 'seq0to9',
                'offset': 0,
                'length': 10,
                'density': 'DENSE',
                'axisInfo': {
                    'name': None,
                    'type': 'io.shapelets.model.density.RegularOrdinalAxis',
                    'starts': 1524864000,
                    'ends': 1524874000,
                    'every': 1000, 'units': ''
                },
                'valuesInfo': [
                    {'name': '0', 'type': 'NumericalValue'}
                ],
                'baseType': 'NUMERICAL',
                'units': 'null',
                'visualizationInfo': {
                    'numberOfLevels': 0, 'chunkSize': 256000
                }
            },

            {
                'id': '102edd3c-639e-48b8-bd61-3676c6a4f04b',
                'parentIds': ['102edd3c-639e-48b8-bd61-3676c6a4f04b'],
                'name': 'seq0to91',
                'offset': 0,
                'length': 10,
                'density': 'DENSE',
                'axisInfo': {
                    'name': None,
                    'type': 'io.shapelets.model.density.RegularOrdinalAxis',
                    'starts': 1524864000,
                    'ends': 1524874000,
                    'every': 1000,
                    'units': ''
                },
                'valuesInfo': [
                    {'name': '0', 'type': 'NumericalValue'}
                ],
                'baseType': 'NUMERICAL',
                'units': 'null',
                'visualizationInfo': {
                    'numberOfLevels': 0,
                    'chunkSize': 256000
                }
            },

            {
                'id': '5b6de6c2-b6bf-41e3-abbc-43d81e121bf9',
                'parentIds': ['5b6de6c2-b6bf-41e3-abbc-43d81e121bf9'],
                'name': 'small_sequence1',
                'offset': 0,
                'length': 5,
                'density': 'DENSE',
                'axisInfo': {
                    'name': None,
                    'type': 'io.shapelets.model.density.RegularOrdinalAxis',
                    'starts': 962653440,
                    'ends': 980653440,
                    'every': 3600000,
                    'units': ''
                },
                'valuesInfo': [
                    {'name': '0', 'type': 'NumericalValue'}
                ],
                'baseType': 'NUMERICAL',
                'units': 'null',
                'visualizationInfo': {
                    'numberOfLevels': 0,
                    'chunkSize': 921600000
                }
            },

            {
                'id': '0af70620-2e2f-4264-b1b5-9ec604e487b0',
                'parentIds': ['0af70620-2e2f-4264-b1b5-9ec604e487b0'],
                'name': 'small_sequence2',
                'offset': 0,
                'length': 5,
                'density': 'DENSE',
                'axisInfo': {
                    'name': None,
                    'type': 'io.shapelets.model.density.RegularOrdinalAxis',
                    'starts': 962653440,
                    'ends': 980653440,
                    'every': 3600000,
                    'units': ''
                },
                'valuesInfo': [{'name': '0', 'type': 'NumericalValue'}],
                'baseType': 'NUMERICAL',
                'units': 'null',
                'visualizationInfo': {
                    'numberOfLevels': 0, 'chunkSize': 921600000
                }
            }
        ]

        for seq_json in received:
            seq_from_json = Sequence.from_dict(seq_json)
            seq_as_dict = Sequence.to_dict(seq_from_json)
            seq_from_dict_content = Sequence(
                sequence_id=seq_as_dict['id'],
                name=seq_as_dict['name'],
                axis=SequenceAxis.from_dict(seq_as_dict['axisInfo']),
                length=seq_as_dict['length'],
                offset=seq_as_dict['offset'],
                units=seq_as_dict['units'],
                density=seq_as_dict['density'],
                base_type=seq_as_dict['baseType']
            )
            self.assertEqual(seq_from_json, seq_from_dict_content)
            self.assertEqual(seq_from_json.to_dict(), seq_from_dict_content.to_dict())
