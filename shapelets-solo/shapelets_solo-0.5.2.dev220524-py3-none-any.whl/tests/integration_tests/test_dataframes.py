# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
import pandas as pd

from shapelets import init_session
from shapelets.model import Dataframe
from shapelets.services import ShapeletsException
from shapelets.dsl import dsl_op as op


def function_dataframe(dataframe: Dataframe) -> Dataframe:
    df = dataframe.dataframe
    df["a*b"] = df["a"] * df["b"]
    shapelets_df = Dataframe.make_dataframe(df, "New Dataframe", "Dataframe Description")
    return shapelets_df


class DataframeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        _data = [2.1, 4.2, 10.8, 22.2, -5.5, 2.1, 4.2, 13.8, 2.2, -0.5, 2.1, 4.2, 11.8, 22.2, -5.5]
        _freq = pd.tseries.offsets.DateOffset(microseconds=3600000000)
        cls._input_dataframe = pd.DataFrame(_data,
                                            index=pd.date_range("2019-01-10 20:08", periods=len(_data), freq=_freq))

        cls._shapelets_dataframe = cls._client.create_dataframe(dataframe=cls._input_dataframe,
                                                                name="Dataframe1",
                                                                description="Description test")

    def test_create_dataframe(self):
        data = [1, 2, 3, 4, 5]
        freq = pd.tseries.offsets.DateOffset(microseconds=3600000000)
        dataframe = pd.DataFrame(data, index=pd.date_range("2019-01-10 20:08", periods=len(data), freq=freq))
        shapelets_dataframe = self._client.create_dataframe(dataframe, name="test1", description="Description test")
        self.assertEqual(shapelets_dataframe.name, "test1")
        self.assertEqual(shapelets_dataframe.description, "Description test")
        self.assertEqual(shapelets_dataframe.col_names, ["0"])
        self.assertEqual(shapelets_dataframe.col_types, ["int64"])
        self.assertEqual(shapelets_dataframe.has_index, True)
        self.assertEqual(shapelets_dataframe.index_type, "datetime64[ns]")
        self.assertEqual(shapelets_dataframe.n_cols, 1)
        self.assertEqual(shapelets_dataframe.n_rows, len(data))

    def test_create_dataframe_without_name_or_description(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        shapelets_df = self._client.create_dataframe(df)
        self.assertEqual(shapelets_df.name, "")
        self.assertEqual(shapelets_df.description, "")
        self.assertEqual(shapelets_df.col_names, ["a", "b"])
        self.assertEqual(shapelets_df.col_types, ["int64", "int64"])
        self.assertEqual(shapelets_df.has_index, True)
        self.assertEqual(shapelets_df.index_type, "int64")
        self.assertEqual(shapelets_df.n_cols, 2)
        self.assertEqual(shapelets_df.n_rows, 3)

    def test_create_dataframe_with_multiple_columns(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        shapelets_df = self._client.create_dataframe(df, name="test2", description="Description test")
        self.assertEqual(shapelets_df.name, "test2")
        self.assertEqual(shapelets_df.description, "Description test")
        self.assertEqual(shapelets_df.col_names, ["a", "b"])
        self.assertEqual(shapelets_df.col_types, ["int64", "int64"])
        self.assertEqual(shapelets_df.has_index, True)
        self.assertEqual(shapelets_df.index_type, "int64")
        self.assertEqual(shapelets_df.n_cols, 2)
        self.assertEqual(shapelets_df.n_rows, 3)

    def test_dataframe_get_data(self):
        dataframe_data = self._client.get_dataframe_data(self._shapelets_dataframe)
        self.assertTrue(dataframe_data.equals(self._input_dataframe))

    def test_dataframe_delete(self):
        data = [1, 2, 3, 4, 5]
        freq = pd.tseries.offsets.DateOffset(microseconds=3600000000)
        dataframe = pd.DataFrame(data, index=pd.date_range("2019-01-10 20:08", periods=len(data), freq=freq))
        shapelets_dataframe = self._client.create_dataframe(dataframe, name="test1", description="Description test")
        self.assertTrue(self._client.delete_dataframe(shapelets_dataframe))
        with self.assertRaises(ShapeletsException):
            self._client.get_dataframe_data(shapelets_dataframe)

    def test_dataframe_update_name(self):
        dataframe = self._shapelets_dataframe
        dataframe.name = "Shapelets"
        dataframe.description = "Shapelets Description"
        update_daframe = self._client.update_dataframe(dataframe)
        self.assertEqual(update_daframe.name, "Shapelets")
        self.assertEqual(update_daframe.description, "Shapelets Description")

    def test_dataframe_update_new_dataframe(self):
        shapelets_dataframe = self._shapelets_dataframe
        shapelets_dataframe.name = "Updated Dataframe"
        shapelets_dataframe.description = "Updated Description"
        data = [1, 2, 3, 4, 5]
        freq = pd.tseries.offsets.DateOffset(microseconds=3600000000)
        new_dataframe = pd.DataFrame(data, index=pd.date_range("2019-01-10 20:08", periods=len(data), freq=freq))
        shapelets_dataframe_updated = self._client.update_dataframe(shapelets_dataframe, new_dataframe)
        shapelets_dataframe_updated_data = self._client.get_dataframe_data(shapelets_dataframe_updated)
        self.assertEqual(shapelets_dataframe_updated.name, "Updated Dataframe")
        self.assertEqual(shapelets_dataframe_updated.description, "Updated Description")
        self.assertTrue(shapelets_dataframe_updated_data.equals(new_dataframe))
        self.assertFalse(shapelets_dataframe_updated_data.equals(self._input_dataframe))

    def test_register_dataframe_function(self):
        self._client.register_custom_function(function_dataframe)
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        shapelets_df = self._client.create_dataframe(df, name="test3", description="Description test")
        expected_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "a*b": [4, 10, 18]})
        res_df = self._client.run(op.function_dataframe(shapelets_df))
        res_df_data = self._client.get_dataframe_data(res_df)
        self.assertEqual(res_df.name, "New Dataframe")
        self.assertEqual(res_df.description, "Dataframe Description")
        self.assertTrue(res_df_data.equals(expected_df))

    def test_register_dataframe_function_without_name_or_description(self):
        self._client.register_custom_function(function_dataframe)
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        shapelets_df = self._client.create_dataframe(df)
        expected_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "a*b": [4, 10, 18]})
        res_df = self._client.run(op.function_dataframe(shapelets_df))
        res_df_data = self._client.get_dataframe_data(res_df)
        self.assertEqual(res_df.name, "New Dataframe")
        self.assertEqual(res_df.description, "Dataframe Description")
        self.assertTrue(res_df_data.equals(expected_df))
