import os, json
import tensorflow as tf
from functools import partial
from .keras_model import KerasModel

# For type hints
import numpy as np
from PIL import Image
from typing import Tuple


class GradCamModel(KerasModel):
    def __init__(self,
        model_path: str,
        input_width: int = 224,
        input_height: int = 224,
    ):
        super().__init__(model_path, input_width, input_height)

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

        # An intermediate model for computing Grad-CAM
        # - model.layers[-3].output: Flattened feature map of size 1 x (1+HW) x d
        #   - The feature map consists of (1+HW) d-dimensional feature vectors
        #   - The first feature vector, called `class token`, has no position information
        #   - The remaining HW features correspond to (H x W) tiled regions in the input image, respectively
        model_ = tf.keras.Model(
            inputs=model.input,
            outputs=[model.layers[-3].output, model.output]
        )

        # feature_dim = d
        feature_dim = model.layers[-4].output.shape[-2:]

        # Wrap the intermediate model for faster computation using tf.function
        predict_fn = tf.function(partial(self._predict_with_gradient, model=model_))

        # Preload the h5 model and the function
        dummy_input = tf.zeros((1, input_height, input_width, 3))
        _ = predict_fn(dummy_input)

        # Keep required variables
        self._model = model
        self._model_info = model_info
        self._predict_fn = predict_fn
        self._feature_dim = feature_dim
        self._input_width = input_width
        self._input_height = input_height

    @classmethod
    def _predict_with_gradient(cls,
        tensor_1hwc: tf.Tensor,
        model: tf.keras.Model,
    ) -> Tuple[tf.Tensor, tf.Tensor, tf.Tensor]:
        # Compute the flat-shaped (1+HW) feature vectors
        # and the strongest output activation
        with tf.GradientTape() as tape:
            feature, prediction = model(tensor_1hwc)

            # Choose output channel of the strongest activation,
            # which corresponds to the predicted class
            pred_index = tf.argmax(prediction[0])
            class_activation = prediction[:, pred_index]

        # Compute (1+HW) gradient vectors of the selected output
        # with respect to the (1+HW) feature vectors
        gradient = tape.gradient(class_activation, feature)
        return prediction[0], feature, gradient

    def predict_with_gradcam(self,
        pil_img: Image.Image,
    ) -> Tuple[np.ndarray, np.ndarray]:
        # Resize PIL image to (w, h) and convert to (1, h, w, 3) tensor
        tensor_1hwc = self._preprocess_image(pil_img)

        # Compute all outputs needed for Grad-CAM
        prediction, feature, gradient = self._predict_fn(tensor_1hwc)

        # Discard the first feature vector, called `class token`,
        # since it has no position information
        feature = tf.reshape(feature, self._feature_dim)[1:]
        gradient = tf.reshape(gradient, self._feature_dim)[1:]

        # Average pooling all gradient vectors over (H x W) positions
        pooled_gradient = tf.reduce_mean(gradient, axis=0)

        # Compute the contribution of each position's feature vector to the selected output,
        # which becomes a flat-shaped heatmap of size H x W
        heatmap = feature @ pooled_gradient[..., tf.newaxis]

        # Normalize the range of values in the heatmap to [0, 1]
        heatmap_0to1 = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)

        # Reshape heatmap
        sz = tf.cast(tf.sqrt(tf.cast(heatmap_0to1.shape[0], tf.float32)), tf.int32)
        heatmap_0to1 = tf.reshape(heatmap_0to1, (sz, sz))

        # Return prediction and heatmap
        return prediction.numpy(), heatmap_0to1.numpy()
