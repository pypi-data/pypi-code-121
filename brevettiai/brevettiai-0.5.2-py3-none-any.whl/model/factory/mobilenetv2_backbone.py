from functools import partial
from typing import List

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from brevettiai.model.factory import ModelFactory


def remap_backbone(bn_momentum, default_regularizer, exchange_padding_on):
    def _remap_backbone(layer):
        if isinstance(layer, tf.keras.Model):
            return tf.keras.models.clone_model(layer, input_tensors=None, clone_function=_remap_backbone)
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.momentum = bn_momentum
        elif isinstance(layer, layers.Conv2D):
            layer.kernel_regularizer = default_regularizer
            if layer.name in exchange_padding_on:
                # Exchange possible asymmetric zero_padding on layers
                layer.padding = "valid"
                return tf.keras.Sequential([
                    layers.ZeroPadding2D(1),
                    # layers.Lambda(zero_pad_to_even, name="zero_pad_to_even"),
                    layer.__class__.from_config(layer.get_config())]
                )
        return layer.__class__.from_config(layer.get_config())

    return _remap_backbone


class MobileNetV2SegmentationBackbone(ModelFactory):
    output_layers: List[str]
    weights: str = 'imagenet'
    alpha: float = 1
    bn_momentum: float = 0.9
    l1_regularization: float = 0
    l2_regularization: float = 0

    @staticmethod
    def custom_objects():
        return {
            "relu6": tf.nn.relu6
        }

    def build(self, input_shape, *args, **kwargs):
        if not self.weights is None and input_shape[-1] is not 3:
            bb_source = MobileNetV2(input_shape=(*input_shape[:-1], 3),
                                    include_top=False, weights=self.weights, alpha=self.alpha)
            backbone = MobileNetV2(input_shape=input_shape, include_top=False,
                                   weights=None, alpha=self.alpha)

            # Exchange layer 1 weights
            w = bb_source.get_weights()
            w[0] = w[0].sum(axis=2, keepdims=True)
            w[0] = np.tile(w[0], (1, 1, input_shape[-1], 1)) * np.random.randn(*w[0].shape) * 0.05
            backbone.set_weights(w)

        else:
            backbone = MobileNetV2(input_shape=input_shape,
                                   include_top=False,
                                   weights=self.weights,
                                   alpha=self.alpha)

        backbone = tf.keras.Model(backbone.input, [backbone.get_layer(l).output for l in self.output_layers],
                                  name=f"MobilenetV2_a{self.alpha}")

        if self.l1_regularization != 0 and self.l2_regularization != 0:
            default_regularizer = tf.keras.regularizers.l1l2(l1=self.l1_regularization, l2=self.l2_regularization)
        else:
            default_regularizer = None

        map_backbone = remap_backbone(bn_momentum=self.bn_momentum,
                                      default_regularizer=default_regularizer,
                                      exchange_padding_on={"Conv1"})

        backbone_clone = tf.keras.models.clone_model(backbone, clone_function=map_backbone)
        backbone_clone.set_weights(backbone.get_weights())
        return backbone_clone


lightning_segmentation_backbone = partial(
    MobileNetV2SegmentationBackbone,
    output_layers=['block_2_add', 'block_5_add', 'block_9_add'],
    alpha=0.35)

thunder_segmentation_backbone = partial(
    MobileNetV2SegmentationBackbone,
    output_layers=['expanded_conv_project', 'block_2_add', 'block_5_add', 'block_9_add', 'block_15_add'],
    alpha=0.35)