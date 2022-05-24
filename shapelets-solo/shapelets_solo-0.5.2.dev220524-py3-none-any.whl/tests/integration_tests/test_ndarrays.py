# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

import numpy as np

from shapelets import init_session
from shapelets.model import NDArray
from shapelets.services import ShapeletsException
from shapelets.dsl import dsl_op as op


class NDArraysTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._input_array = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        cls._nd_array = cls._client.create_nd_array(
            array=cls._input_array, name="test1",
            description="Description test")
        cls._input_multi_array = np.array(
            [
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            ])
        cls._multi_nd_array = cls._client.create_nd_array(array=cls._input_multi_array, name="multitest1",
                                                          description="Description test")

    def test_create_nd_array(self):
        input_array = np.array([1, 2, 3, 4, 5])
        nd_array = self._client.create_nd_array(array=input_array, name="test1", description="Description test")
        self.assertEqual(nd_array.name, "test1")
        self.assertEqual(nd_array.description, "Description test")
        self.assertTupleEqual(nd_array.dims, input_array.shape)
        self.assertEqual(nd_array.dtype, input_array.dtype)

    def test_nd_array_get_data(self):
        array_data = self._client.get_nd_array_data(self._nd_array)
        np.testing.assert_array_equal(array_data, self._input_array)

    def test_multi_nd_array_get_data(self):
        array_data = self._client.get_nd_array_data(self._multi_nd_array)
        np.testing.assert_array_equal(array_data, self._input_multi_array)

    def test_nd_array_delete(self):
        input_array = np.array([1, 2, 3, 4, 5])
        nd_array = self._client.create_nd_array(array=input_array, name="test1", description="Description test")
        self._client.delete_nd_array(nd_array)
        with self.assertRaises(ShapeletsException):
            self._client.get_nd_array_data(nd_array)

    def test_nd_array_update_name(self):
        nd_array = self._nd_array
        nd_array.name = "Shapelets"
        update_nd_array = self._client.update_nd_array(nd_array)
        self.assertEqual(update_nd_array.name, "Shapelets")

    def test_nd_array_update_array_dims(self):
        input_array = np.array([1, 2, 3, 4, 5, 6])
        nd_array = self._client.create_nd_array(array=input_array, name="test1", description="Description test")
        self.assertEqual(nd_array.dims, (6,))
        nd_array.dims = (2, 3)
        update_nd_array = self._client.update_nd_array(nd_array)
        self.assertEqual(update_nd_array.dims, (2, 3))
        np_array = self._client.get_nd_array_data(update_nd_array)
        np.testing.assert_array_equal(np_array, np.array([[1, 2, 3], [4, 5, 6]]))

    def test_nd_array_update_array_data_with_different_dims(self):
        input_array = np.array([1, 2, 3, 4, 5, 6])
        nd_array = self._client.create_nd_array(array=input_array, name="test1", description="Description test")
        np_array = np.array([[11, 12, 13], [14, 15, 16]])
        with self.assertRaises(ShapeletsException):
            self._client.update_nd_array(nd_array, np_array)

    def test_nd_array_update_array_data_with_different_types(self):
        input_array = np.array([1, 2, 3, 4, 5, 6], dtype=np.dtype("float64"))
        nd_array = self._client.create_nd_array(array=input_array, name="test1", description="Description test")
        np_array = np.array([1, 2, 3, 4, 5, 6], dtype=np.dtype("int32"))
        with self.assertRaises(ShapeletsException):
            self._client.update_nd_array(nd_array, np_array)

    def test_nd_array_update_array_data(self):
        input_array = np.array([1, 2, 3, 4, 5, 6], dtype=np.dtype("float64"))
        nd_array = self._client.create_nd_array(array=input_array, name="test1", description="Description test")
        np_array = np.array([11, 12, 13, 14, 15, 16], dtype=np.dtype("float64"))
        update_nd_array = self._client.update_nd_array(nd_array, np_array)
        update_np_array = self._client.get_nd_array_data(update_nd_array)
        np.testing.assert_array_equal(update_np_array, np.array([11, 12, 13, 14, 15, 16]))
        self.assertEqual(update_np_array.shape, (6,))
        self.assertEqual(update_np_array.dtype, np.dtype("float64"))

    def test_get_nd_array_data(self):
        client = NDArraysTest._client
        res = NDArraysTest._client.run(op.filter_nd_array(lambda x: x > 3, NDArraysTest._nd_array))
        res_data = client.get_nd_array_data(res)
        np.testing.assert_array_equal(np.array([4, 5, 6, 7, 8, 9, 10]), res_data)
