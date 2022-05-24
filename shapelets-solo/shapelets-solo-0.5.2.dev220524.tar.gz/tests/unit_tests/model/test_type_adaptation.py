# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import typing
import numpy as np
import re
import unittest

from shapelets.dsl import (
    ArgumentType,
    ArgumentTypeEnum,
    backend_type,
)
from shapelets.model import (
    Match,
    Sequence,
    View,
    ViewGroupEntry,
    NDArray,
    ReplicatedParam
)

from shapelets.services.exceptions import ShapeletsException
from shapelets.services.py2backend_type_adapter import (
    OUTPUT_LIST_RETURN_TYPE,
    transform_type,
    TransformMode
)


class TestTypeAdaptation(unittest.TestCase):
    def test_transform_type_worker_mode(self):
        base_types = {
            Sequence: ArgumentTypeEnum.SEQUENCE.value,
            View: ArgumentTypeEnum.VIEW.value,
            ViewGroupEntry: ArgumentTypeEnum.VIEW_GROUP_ENTRY.value,
            Match: ArgumentTypeEnum.MATCH.value,
            bool: ArgumentTypeEnum.BOOLEAN.value,
            float: ArgumentTypeEnum.FLOAT.value,
            str: ArgumentTypeEnum.STRING.value,
            int: ArgumentTypeEnum.INT.value,
            NDArray: ArgumentTypeEnum.ND_ARRAY.value
        }
        all_types = dict(base_types)
        for key, val in base_types.items():
            key = re.findall("'([^\']*)'", str(key))[0].split('.')[-1]
            if key == 'ndarray':
                key = 'np.ndarray'
            all_types[eval(f"ReplicatedParam[{key}]")] = val
            val = f"{OUTPUT_LIST_RETURN_TYPE}({val})"
            all_types[eval(f"typing.List[{key}]")] = val
            all_types[eval(f"typing.List[ReplicatedParam[{key}]]")] = val
        for key, val in all_types.items():
            result = transform_type(key, TransformMode.SHAPELETS_WORKER)
            self.assertEqual(result, val)

    def test_transform_type_kotlin_mode(self):
        base_types = {
            Sequence: backend_type(ArgumentTypeEnum.SEQUENCE),
            View: backend_type(ArgumentTypeEnum.VIEW),
            ViewGroupEntry: backend_type(ArgumentTypeEnum.VIEW_GROUP_ENTRY),
            Match: backend_type(ArgumentTypeEnum.MATCH),
            bool: backend_type(ArgumentTypeEnum.BOOLEAN),
            float: backend_type(ArgumentTypeEnum.DOUBLE),
            str: backend_type(ArgumentTypeEnum.STRING),
            int: backend_type(ArgumentTypeEnum.INT),
            NDArray: backend_type(ArgumentTypeEnum.ND_ARRAY)
        }
        all_types = dict(base_types)
        for key, val in base_types.items():
            key = re.findall("'([^\']*)'", str(key))[0].split('.')[-1]
            if key == 'ndarray':
                key = 'np.ndarray'
            all_types[eval(f"ReplicatedParam[{key}]")] = val
            be_type = backend_type(ArgumentTypeEnum.LIST)
            val = f"{be_type}{ArgumentType.SEP}{val}"
            all_types[eval(f"typing.List[{key}]")] = val
            all_types[eval(f"typing.List[ReplicatedParam[{key}]]")] = val
        for key, val in all_types.items():
            result = transform_type(key, TransformMode.KOTLIN)
            self.assertEqual(result, val)

    def test_invalid_transform_mode(self):
        with self.assertRaises(ValueError):
            transform_type("a", "invalid")

    def test_transform_type_worker_mode_unsupported_type(self):
        with self.assertRaisesRegex(ValueError, "not supported"):
            transform_type(np.ndarray, TransformMode.SHAPELETS_WORKER)

    def test_transform_type_kotlin_mode_unsupported_type(self):
        with self.assertRaisesRegex(ValueError, "not supported"):
            transform_type(np.ndarray, TransformMode.KOTLIN)
