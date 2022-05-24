# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

from shapelets import init_session
# from keras.models import Sequential
# from keras.layers import Dense
from shapelets.model import Model
from shapelets.dsl import dsl_op as op


def model_function(model: Model) -> Model:
    md = model.data
    md.append(22)
    new_metadata = {
        "layers": "22"
    }
    return Model(name="New Model", description="My new model", data=md, metadata=new_metadata)


class NDArraysTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._client = init_session("admin", "admin", "https://127.0.0.1")
        cls._model = [1, 2, 3, 4, 5]
        # cls._model = Sequential()
        # cls._model.add(Dense(12, input_dim=8, activation='relu'))
        # cls._model.add(Dense(8, activation='relu'))
        # cls._model.add(Dense(1, activation='sigmoid'))
        # cls._model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        cls._model_metadata = {
            "layers": "3",
            "train set size": "X"
        }
        cls._shapelets_model = cls._client.create_model(model=cls._model,
                                                        name="model1",
                                                        description="My First Model",
                                                        metadata=cls._model_metadata)

    def test_model_utils(self):
        model_1 = Model("id_1", "model1", "My First Model", self._model, {"layers": "3"})
        model_2 = Model("id_1", "model1", "My First Model", self._model, {"layers": "3"})
        model_representation = model_1.__repr__()
        expected_representation = """model(model_id=id_1, name=model1, description=My First Model, data=[1, 2, 3, 4, 5], metadata={\'layers\': \'3\'} """
        self.assertEqual(model_representation, expected_representation)
        self.assertEqual(model_1, model_2)

    def test_create_model(self):
        model = self._shapelets_model
        self.assertEqual(model.name, "model1")
        self.assertEqual(model.description, "My First Model")
        self.assertEqual(model.metadata, self._model_metadata)

    def test_model_get_data(self):
        model_data = self._client.get_model_data(self._shapelets_model)
        # For Keras Model
        # self.assertEqual(model_data.get_config(), self._model.get_config())
        self.assertEqual(model_data, self._model)

    def test_model_delete(self):
        model = self._client.create_model(self._model, "Model2", "Model to be deleted")
        self.assertTrue(self._client.delete_model(model))

    def test_model_update_name(self):
        model = self._shapelets_model
        model.name = "Shapelets"
        model.description = "Model Updated"
        update_model = self._client.update_model(model)
        self.assertEqual(update_model.name, "Shapelets")
        self.assertEqual(model.description, "Model Updated")

    def test_model_update_data(self):
        model = self._shapelets_model
        new_model = [6, 7, 8, 9, 10]
        new_metadata = {
            "layers": "2",
            "train set size": "Y"
        }
        model.metadata = new_metadata
        update_model = self._client.update_model(model, new_model)
        update_data = self._client.get_model_data(update_model)
        self.assertEqual(update_model.name, model.name)
        self.assertEqual(update_model.description, model.description)
        self.assertEqual(model.metadata, new_metadata)
        self.assertEqual(update_data, new_model)

    def test_register_model_function(self):
        self._client.register_custom_function(model_function)
        model = self._shapelets_model
        res1 = op.model_function(model)
        res_model = self._client.run(res1)
        res_data = self._client.get_model_data(res_model)
        self.assertEqual(res_model.name, "New Model")
        self.assertEqual(res_model.description, "My new model")
        self.assertEqual(res_model.metadata, {"layers": "22"})
        self.assertEqual(res_data, [1, 2, 3, 4, 5, 22])
