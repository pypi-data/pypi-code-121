from pydantic import PrivateAttr
import tensorflow as tf
from tensorflow.keras import layers
from typing import Optional, List, Tuple
from pydantic.typing import Literal
from tensorflow.python.keras.engine.functional import Functional
from brevettiai.model.factory import ModelFactory


class SegmentationModelFactory(ModelFactory):
    backbone_factory: ModelFactory
    head_factory: ModelFactory
    classes: List[str]
    bn_momentum: float = 0.9
    activation = "sigmoid"
    resize_method: Literal["bilinear", "nearest"] = "bilinear"
    resize_output: bool = False

    _backbone: Optional[Functional] = PrivateAttr(default=None)
    _head: Optional[Functional] = PrivateAttr(default=None)
    _model: Optional[Functional] = PrivateAttr(default=None)

    @property
    def backbone(self):
        return self._backbone

    @property
    def head(self):
        return self._head

    @property
    def model(self):
        return self._model

    def custom_objects(self):
        return {**self.backbone_factory.custom_objects(), **self.head_factory.custom_objects()}

    def build(self, input_shape: Tuple[Optional[int], Optional[int], Optional[int]], **kwargs):
        """Function to build the segmentation model and return the input and output keras tensors"""
        in_ = signal = tf.keras.layers.Input(input_shape)

        mean_init = tf.constant_initializer(127.5)  # Mean of uint8 values
        var_init = tf.constant_initializer(74 ** 2)  # ~Variance of uint8 values
        signal = layers.BatchNormalization(momentum=self.bn_momentum,
                                           moving_mean_initializer=mean_init,
                                           moving_variance_initializer=var_init)(signal)

        # Build backbones
        output_shape = (len(self.classes), )
        self._backbone = self.backbone_factory.build(signal.shape[1:], output_shape)
        self._head = self.head_factory.build([x.shape[1:] for x in self.backbone.outputs], output_shape)

        backbone_output = self.backbone(signal)
        signal = self.head(backbone_output)

        signal = layers.Activation(self.activation)(signal)

        if self.resize_output:
            signal = tf.compat.v1.image.resize_images(signal, size=tf.shape(in_)[1:3],
                                                      align_corners=True,
                                                      method=self.resize_method,
                                                      preserve_aspect_ratio=False,
                                                      name=None)

        self._model = tf.keras.models.Model(in_, signal)
        return self.model

