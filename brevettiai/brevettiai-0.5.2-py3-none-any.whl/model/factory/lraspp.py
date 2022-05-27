from typing import Tuple, Optional

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

from brevettiai.model.factory import ModelFactory


def ceil_divisible_by_8(x):
    return int(np.ceil(x / 8) * 8)


class LRASPPSegmentationHead(ModelFactory):
    avg_pool_kernel = (11, 11)
    avg_pool_strides = (4, 4)
    resize_method: str = tf.image.ResizeMethod.BILINEAR
    filter_bank_multiplier: int = 1
    bn_momentum: float = 0.99
    filter_bank: int = 64

    output_channels: Optional[int] = None

    def build(self, input_shape, output_shape, **kwargs):

        feature_out = None
        b1_b3_channels = output_shape
        if len(input_shape) > 2:
            feature_out = layers.Input(input_shape[0])
            input_shape = input_shape[-2:]
            b1_b3_channels = 16

        feature8 = tf.keras.Input(input_shape[0])

        feature16 = tf.keras.Input(input_shape[1])

        if feature_out is None:
            input_layers = [feature8, feature16]
        else:
            input_layers = [feature_out, feature8, feature16]


        # Branch 1
        b1 = layers.Conv2D(self.filter_bank, 1, padding="same", strides=1, name="branch1_conv")(feature16)
        b1 = layers.BatchNormalization(momentum=self.bn_momentum, axis=-1)(b1)
        b1 = layers.Activation(tf.nn.relu6)(b1)

        # Branch2
        b2 = layers.AveragePooling2D(pool_size=self.avg_pool_kernel, strides=self.avg_pool_strides, name="branch2_avg_pool")(feature16)
        b2 = layers.Conv2D(self.filter_bank, 1, strides=1, name="branch2_conv")(b2)
        b2 = layers.Activation("sigmoid")(b2)
        b2 = tf.compat.v1.image.resize_images(b2, size=tf.shape(b1)[1:3],
                                              align_corners=True,
                                              method=self.resize_method,
                                              preserve_aspect_ratio=False,
                                              name=None)

        # Branch 3
        b3 = layers.BatchNormalization(momentum=self.bn_momentum, axis=-1)(feature8)
        b3 = layers.Conv2D(b1_b3_channels, 1, strides=1, name="branch3_conv")(b3)

        # Connect
        x = layers.Multiply(name='b1_b2_merge/Mul')([b1, b2])
        x = tf.compat.v1.image.resize_images(x, size=tf.shape(b3)[1:3],
                                             align_corners=True,
                                             method=self.resize_method,
                                             preserve_aspect_ratio=False,
                                             name=None)
        x = layers.Conv2D(b1_b3_channels, 1, strides=1, name="branch1_2_conv")(x)

        x = layers.Add(name='b1_b3_merge/Add')([x, b3])

        if feature_out is not None:
            x = tf.compat.v1.image.resize_images(x, size=tf.shape(feature_out)[1:3],
                                                 align_corners=True,
                                                 method=self.resize_method,
                                                 preserve_aspect_ratio=False,
                                                 name=None)
            x = tf.keras.layers.Concatenate()([feature_out, x])
            x = tf.keras.layers.BatchNormalization(momentum=self.bn_momentum)(x)
            x = tf.keras.layers.Conv2D(output_shape[-1], 1, padding="same", name="branch_out_conv",
                                       kernel_regularizer=tf.keras.regularizers.l2())(x)

        model = tf.keras.Model(input_layers, x, name="LiteRASPP")
        return model


