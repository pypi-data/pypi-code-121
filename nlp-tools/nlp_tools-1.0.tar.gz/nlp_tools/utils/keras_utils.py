# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Utilities for tf.keras."""

import tensorflow as tf
import tensorflow.keras.backend as K

def is_tensor_or_variable(x):
    return tf.is_tensor(x) or isinstance(x,tf.Variable)

class LossFunctionWrapper(tf.keras.losses.Loss):
    """Wraps a loss function in the `Loss` class."""
    def __init__(self,fn,reduction=tf.keras.losses.Reduction.AUTO,name=None,**kwargs):
        """Initializes `LossFunctionWrapper` class.
                Args:
                  fn: The loss function to wrap, with signature `fn(y_true, y_pred,
                    **kwargs)`.
                  reduction: (Optional) Type of `tf.keras.losses.Reduction` to apply to
                    loss. Default value is `AUTO`. `AUTO` indicates that the reduction
                    option will be determined by the usage context. For almost all cases
                    this defaults to `SUM_OVER_BATCH_SIZE`. When used with
                    `tf.distribute.Strategy`, outside of built-in training loops such as
                    `tf.keras` `compile` and `fit`, using `AUTO` or `SUM_OVER_BATCH_SIZE`
                    will raise an error. Please see this custom training [tutorial](
                      https://www.tensorflow.org/tutorials/distribute/custom_training)
                    for more details.
                  name: (Optional) name for the loss.
                  **kwargs: The keyword arguments that are passed on to `fn`.
                """
        super().__init__(reduction=reduction,name=name)
        self.fn = fn
        self._fn_kwargs = kwargs

    def call(self,y_true,y_pred):
        """Invokes the `LossFunctionWrapper` instance.
                Args:
                  y_true: Ground truth values.
                  y_pred: The predicted values.
                Returns:
                  Loss values per sample.
                """
        return self.fn(y_true,y_pred,**self._fn_kwargs)

    def get_config(self):
        config = {}
        for k,v in iter(self._fn_kwargs.items()):
            config[k] = tf.keras.backend.eval(v) if is_tensor_or_variable(v) else v
        base_config = super(LossFunctionWrapper, self).get_config().get_config()
        return {**base_config, **config}


def normalize_data_format(value):
    if value is None:
        value = tf.keras.backend.image_data_format()
    data_format = value.lower()
    if data_format not in {"channels_first", "channels_last"}:
        raise ValueError(
            "The `data_format` argument must be one of "
            '"channels_first", "channels_last". Received: ' + str(value)
        )
    return data_format


def sequence_masking(x, mask,value =0.0,axis=None):
    """为序列条件mask的函数
        mask: 形如(batch_size, seq_len)的0-1矩阵；
        value: mask部分要被替换成的值，可以是'-inf'或'inf'；
        axis: 序列所在轴，默认为1；
        """
    if mask is None:
        return x
    else:
        if K.dtype(mask) != K.dtype(x):
            mask = K.cast(mask,K.dtype(x))

        if value == '-inf':
            value = -1e12
        elif value == 'inf':
            value = 1e12

        if axis is None:
            axis =1
        elif axis < 0:
            axis = K.ndim(x) + axis

        assert  axis > 0, 'axis must be greater than 0'
        for _ in range(axis - 1):
            mask = K.expand_dims(mask, 1)

        for _ in range(K.ndim(x) - K.ndim(mask)):
            mask = K.expand_dims(mask,K.ndim(mask))

        return x * mask + value * (1 - mask)