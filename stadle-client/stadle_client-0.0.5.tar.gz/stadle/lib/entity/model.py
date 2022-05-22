import pathlib
from typing import Any
import pickle

import numpy as np

from stadle.lib import BaseModelConvFormat, extract_weights_dict, merge_model_weights
from stadle.lib.env.handler import EnvironmentHandler

# TODO replace with conditional import
if EnvironmentHandler.pt_installed_flag():
    import torch

if EnvironmentHandler.tf_installed_flag():
    import tensorflow as tf


class BaseModel(object):
    """Base Model represents an entity which contains the Deep Learning Model
    Args:
        name: name of the model
        obj: deep learning model object (Torch Model, Tensorflow Model)
        type: Model Type (PyTorch, Tensorflow)
        id: model id
    """

    def __init__(self, name: str, obj: object, type: BaseModelConvFormat, id: str = None):
        """constructor
        """
        self._name = name
        self._obj = obj
        self._type = type
        self._id = id

        self.create_serialized_obj()
        self.extract_initial_weights()

    @property
    def name(self) -> str:
        """
        get the name of the model
        Returns:
        """
        return self._name

    @name.setter
    def name(self, name) -> None:
        """
        set the name of the model
        Args:
            name:
        """
        self._name = name

    @property
    def obj(self) -> Any:
        """
        get model object
        Returns:
        """
        return self._obj

    @obj.setter
    def obj(self, obj) -> None:
        """
        set model object
        Args:
            obj:
        """
        self._obj = obj

    @property
    def ser_obj(self) -> Any:
        """
        get model object
        Returns:
        """
        return self._ser_obj

    @ser_obj.setter
    def ser_obj(self, ser_obj) -> None:
        """
        set model object
        Args:
            obj:
        """
        self._ser_obj = ser_obj

    @property
    def weights(self) -> Any:
        """
        get model object
        Returns:
        """
        return self._weights

    @weights.setter
    def weights(self, weights) -> None:
        """
        set model object
        Args:
            obj:
        """
        self._weights = weights

    @property
    def type(self) -> BaseModelConvFormat:
        """
        get model type
        Returns:
        """
        return self._type

    @type.setter
    def type(self, type) -> None:
        """
        set model type
        Args:
            type:
        """
        self._type = type

    @property
    def id(self) -> str:
        """
        get model id
        Returns:
        """
        return self._id

    @id.setter
    def id(self, id) -> None:
        """
        set model id
        Args:
            id: unique id for the model
        """
        self._id = id

    def __str__(self):
        if (self._type == BaseModelConvFormat.pytorch_format):
            type_name = "PyTorch"
        elif (self._type == BaseModelConvFormat.keras_format):
            type_name = "Keras"
        elif (self._type == BaseModelConvFormat.tensorflow_format):
            type_name = "TensorFlow"
        else:
            type_name = "No Type Set"

        return f"Base Model: \n\tName: {self._name}\n\tType: {type_name}\n\tModel Object Serialized: {self._ser_obj != None}"
        #return "Model Name: " + self._name + "\n" + ", Model : " + self._ser_obj.__str__() + "\n" + "Type : " + str(
        #    self._type) + "\n" + "ID : " + self._id

    def create_serialized_obj(self):
        if self.type == BaseModelConvFormat.pytorch_format:
            self.ser_obj = self.obj.state_dict()
        elif self.type == BaseModelConvFormat.keras_format:
            self.ser_obj = self.obj.get_config()
        else:
            raise ValueError("Attempted to serialize base model obj without valid model type")

    def extract_initial_weights(self):
        self.weights = extract_weights_dict(self.obj, self.type)

    def prep_for_pickle(self):
        self.obj = None

    def save(self, data_path) -> None:
        """
        save the model
        Args:
            data_path: path to save the model
        Returns:
        """
        filepath = f"{data_path}/base_models/{self.id}.pkl"

        pathlib.Path(f'{data_path}/base_models').mkdir(exist_ok=True)

        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

        return filepath

    def get_merged_model(self, weight_dict):
        """
        get the fused model considering the based model and the updated weight vectors
        Args:
            weight_dict: weight dictionary
        Returns:
        """
        merged_model = merge_model_weights(self.obj, weight_dict, self.type)

        return merged_model

    def get_merged_ser_model(self, model_id, data_path):
        filepath = f"{data_path}/sample_models/{model_id}.binaryfile"

        with open(filepath, 'rb') as f:
            model_dict = pickle.load(f)

        if self.type == BaseModelConvFormat.pytorch_format:
            for key, val in model_dict.items():
                self.ser_obj[key] = torch.from_numpy(np.asarray(model_dict[key]))

            return self.ser_obj

        elif self.type == BaseModelConvFormat.keras_format:
            model = tf.keras.models.model_from_config(self.ser_obj)
            model_weights = model.get_weights()

            for k in model_dict:
                idx = int(k[6:])
                model_weights[idx] = model_dict[k]

            model.set_weights(model_weights)
            return model
        else:
            raise ValueError("Attempted to create merged model without valid model type")
