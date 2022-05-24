# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import numpy as np
import pandas as pd

from shapelets import init_session
from shapelets.model import Capsule
from shapelets.dsl import dsl_op as op


def capsule_function(cap1: Capsule, cap2: Capsule) -> Capsule:
    c_1 = cap1.data
    c_2 = cap2.data
    res = c_1 + c_2
    return Capsule(data=res, name="New Capsule")


class CapsulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._client.register_custom_function(capsule_function)

    def test_capsule_utils(self):
        c_1 = Capsule(data=[12, 13], name="First Capsule")
        c_2 = Capsule(data=[12, 13], name="First Capsule")
        c_representation = c_1.__repr__()
        expected_representation = "(data=[12, 13], name=First Capsule)"
        expected_from_dict = {"data": "gANdcQAoSwxLDWUu", "name": "First Capsule"}
        self.assertEqual(c_representation, expected_representation)
        self.assertEqual(c_1, c_2)
        self.assertEqual(c_1, Capsule.from_dict(expected_from_dict))

    def test_function_capsule_int(self):
        c_1 = Capsule(data=1, name="First Component")
        c_2 = Capsule(data=2, name="Second Component")

        node = op.capsule_function(c_1, c_2)
        capsule_res = self._client.run(node)

        self.assertEqual(capsule_res.name, "New Capsule")
        self.assertEqual(capsule_res.data, 3)

    def test_function_capsule_list(self):
        c_1 = Capsule(data=[1, 2, 3, 4, 5])
        c_2 = Capsule(data=[6, 7, 8, 9, 10], name="Second Component")

        node = op.capsule_function(c_1, c_2)
        capsule_res = self._client.run(node)

        self.assertEqual(capsule_res.name, "New Capsule")
        self.assertEqual(capsule_res.data, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_function_capsule_numpy(self):
        c_1 = Capsule(data=np.array([1, 2, 3, 4, 5]), name="First Component")
        c_2 = Capsule(data=np.array([6, 7, 8, 9, 10]), name="Second Component")

        node = op.capsule_function(c_1, c_2)
        capsule_res = self._client.run(node)

        self.assertEqual(capsule_res.name, "New Capsule")
        np.testing.assert_array_equal(capsule_res.data, np.array([7, 9, 11, 13, 15]))

    def test_function_capsule_dataframe(self):
        c_1 = Capsule(data=pd.DataFrame({"a": [1, 2, 3]}), name="First Component")
        c_2 = Capsule(data=2, name="Second Component")

        node = op.capsule_function(c_1, c_2)
        capsule_res = self._client.run(node)

        self.assertEqual(capsule_res.name, "New Capsule")
        np.testing.assert_array_equal(capsule_res.data, pd.DataFrame({"a": [3, 4, 5]}))