class LRASPP2SegmentationHead(ModelFactory):
    avg_pool_kernel: Tuple[int, int] = (11, 11)  #(25, 25)  #(11, 11)
    avg_pool_strides: Tuple[int, int] = (4, 4) #(8, 8)  #(4, 4)
    resize_method: str = tf.image.ResizeMethod.BILINEAR
    filter_bank_multiplier: int = 1
    bn_momentum: float = 0.99

    output_channels: Optional[int] = None

    def build(self, input_shape, output_shape, **kwargs):

        inputs = []
        for shape in input_shape:
            inputs.append(layers.Input(shape))

        # Branch 2
        b1 = inputs[-1]
        fb = max(8, ceil_divisible_by_8(b1.shape[-1] * self.filter_bank_multiplier))
        b1 = layers.Conv2D(fb, 1, padding="same", strides=1, name="branch1_conv")(b1)

        # Branch 1
        b2 = inputs[-1]
        b2 = layers.AveragePooling2D(pool_size=self.avg_pool_kernel, strides=self.avg_pool_strides, name="branch2_avg_pool")(b2)
        b2 = layers.Conv2D(fb, 1, strides=1, name="branch2_conv")(b2)
        b2 = layers.Activation("sigmoid")(b2)
        b2 = tf.compat.v1.image.resize_images(b2, size=tf.shape(b1)[1:3],
                                              align_corners=True,
                                              method=self.resize_method,
                                              preserve_aspect_ratio=False,
                                              name=None)

        x = layers.Multiply(name='b1_b2_merge/Mul')([b1, b2])

        for bix, branch in enumerate(inputs[1::-1], start=3):
            fb = max(8, ceil_divisible_by_8(branch.shape[-1]*self.filter_bank_multiplier))
            branch = layers.Conv2D(fb, 1, strides=1, name=f"branch{bix}_conv")(branch)

            x = layers.SeparableConv2D(fb, 3, padding="same", name=f"branch{bix-1}_{bix}_conv")(x)
            x = tf.keras.layers.BatchNormalization(momentum=self.bn_momentum)(x)
            x = layers.Activation("relu")(x)
            x = tf.compat.v1.image.resize_images(x, size=tf.shape(branch)[1:3],
                                                 align_corners=True,
                                                 method=self.resize_method,
                                                 preserve_aspect_ratio=False,
                                                 name=None)

            x = layers.Add(name=f'branch{bix-1}_{bix}_merge/Add')([x, branch])

        x = layers.SeparableConv2D(output_shape[-1], 3, padding="same", name="LRASPP_out_conv")(x)

        model = tf.keras.Model(inputs, x, name="LiteRASPP")
        return model


class LRASPP3SegmentationHead(ModelFactory):
    avg_pool_kernel: Tuple[int, int] = (11, 11)  #(25, 25)  #(11, 11)
    avg_pool_strides: Tuple[int, int] = (4, 4) #(8, 8)  #(4, 4)
    resize_method: str = tf.image.ResizeMethod.BILINEAR
    filter_bank_multiplier: int = 1
    bn_momentum: float = 0.99
    output_channels: Optional[int] = None

    def build(self, input_shape, output_shape, **kwargs):

        inputs = []
        for shape in input_shape:
            inputs.append(layers.Input(shape))

        # Branch 2
        b1 = inputs[-1]
        fb = max(8, ceil_divisible_by_8(b1.shape[-1] * self.filter_bank_multiplier))
        b1 = layers.Conv2D(fb, 1, padding="same", strides=1, name="branch1_conv")(b1)

        # Branch 1
        b2 = inputs[-1]
        b2 = layers.AveragePooling2D(pool_size=self.avg_pool_kernel, strides=self.avg_pool_strides, name="branch2_avg_pool")(b2)
        b2 = layers.Conv2D(fb, 1, strides=1, name="branch2_conv")(b2)
        b2 = layers.Activation("sigmoid")(b2)
        b2 = tf.compat.v1.image.resize_images(b2, size=tf.shape(b1)[1:3],
                                              align_corners=True,
                                              method=self.resize_method,
                                              preserve_aspect_ratio=False,
                                              name=None)

        x = layers.Multiply(name='b1_b2_merge/Mul')([b1, b2])

        for bix, branch in enumerate(inputs[1::-1], start=3):
            fb = max(8, ceil_divisible_by_8(branch.shape[-1]*self.filter_bank_multiplier))
            branch = layers.Conv2D(fb, 1, strides=1, name=f"branch{bix}_conv")(branch)

            #x = layers.SeparableConv2D(fb, 3, padding="same", name=f"branch{bix-1}_{bix}_conv")(x)
            x = layers.Conv2D(fb, 3, padding="same", name=f"branch{bix-1}_{bix}_conv")(x)
            x = tf.keras.layers.BatchNormalization(momentum=self.bn_momentum)(x)
            x = layers.Activation("relu")(x)
            x = tf.compat.v1.image.resize_images(x, size=tf.shape(branch)[1:3],
                                                 align_corners=True,
                                                 method=self.resize_method,
                                                 preserve_aspect_ratio=False,
                                                 name=None)

            x = layers.Add(name=f'branch{bix-1}_{bix}_merge/Add')([x, branch])

        #x = layers.SeparableConv2D(output_shape[-1], 3, padding="same", name="LRASPP_out_conv")(x)
        x = layers.Conv2D(output_shape[-1], 3, padding="same", name="LRASPP_out_conv")(x)

        model = tf.keras.Model(inputs, x, name="LiteRASPP")
        return model

