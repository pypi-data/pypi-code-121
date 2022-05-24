# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

from shapelets.dsl import (
    ArgumentType,
    ArgumentTypeEnum,
    backend_type,
    compatible_types_pred
)


class ArgumentTypesTest(unittest.TestCase):
    def test_single_argument_type(self):
        arg_type = ArgumentType(ArgumentTypeEnum.INT)
        self.assertEqual(arg_type.get_order(), 1)
        self.assertEqual(arg_type.get(), ArgumentTypeEnum.INT)
        self.assertEqual(arg_type.get_backend(), backend_type(ArgumentTypeEnum.INT))
        self.assertEqual(arg_type.get_all_values(), ArgumentTypeEnum.INT.value)
        self.assertEqual(arg_type.get_inner().types, ())
        self.assertTrue(arg_type == ArgumentType(ArgumentTypeEnum.INT))
        self.assertTrue(arg_type != ArgumentType(ArgumentTypeEnum.DOUBLE))
        with self.assertRaises(IndexError):
            arg_type.get(index=1)

    def test_complex_argument_type(self):
        arg_type = ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT)
        self.assertEqual(arg_type.get_order(), 2)
        self.assertEqual(arg_type.get(), ArgumentTypeEnum.LIST)
        self.assertEqual(arg_type.get(index=1), ArgumentTypeEnum.INT)
        self.assertEqual(arg_type.get_backend(), backend_type(ArgumentTypeEnum.LIST))
        self.assertEqual(arg_type.get_backend(index=1), backend_type(ArgumentTypeEnum.INT))
        self.assertEqual(
            arg_type.get_all_values(),
            f"{ArgumentTypeEnum.LIST.value}{ArgumentType.SEP}{ArgumentTypeEnum.INT.value}")
        self.assertEqual(arg_type.get_inner(), ArgumentType(ArgumentTypeEnum.INT))
        self.assertTrue(arg_type == ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT))
        self.assertTrue(arg_type != ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.DOUBLE))
        self.assertTrue(arg_type != ArgumentType(ArgumentTypeEnum.DOUBLE, ArgumentTypeEnum.INT))
        self.assertTrue(arg_type != ArgumentType(ArgumentTypeEnum.DOUBLE))
        with self.assertRaises(IndexError):
            arg_type.get(index=2)

    def test_compatible_types_simple(self):
        arg_type_src = ArgumentType(ArgumentTypeEnum.INT)
        arg_type_dst = ArgumentType(ArgumentTypeEnum.INT)
        self.assertTrue(compatible_types_pred(arg_type_src, arg_type_src))
        self.assertTrue(compatible_types_pred(arg_type_src, arg_type_dst))

    def test_compatible_types_complex(self):
        arg_type_src = ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT)
        arg_type_dst = ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT)
        self.assertTrue(compatible_types_pred(arg_type_src, arg_type_src))
        self.assertTrue(compatible_types_pred(arg_type_src, arg_type_dst))

    def test_incompatible_types(self):
        arg_type_src = ArgumentType(ArgumentTypeEnum.INT)
        arg_type_dst = ArgumentType(ArgumentTypeEnum.DOUBLE)
        self.assertFalse(compatible_types_pred(arg_type_src, arg_type_dst))

    def test_compatible_types_second_order_incompatible(self):
        arg_type_src = ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.INT)
        arg_type_dst = ArgumentType(ArgumentTypeEnum.LIST, ArgumentTypeEnum.DOUBLE)
        self.assertFalse(compatible_types_pred(arg_type_src, arg_type_dst))

    def test_argument_type_get_backend_type_mapping(self):
        self.assertEqual(backend_type(ArgumentTypeEnum.ND_ARRAY), 'NDArray')
        self.assertEqual(backend_type(ArgumentTypeEnum.VIEW), 'View')
        self.assertEqual(backend_type(ArgumentTypeEnum.VIEW_GROUP_ENTRY), 'ViewGroupEntry')
        self.assertEqual(backend_type(ArgumentTypeEnum.MATCH), 'Match')
        self.assertEqual(backend_type(ArgumentTypeEnum.BOOLEAN), 'Boolean')
        self.assertEqual(backend_type(ArgumentTypeEnum.BYTE), 'Byte')
        self.assertEqual(backend_type(ArgumentTypeEnum.FLOAT), 'Float')
        self.assertEqual(backend_type(ArgumentTypeEnum.FUNCTION), '() ->')
        self.assertEqual(backend_type(ArgumentTypeEnum.INT), 'Int')
        self.assertEqual(backend_type(ArgumentTypeEnum.LIST), 'List')
        self.assertEqual(backend_type(ArgumentTypeEnum.LONG), 'Long')
        self.assertEqual(backend_type(ArgumentTypeEnum.SEQUENCE), 'SequenceSpec')
        self.assertEqual(backend_type(ArgumentTypeEnum.SHORT), 'Short')
        self.assertEqual(backend_type(ArgumentTypeEnum.STRING), 'String')
        self.assertEqual(backend_type(ArgumentTypeEnum.ALTAIR), 'Altair')

    def test_argument_type_enum_values(self):
        self.assertEqual(ArgumentTypeEnum.ND_ARRAY.value, 'ND_ARRAY')
        self.assertEqual(ArgumentTypeEnum.VIEW.value, 'VIEW')
        self.assertEqual(ArgumentTypeEnum.VIEW_GROUP_ENTRY.value, 'VIEW_GROUP_ENTRY')
        self.assertEqual(ArgumentTypeEnum.MATCH.value, 'MATCH')
        self.assertEqual(ArgumentTypeEnum.BOOLEAN.value, 'BOOLEAN')
        self.assertEqual(ArgumentTypeEnum.BYTE.value, 'BYTE')
        self.assertEqual(ArgumentTypeEnum.DOUBLE.value, 'DOUBLE')
        self.assertEqual(ArgumentTypeEnum.FLOAT.value, 'FLOAT')
        self.assertEqual(ArgumentTypeEnum.FUNCTION.value, 'FUNCTION')
        self.assertEqual(ArgumentTypeEnum.INT.value, 'INTEGER')
        self.assertEqual(ArgumentTypeEnum.LIST.value, 'ARGUMENT_LIST')
        self.assertEqual(ArgumentTypeEnum.LONG.value, 'LONG')
        self.assertEqual(ArgumentTypeEnum.SEQUENCE.value, 'SEQUENCE')
        self.assertEqual(ArgumentTypeEnum.SHORT.value, 'SHORT')
        self.assertEqual(ArgumentTypeEnum.STRING.value, 'STRING')
        self.assertEqual(ArgumentTypeEnum.ALTAIR.value, 'ALTAIR')
