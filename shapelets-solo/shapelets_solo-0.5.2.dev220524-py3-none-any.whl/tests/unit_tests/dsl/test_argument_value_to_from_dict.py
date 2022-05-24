# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import numpy as np

from shapelets.dsl import (
    ArgumentType,
    ArgumentTypeEnum,
    ArgumentValue,
    serialize_lambda
)
from shapelets.model import (
    Sequence,
    SequenceAxis,
    SequenceDensityEnum,
    SequenceBaseTypeEnum,
    AxisTypeEnum,
    View,
    ViewGroupEntry,
    Match,
    NDArray
)


class ArgumentValueSerializationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.seq = Sequence("camomile",
                           "seq0",
                           SequenceAxis(AxisTypeEnum.ORDINAL, 0, 1),
                           10, 0, "s",
                           SequenceDensityEnum.DENSE,
                           SequenceBaseTypeEnum.ORDINAL)
        cls.nd_array = NDArray(nd_array_id="nd_array_id",
                               name="NDArray",
                               description="NDArray Description",
                               dtype=np.dtype("int32"),
                               dims=(1, 2, 3, 4, 5))

    def test_sequence_to_dict(self):
        seq = ArgumentValueSerializationTest.seq
        expected = {
            "id": seq.sequence_id,
            "name": seq.name,
            "offset": seq.offset,
            "length": seq.length,
            "units": seq.units,
            "density": seq.density.value,
            "baseType": seq.base_type.value,
            "axisInfo": {
                "type": seq.axis.type.value,
                "starts": seq.axis.starts,
                "every": seq.axis.every
            }
        }
        self.assertEqual(expected, seq.to_dict())

    def test_sequence_from_dict(self):
        seq = {
            "id": "camomile",
            "name": "seq0",
            "offset": 0,
            "length": 10,
            "units": "s",
            "density": "DENSE",
            "baseType": "ORDINAL",
            "axisInfo": {
                "type": "io.shapelets.model.density.RegularOrdinalAxis",
                "starts": 0,
                "every": 1
            }
        }
        expected = ArgumentValueSerializationTest.seq
        self.assertEqual(expected, Sequence.from_dict(seq))

    def test_argument_value_sequence_to_dict(self):
        seq = ArgumentValueSerializationTest.seq
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.SEQUENCE), seq)
        expected = {
            "type": str(arg_value.arg_type),
            "sequence": {
                "id": seq.sequence_id
            }
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_sequence_from_dict(self):
        arg_value = {
            "type": "SEQUENCE",
            "sequence": {
                "id": "camomile",
                "name": "seq0",
                "offset": 0,
                "length": 10,
                "units": "s",
                "density": "DENSE",
                "baseType": "ORDINAL",
                "axisInfo": {
                    "type": "io.shapelets.model.density.RegularOrdinalAxis",
                    "starts": 0,
                    "every": 1
                }
            }
        }
        seq = ArgumentValueSerializationTest.seq
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.SEQUENCE), seq)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_nd_array_to_dict(self):
        nd_array = ArgumentValueSerializationTest.nd_array
        expected = {
            "ndArrayId": nd_array.nd_array_id,
            "name": nd_array.name,
            "description": nd_array.description,
            "dtype": nd_array.dtype,
            "dims": nd_array.dims
        }
        self.assertEqual(expected, nd_array.to_dict())

    def test_nd_array_from_dict(self):
        nd_array = {
            "ndArrayId": "nd_array_id",
            "name": "NDArray",
            "description": "NDArray Description",
            "dtype": np.dtype("int32"),
            "dims": (1, 2, 3, 4, 5)
        }
        expected = ArgumentValueSerializationTest.nd_array
        self.assertEqual(expected, NDArray.from_dict(nd_array))

    def test_argument_value_nd_array_to_dict(self):
        nd_array = ArgumentValueSerializationTest.nd_array
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.ND_ARRAY), nd_array)
        expected = {
            "type": "ND_ARRAY",
            "ndArray": {
                "description": "NDArray Description",
                "dims": (1, 2, 3, 4, 5),
                "dtype": "int32",
                "name": "NDArray",
                "ndArrayId": "nd_array_id"
            }
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_nd_array_from_dict(self):
        arg_value = {
            "type": "ND_ARRAY",
            "ndArray": {
                "description": "NDArray Description",
                "dims": (1, 2, 3, 4, 5),
                "dtype": "int32",
                "name": "NDArray",
                "ndArrayId": "nd_array_id"
            }
        }
        nd_array = ArgumentValueSerializationTest.nd_array
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.ND_ARRAY), nd_array)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_view_to_dict(self):
        seq = ArgumentValueSerializationTest.seq
        view = View(seq, 0, 100)
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.VIEW), view)
        expected = {
            "type": str(arg_value.arg_type),
            "view": {
                "sequence_id": "camomile",
                "begin": 0,
                "end": 100
            }
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_view_from_dict(self):
        seq = ArgumentValueSerializationTest.seq
        arg_value = {
            "type": "VIEW",
            "view": {
                "sequence": seq,
                "begin": 0,
                "end": 100
            }
        }
        view = View(seq, 0, 100)
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.VIEW), view)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_view_group_entry_to_dict(self):
        seq = ArgumentValueSerializationTest.seq
        view = View(seq, 0, 100)
        view_group_entry = ViewGroupEntry("liberty", view, {"awesome": "True", "novelty": "100"})
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.VIEW_GROUP_ENTRY), view_group_entry)
        expected = {
            "type": str(arg_value.arg_type),
            "viewGroupEntry": {
                "id": "liberty",
                "view": {
                    "sequence_id": "camomile",
                    "begin": 0,
                    "end": 100
                },
                "properties": {
                    "awesome": "True",
                    "novelty": "100"
                }
            }
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_view_group_entry_from_dict(self):
        seq = ArgumentValueSerializationTest.seq
        arg_value = {
            "type": "VIEW_GROUP_ENTRY",
            "viewGroupEntry": {
                "id": "liberty",
                "view": {
                    "sequence": seq,
                    "begin": 0,
                    "end": 100
                },
                "properties": {
                    "awesome": "True",
                    "novelty": "100"
                }
            }
        }
        view = View(seq, 0, 100)
        view_group_entry = ViewGroupEntry("liberty", view, {"awesome": "True", "novelty": "100"})
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.VIEW_GROUP_ENTRY), view_group_entry)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_match_to_dict(self):
        seq = ArgumentValueSerializationTest.seq
        match = Match(3.1415, View(seq, 0, 100))
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.MATCH), match)
        expected = {
            "type": str(arg_value.arg_type),
            "match": {
                "correlation": 3.1415,
                "view": {
                    "sequence_id": "camomile",
                    "begin": 0,
                    "end": 100
                },
            }
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_match_from_dict(self):
        seq = ArgumentValueSerializationTest.seq
        arg_value = {
            "type": "MATCH",
            "match": {
                "correlation": 3.1415,
                "view": {
                    "sequence": seq,
                    "begin": 0,
                    "end": 100
                },
            }
        }
        match = Match(3.1415, View(seq, 0, 100))
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.MATCH), match)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_function_to_dict(self):
        def function(a, b): return a + b

        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.FUNCTION), function)
        expected = {
            "type": str(arg_value.arg_type),
            "function": serialize_lambda(function)
        }
        self.assertEqual(str(expected), str(arg_value.to_dict()))

    def test_argument_value_function_from_dict(self):
        def function(a, b): return a + b

        arg_value = {
            "type": "FUNCTION",
            "function": serialize_lambda(function)
        }
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.FUNCTION), function)
        self.assertEqual(expected.arg_value(28, 2),
                         ArgumentValue.from_dict(arg_value).arg_value(28, 2))

    def test_argument_value_boolean_to_dict(self):
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.BOOLEAN), True)
        expected = {
            "type": str(arg_value.arg_type),
            "bool": True
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_boolean_from_dict(self):
        arg_value = {
            "type": "BOOLEAN",
            "bool": True
        }
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.BOOLEAN), True)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_byte_to_dict(self):
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.BYTE), b"0")
        expected = {
            "type": str(arg_value.arg_type),
            "byte": b"0"
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_byte_from_dict(self):
        arg_value = {
            "type": "BYTE",
            "byte": b"0"
        }
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.BYTE), b"0")
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_list_to_dict(self):
        int_list = ArgumentValue(
            ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT),
            [1, 2, 3, 4, 5])
        expected = {
            "type": "ARGUMENT_LIST",
            "list": [
                {"type": "INTEGER", "int": 1},
                {"type": "INTEGER", "int": 2},
                {"type": "INTEGER", "int": 3},
                {"type": "INTEGER", "int": 4},
                {"type": "INTEGER", "int": 5}
            ]
        }
        self.assertEqual(expected, int_list.to_dict())

    def test_argument_value_list_from_dict(self):
        int_list = {
            "type": "LIST",
            "list": [
                {"type": "INTEGER", "int": 1},
                {"type": "INTEGER", "int": 2},
                {"type": "INTEGER", "int": 3},
                {"type": "INTEGER", "int": 4},
                {"type": "INTEGER", "int": 5}
            ]
        }
        expected = ArgumentValue(
            ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT),
            [1, 2, 3, 4, 5])
        self.assertEqual(expected, ArgumentValue.from_dict(int_list))

    def test_argument_value_double_to_dict(self):
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.DOUBLE), 3.1415)
        expected = {
            "type": str(arg_value.arg_type),
            "double": 3.1415
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_double_from_dict(self):
        arg_value = {
            "type": "DOUBLE",
            "double": 3.1415
        }
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.DOUBLE), 3.1415)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_float_to_dict(self):
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.FLOAT), 3.1415)
        expected = {
            "type": str(arg_value.arg_type),
            "float": 3.1415
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_float_from_dict(self):
        arg_value = {
            "type": "FLOAT",
            "float": 3.1415
        }
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.FLOAT), 3.1415)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_int_to_dict(self):
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.INT), 31415)
        expected = {
            "type": str(arg_value.arg_type),
            "int": 31415
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_int_from_dict(self):
        arg_value = {
            "type": "INT",
            "int": 31415
        }
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.INT), 31415)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_long_to_dict(self):
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.LONG), 314153141516)
        expected = {
            "type": str(arg_value.arg_type),
            "long": 314153141516
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_long_from_dict(self):
        arg_value = {
            "type": "LONG",
            "long": 314153141516
        }
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.LONG), 314153141516)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_short_to_dict(self):
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.SHORT), 5)
        expected = {
            "type": str(arg_value.arg_type),
            "short": 5
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_short_from_dict(self):
        arg_value = {
            "type": "SHORT",
            "short": 5
        }
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.SHORT), 5)
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))

    def test_argument_value_string_to_dict(self):
        arg_value = ArgumentValue(ArgumentType(ArgumentTypeEnum.STRING), "Alberto")
        expected = {
            "type": str(arg_value.arg_type),
            "string": "Alberto"
        }
        self.assertEqual(expected, arg_value.to_dict())

    def test_argument_value_string_from_dict(self):
        arg_value = {
            "type": "STRING",
            "string": "Alberto"
        }
        expected = ArgumentValue(ArgumentType(ArgumentTypeEnum.STRING), "Alberto")
        self.assertEqual(expected, ArgumentValue.from_dict(arg_value))
