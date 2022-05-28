import os, json
import tensorflow as tf
from functools import partial

# For type hints
import numpy as np
from PIL import Image
from typing import Any, List, Dict


class KerasModel(object):
    def __init__(self,
        model_path: str,
        input_width: int = 224,
        input_height: int = 224,
    ):
        super().__init__()
        self.__initialize__(model_path, input_width, input_height)

    def __initialize__(self,
        model_path: str,
        input_width: int = 224,
        input_height: int = 224,
    ) -> None:
        # Load h5 model
        model = tf.keras.models.load_model(model_path)

        # Load model info
        model_info_path = os.path.splitext(model_path)[0] + '.json'
        model_info = json.load(open(model_info_path))

        # Wrap the model for faster computation using tf.function
        predict_fn = tf.function(partial(self._predict, model=model))

        # Preload the h5 model and the function
        dummy_input = tf.zeros((1, input_height, input_width, 3))
        _ = predict_fn(dummy_input)

        # Keep required variables
        self._model = model
        self._model_info = model_info
        self._predict_fn = predict_fn
        self._input_width = input_width
        self._input_height = input_height

    @property
    def model(self) -> tf.keras.Model:
        return self._model

    @property
    def model_info(self) -> Dict[str, Any]:
        return self._model_info

    @classmethod
    def _predict(cls,
        tensor_1hwc: tf.Tensor,
        model: tf.keras.Model,
    ) -> tf.Tensor:
        # Wrap the model for faster computation using tf.function
        return model(tensor_1hwc)

    def _preprocess_image(self,
        pil_img: Image.Image,
    ) -> tf.Tensor:
        # Resize PIL image to (w, h) and convert to (1, h, w, 3) tensor
        resized_img = pil_img.resize((self._input_width, self._input_height))
        tensor_hwc = tf.keras.preprocessing.image.img_to_array(resized_img)
        tensor_1hwc = tf.expand_dims(tensor_hwc, 0)
        return tensor_1hwc

    def predict(self,
        pil_img: Image.Image,
    ) -> np.ndarray:
        # Resize PIL image to (w, h) and convert to (1, h, w, 3) tensor
        tensor_1hwc = self._preprocess_image(pil_img)

        # Compute prediction
        prediction = self._predict_fn(tensor_1hwc)
        return prediction[0].numpy()

    def get_top1_class(self,
        prediction: np.ndarray,
    ) -> Dict[str, Any]:
        # Return the class with the highest prediction score
        cls_index = prediction.argmax()
        cls = self.model_info['options'][cls_index]
        confidence = prediction[cls_index]
        return { 'name': cls['name'], 'confidence': confidence }

    def get_all_classes(self,
        prediction: np.ndarray,
    ) -> List[Dict[str, Any]]:
        # Return all classes with their prediction scores
        return [
            { 'name': cls['name'], 'confidence': confidence }
            for cls, confidence in zip(self.model_info['options'], prediction)
            if confidence > cls.get('score_thres', 0)
        ]
