# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Custom layers not natively supported by Keras."""

import keras
from keras import backend as K
from keras.utils import conv_utils
from keras.engine import InputSpec

import tensorflow as tf
import numpy as np


class InstanceNormalization(keras.layers.Layer):
    """Instance normalization layer.

    Normalize the activations of the previous layer at each step,
    i.e. applies a transformation that maintains the mean activation
    close to 0 and the activation standard deviation close to 1.
    - [Layer Normalization](https://arxiv.org/abs/1607.06450)
    - [Instance Normalization: The Missing Ingredient for Fast Stylization](
    https://arxiv.org/abs/1607.08022)

    Attributes:
        axis: Integer, the axis that should be normalized
            (typically the features axis).
            For instance, after a `Conv2D` layer with
            `data_format="channels_first"`,
            set `axis=1` in `InstanceNormalization`.
            Setting `axis=None` will normalize all values in each
            instance of the batch.
            Axis 0 is the batch dimension. `axis` cannot be set to 0 to avoid errors.
        epsilon: Small float added to variance to avoid dividing by zero.
        center: If True, add offset of `beta` to normalized tensor.
            If False, `beta` is ignored.
        scale: If True, multiply by `gamma`.
            If False, `gamma` is not used.
            When the next layer is linear (also e.g. `nn.relu`),
            this can be disabled since the scaling
            will be done by the next layer.
        beta_initializer: Initializer for the beta weight.
        gamma_initializer: Initializer for the gamma weight.
        beta_regularizer: Optional regularizer for the beta weight.
        gamma_regularizer: Optional regularizer for the gamma weight.
        beta_constraint: Optional constraint for the beta weight.
        gamma_constraint: Optional constraint for the gamma weight.
    """

    def __init__(self,
                 axis=None,
                 epsilon=1e-3,
                 center=True,
                 scale=True,
                 beta_initializer='zeros',
                 gamma_initializer='ones',
                 beta_regularizer=None,
                 gamma_regularizer=None,
                 beta_constraint=None,
                 gamma_constraint=None,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.supports_masking = True
        self.axis = axis
        self.epsilon = epsilon
        self.center = center
        self.scale = scale
        self.beta_initializer = keras.initializers.get(beta_initializer)
        self.gamma_initializer = keras.initializers.get(gamma_initializer)
        self.beta_regularizer = keras.regularizers.get(beta_regularizer)
        self.gamma_regularizer = keras.regularizers.get(gamma_regularizer)
        self.beta_constraint = keras.constraints.get(beta_constraint)
        self.gamma_constraint = keras.constraints.get(gamma_constraint)

    def build(self, input_shape):
        """Build."""
        ndim = len(input_shape)
        if self.axis == 0:
            raise ValueError('Axis cannot be zero')

        if (self.axis is not None) and (ndim == 2):
            raise ValueError('Cannot specify axis for rank 1 tensor')

        self.input_spec = InputSpec(ndim=ndim)

        if self.axis is None:
            shape = (1,)
        else:
            shape = (input_shape[self.axis],)

        if self.scale:
            self.gamma = self.add_weight(shape=shape,
                                         name='gamma',
                                         initializer=self.gamma_initializer,
                                         regularizer=self.gamma_regularizer,
                                         constraint=self.gamma_constraint)
        else:
            self.gamma = None
        if self.center:
            self.beta = self.add_weight(shape=shape,
                                        name='beta',
                                        initializer=self.beta_initializer,
                                        regularizer=self.beta_regularizer,
                                        constraint=self.beta_constraint)
        else:
            self.beta = None
        self.built = True

    def call(self, inputs, training=None):
        """Instance Normalization"""
        input_shape = K.int_shape(inputs)
        reduction_axes = list(range(0, len(input_shape)))

        if self.axis is not None:
            del reduction_axes[self.axis]

        del reduction_axes[0]

        mean = K.mean(inputs, reduction_axes, keepdims=True)

        # @scha: keras_contrib implementation of InstanceNorm has a bug
        # stddev should be sqrt(variance + epsion) but it was calculated as
        # sqrt(variance) + epsilon
        stddev = tf.sqrt(K.var(inputs, reduction_axes, keepdims=True) + self.epsilon)
        normed = (inputs - mean) / stddev

        broadcast_shape = [1] * len(input_shape)
        if self.axis is not None:
            broadcast_shape[self.axis] = input_shape[self.axis]

        if self.scale:
            broadcast_gamma = K.reshape(self.gamma, broadcast_shape)
            normed = normed * broadcast_gamma
        if self.center:
            broadcast_beta = K.reshape(self.beta, broadcast_shape)
            normed = normed + broadcast_beta
        return normed

    def get_config(self):
        """Keras layer get config."""
        config = {
            'axis': self.axis,
            'epsilon': self.epsilon,
            'center': self.center,
            'scale': self.scale,
            'beta_initializer': keras.initializers.serialize(self.beta_initializer),
            'gamma_initializer': keras.initializers.serialize(self.gamma_initializer),
            'beta_regularizer': keras.regularizers.serialize(self.beta_regularizer),
            'gamma_regularizer': keras.regularizers.serialize(self.gamma_regularizer),
            'beta_constraint': keras.constraints.serialize(self.beta_constraint),
            'gamma_constraint': keras.constraints.serialize(self.gamma_constraint)
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class SliceLayer(keras.layers.Layer):
    """A Keras layer to slice a tf tensor.

    Currently implementation, hardcode the slicing depending on the provided axes.
    TODO: change to tf.stride_slice().

    Attributes:
        axes: Axes to slice.
        starts: Start index.
        ends: End index.
        steps: Step size.
    """

    def __init__(self,
                 axes,
                 starts,
                 ends,
                 steps=1,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.axes = axes
        self.starts = starts
        self.ends = ends
        self.steps = steps
        self.output_dim = None

    def call(self, inputs):
        """Slice based on axes."""
        if self.axes == 0:
            out = inputs[self.starts:self.ends:self.steps]
        elif self.axes == 1:
            out = inputs[:, self.starts:self.ends:self.steps]
        elif self.axes == 2:
            out = inputs[:, :, self.starts:self.ends:self.steps]
        elif self.axes == 3:
            out = inputs[:, :, :, self.starts:self.ends:self.steps]
        elif self.axes == 4:
            out = inputs[:, :, :, :, self.starts:self.ends:self.steps]
        else:
            raise AttributeError('Not implemented')
        self.output_dim = out.get_shape().as_list()
        return out

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        # Need to return tuple. tensor.shape returns tenors not tuple
        # So if we just concat, then we get tuple of tensors
        if isinstance(input_shape, int):
            inp = input_shape
        else:
            inp = input_shape[0]
        shapes = []
        for i, sh in enumerate(self.output_dim):
            if i == 0:
                shapes.append(inp)
            else:
                shapes.append(sh)
        return tuple(shapes)

    def get_config(self):
        """Keras layer get config."""
        config = {
            'axes': self.axes,
            'starts': self.starts,
            'ends': self.ends,
            'steps': self.steps,
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ImageResizeLayer(keras.layers.Layer):
    """Resize Images to a specified size

    Ref https://stackoverflow.com/questions/41903928/add-a-resizing-layer-to-a-keras-sequential-model

    Attributes:
        output_dim: Size of output layer width and height.
        output_scale: scale compared with input
        data_format: A string,
            one of `channels_first` (default) or `channels_last`.
        mode: A string,
            one of `nearest` (default) or `bilinear`.

    # Input shape
        - If `data_format='channels_last'`:
            4D tensor with shape:
            `(batch_size, rows, cols, channels)`
        - If `data_format='channels_first'`:
            4D tensor with shape:
            `(batch_size, channels, rows, cols)`

    # Output shape
        - If `data_format='channels_last'`:
            4D tensor with shape:
            `(batch_size, pooled_rows, pooled_cols, channels)`
        - If `data_format='channels_first'`:
            4D tensor with shape:
            `(batch_size, channels, pooled_rows, pooled_cols)`
    """

    def __init__(self,
                 output_dim=(1, 1),
                 output_scale=None,
                 data_format='channels_first',
                 mode="nearest",
                 coordinate_transformation_mode="half_pixel",
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.naive_output_dim = conv_utils.normalize_tuple(output_dim,
                                                           2, 'output_dim')

        self.data_format = data_format
        if isinstance(output_scale, (list, np.ndarray)):
            output_scale = output_scale[0]
        self.naive_output_scale = output_scale
        self.mode = mode.lower()

        self.coordinate_transformation_mode = coordinate_transformation_mode

        if self.mode == "linear":
            self.mode = "bilinear"

        self.input_spec = InputSpec(ndim=4)

    def build(self, input_shape):
        """Build."""
        self.input_spec = [InputSpec(shape=input_shape)]
        if self.naive_output_scale is not None:
            if self.data_format == 'channels_first':
                self.output_dim = (self.naive_output_scale * input_shape[2],
                                   self.naive_output_scale * input_shape[3])
            elif self.data_format == 'channels_last':
                self.output_dim = (self.naive_output_scale * input_shape[1],
                                   self.naive_output_scale * input_shape[2])
        else:
            self.output_dim = self.naive_output_dim

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        if self.data_format == 'channels_first':
            return (input_shape[0], input_shape[1], self.output_dim[0], self.output_dim[1])
        return (input_shape[0], self.output_dim[0], self.output_dim[1], input_shape[3])

    def call(self, inputs):
        """Resize."""
        if self.data_format == 'channels_first':
            # inputs = keras.layers.Permute((2, 3, 1))(inputs)
            inputs = tf.transpose(inputs, perm=[0, 2, 3, 1])

        # Upsampling in TF1.x is implemented incorrectly
        # https://machinethink.net/blog/coreml-upsampling/
        # As a result, align_corners=True must be set in order to be compatiable with other frameworks
        output = tf.image.resize_images(inputs, self.output_dim, self.mode, align_corners=(self.coordinate_transformation_mode == "align_corners"))

        if self.data_format == 'channels_first':
            # output = keras.layers.Permute((3, 1, 2))(output)
            output = tf.transpose(output, perm=[0, 3, 1, 2])

        return output

    def get_config(self):
        """Keras layer get config."""
        config = {'output_dim': self.output_dim,
                  'data_format': self.data_format,
                  'mode': self.mode,
                  'coordinate_transformation_mode': self.coordinate_transformation_mode}
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class EqualLayer(keras.layers.Layer):
    """Elementwise equal with broadcast support.

    Native Keras only supports elementwise equal w/ same input shape.
    Broadcasting is allowed in tf tensor operation.

    Attributes:
        output_dim: Dimension of the output from the layer
    """

    def __init__(self,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.output_dim = None

    def call(self, inputs):
        """Equal."""
        # out = tf.equal(x[0], x[1])
        out = K.equal(inputs[0], inputs[1])
        self.output_dim = out.get_shape().as_list()
        return out

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        # Need to return tuple. tensor.shape returns tenors not tuple
        # So if we just concat, then we get tuple of tensors
        shapes = []
        for i, sh in enumerate(self.output_dim):
            if i == 0:  # Batch dim
                shapes.append(None)
            else:
                shapes.append(sh)
        return tuple(shapes)

    def get_config(self):
        """Keras layer get config."""
        # config = {'output_dim': self.output_dim}
        config = {}
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class MultiplyLayer(keras.layers.Layer):
    """Elementwise multiply with broadcast support.

    Native Keras only supports elementwise multiply w/ same input shape.
    Broadcasting is allowed in tf tensor operation.

    Attributes:
        output_dim: Dimension of the output from the layer
    """

    def __init__(self,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.output_dim = None

    def call(self, inputs):
        """Multiply."""
        out = tf.math.multiply(inputs[0], inputs[1])
        # out = inputs[0] * inputs[1]
        self.output_dim = out.get_shape().as_list()
        return out

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        # Need to return tuple. tensor.shape returns tenors not tuple
        # So if we just concat, then we get tuple of tensors
        shapes = []
        for i, sh in enumerate(self.output_dim):
            if i == 0:  # Batch dim
                shapes.append(None)
            else:
                shapes.append(sh)
        return tuple(shapes)

    def get_config(self):
        """Keras layer get config."""
        # config = {'output_dim': self.output_dim}
        config = {}
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class DivideLayer(keras.layers.Layer):
    """Elementwise divide with broadcast support.

    Native Keras only supports elementwise divide w/ same input shape.
    Broadcasting is allowed in tf tensor operation.

    Attributes:
        output_dim: Dimension of the output from the layer
    """

    def __init__(self,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.output_dim = None

    def call(self, inputs):
        """Divide."""
        out = tf.math.divide(inputs[0], inputs[1])
        # out = inputs[0] / inputs[1]
        self.output_dim = out.get_shape().as_list()
        return out

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        # Need to return tuple. tensor.shape returns tenors not tuple
        # So if we just concat, then we get tuple of tensors
        shapes = []
        for i, sh in enumerate(self.output_dim):
            if i == 0:  # Batch dim
                shapes.append(None)
            else:
                shapes.append(sh)
        return tuple(shapes)

    def get_config(self):
        """Keras layer get config."""
        # config = {'output_dim': self.output_dim}
        config = {}
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class AddLayer(keras.layers.Layer):
    """Elementwise add with broadcast support.

    Native Keras only supports elementwise add w/ same input shape.
    Broadcasting is allowed in tf tensor operation.

    Attributes:
        output_dim: Dimension of the output from the layer
    """

    def __init__(self,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.output_dim = None

    def call(self, inputs):
        """Add."""
        out = tf.math.add(inputs[0], inputs[1])
        # out = inputs[0] + inputs[1]
        self.output_dim = out.get_shape().as_list()
        return out

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        # Need to return tuple. tensor.shape returns tenors not tuple
        # So if we just concat, then we get tuple of tensors
        shapes = []
        for i, sh in enumerate(self.output_dim):
            if i == 0:  # Batch dim
                shapes.append(None)
            else:
                shapes.append(sh)
        return tuple(shapes)

    def get_config(self):
        """Keras layer get config."""
        # config = {'output_dim': self.output_dim}
        config = {}
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class SubtractLayer(keras.layers.Layer):
    """Elementwise subtract with broadcast support.

    Native Keras only supports elementwise sub w/ same input shape.
    Broadcasting is allowed in tf tensor operation.

    Attributes:
        output_dim: Dimension of the output from the layer
    """

    def __init__(self,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.output_dim = None

    def call(self, inputs):
        """Subtract."""
        out = tf.math.subtract(inputs[0], inputs[1])
        # out = inputs[0] - inputs[1]
        self.output_dim = out.get_shape().as_list()
        return out

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        # Need to return tuple. tensor.shape returns tenors not tuple
        # So if we just concat, then we get tuple of tensors
        shapes = []
        for i, sh in enumerate(self.output_dim):
            if i == 0:  # Batch dim
                shapes.append(None)
            else:
                shapes.append(sh)
        return tuple(shapes)

    def get_config(self):
        """Keras layer get config."""
        # config = {'output_dim': self.output_dim}
        config = {}
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class WhereLayer(keras.layers.Layer):
    """Where layer using tf.where"""

    def call(self, inputs):
        """Where."""
        inp, then_cond, else_cond = inputs
        # inp = tf.cast(inp, tf.bool)
        out = tf.where(inp, x=then_cond, y=else_cond)
        return out

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        return input_shape

    def get_config(self):
        """Keras layer get config."""
        config = {}
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ExpandLayer(keras.layers.Layer):
    """Expand w/ broadcast enabled.

    Attributes
        shape: Input shape
    """

    def __init__(self, shape,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.shape = shape
        self.ouput_dim = None

    def call(self, inputs):
        """Expand."""
        ones = K.ones(self.shape, dtype=inputs.dtype)
        out = [inputs * ones]
        self.output_dim = ones.get_shape().as_list()
        return out

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        # Need to return tuple. tensor.shape returns tenors not tuple
        # So if we just concat, then we get tuple of tensors
        shapes = []
        for i, sh in enumerate(self.output_dim):
            if i == 0:
                shapes.append(input_shape[0])
            else:
                shapes.append(sh)
        return tuple(shapes)

    def get_config(self):
        """Keras layer get config."""
        config = {'shape': self.shape, }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class GatherLayer(keras.layers.Layer):
    """Gather from TF tensor.

    Attributes
        indices: Indices to gather on
        axis: Which axis to gather on
    """

    def __init__(self, indices, axis, **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.indices = indices
        self.axis = axis
        self.output_dim = None

    def call(self, inputs):
        """Gather."""
        # TF gather only accepts indices in range of 0 ~ shape[axis]
        # Hence, need to convert all negative indices to positve
        # https://github.com/onnx/onnx-tensorflow/blob/master/onnx_tf/handlers/backend/gather_and_scatter_mixin.py#L81
        data_shape = tf.shape(inputs, out_type=tf.int64)
        max_i = data_shape[self.axis]
        ind = self.indices + max_i
        ind = tf.math.floormod(ind, max_i)

        out = tf.gather(inputs, ind, axis=self.axis, batch_dims=0)
        self.output_dim = out.get_shape().as_list()
        return out

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        # Need to return tuple. tensor.shape returns tenors not tuple
        # So if we just concat, then we get tuple of tensors
        shapes = []
        for i, sh in enumerate(self.output_dim):
            if i == 0:
                shapes.append(input_shape[0])
            else:
                shapes.append(sh)
        return tuple(shapes)

    def get_config(self):
        """Keras layer get config."""
        config = {'indices': self.indices, 'axis': self.axis}
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ReshapeLayer(keras.layers.Layer):
    """Reshape using Keras backend.

    Default Reshape Layer expects batch dimension.

    Attributes:
        shape: Target shape
    """

    def __init__(self, shape,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.shape = shape

    def call(self, inputs):
        """Reshape."""
        return K.reshape(inputs, self.shape)

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        return self.shape

    def get_config(self):
        """Keras layer get config."""
        config = {'shape': self.shape, }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ZeroPadding1D_NCW(keras.layers.convolutional._ZeroPadding):
    """Zero-padding layer for 1D input (e.g. temporal sequence).

    Default ZeroPadding1D only accepts `channels_last`.

    # Arguments
        padding: int, or tuple of int (length 2), or dictionary.
            - If int:
            How many zeros to add at the beginning and end of
            the padding dimension (axis 1).
            - If tuple of int (length 2):
            How many zeros to add at the beginning and at the end of
            the padding dimension (`(left_pad, right_pad)`).

    # Input shape
        3D tensor with shape `(batch, axis_to_pad, features)`

    # Output shape
        3D tensor with shape `(batch, padded_axis, features)`
    """

    def __init__(self, padding=1, **kwargs):
        """Init."""
        normalized_padding = (conv_utils.normalize_tuple(padding, 2, 'padding'),)
        super().__init__(normalized_padding, 'channels_first', **kwargs)

    def call(self, inputs):
        """Zero Pad."""
        pattern = [[0, 0], [0, 0], [self.padding[0][0], self.padding[0][1]]]
        return tf.pad(inputs, pattern)

    def get_config(self):
        """Keras layer get config."""
        config = super().get_config()
        config['padding'] = config['padding'][0]
        config.pop('data_format')
        return config


class GroupConv(keras.layers.Layer):
    """Abstract nD convolution layer (private, used as implementation base).

    This layer creates a convolution kernel that is convolved
    with the layer input to produce a tensor of outputs.
    If `use_bias` is True, a bias vector is created and added to the outputs.
    Finally, if `activation` is not `None`,
    it is applied to the outputs as well.

    Attributes
        rank: An integer, the rank of the convolution,
            e.g. "2" for 2D convolution.
        filters: Integer, the dimensionality of the output space
            (i.e. the number of output filters in the convolution).
        kernel_size: An integer or tuple/list of n integers, specifying the
            dimensions of the convolution window.
        strides: An integer or tuple/list of n integers,
            specifying the strides of the convolution.
            Specifying any stride value != 1 is incompatible with specifying
            any `dilation_rate` value != 1.
        padding: One of `"valid"` or `"same"` (case-insensitive).
        data_format: A string,
            one of `"channels_last"` or `"channels_first"`.
            The ordering of the dimensions in the inputs.
            `"channels_last"` corresponds to inputs with shape
            `(batch, ..., channels)` while `"channels_first"` corresponds to
            inputs with shape `(batch, channels, ...)`.
            It defaults to the `image_data_format` value found in your
            Keras config file at `~/.keras/keras.json`.
            If you never set it, then it will be "channels_last".
        dilation_rate: An integer or tuple/list of n integers, specifying
            the dilation rate to use for dilated convolution.
            Currently, specifying any `dilation_rate` value != 1 is
            incompatible with specifying any `strides` value != 1.
        groups: A positive integer specifying the number of groups in which the
            input is split along the channel axis. Each group is convolved
            separately with `filters / groups` filters. The output is the
            concatenation of all the `groups` results along the channel axis.
            Input channels and `filters` must both be divisible by `groups`.
        activation: Activation function to use
            (see [activations](../activations.md)).
            If you don't specify anything, no activation is applied
            (ie. "linear" activation: `a(x) = x`).
        use_bias: Boolean, whether the layer uses a bias vector.
        kernel_initializer: Initializer for the `kernel` weights matrix
            (see [initializers](../initializers.md)).
        bias_initializer: Initializer for the bias vector
            (see [initializers](../initializers.md)).
        kernel_regularizer: Regularizer function applied to
            the `kernel` weights matrix
            (see [regularizer](../regularizers.md)).
        bias_regularizer: Regularizer function applied to the bias vector
            (see [regularizer](../regularizers.md)).
        activity_regularizer: Regularizer function applied to
            the output of the layer (its "activation").
            (see [regularizer](../regularizers.md)).
        kernel_constraint: Constraint function applied to the kernel matrix
            (see [constraints](../constraints.md)).
        bias_constraint: Constraint function applied to the bias vector
            (see [constraints](../constraints.md)).
    """

    def __init__(self, rank,
                 filters,
                 kernel_size,
                 strides=1,
                 padding='valid',
                 data_format=None,
                 dilation_rate=1,
                 activation=None,
                 use_bias=True,
                 groups=1,
                 kernel_initializer='glorot_uniform',
                 bias_initializer='zeros',
                 kernel_regularizer=None,
                 bias_regularizer=None,
                 activity_regularizer=None,
                 kernel_constraint=None,
                 bias_constraint=None,
                 **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.rank = rank
        self.filters = filters
        self.kernel_size = conv_utils.normalize_tuple(kernel_size, rank,
                                                      'kernel_size')
        self.strides = conv_utils.normalize_tuple(strides, rank, 'strides')
        self.padding = conv_utils.normalize_padding(padding)
        self.data_format = K.normalize_data_format(data_format)
        self.dilation_rate = conv_utils.normalize_tuple(dilation_rate, rank,
                                                        'dilation_rate')
        self.groups = groups or 1
        self.activation = keras.activations.get(activation)
        self.use_bias = use_bias
        self.kernel_initializer = keras.initializers.get(kernel_initializer)
        self.bias_initializer = keras.initializers.get(bias_initializer)
        self.kernel_regularizer = keras.regularizers.get(kernel_regularizer)
        self.bias_regularizer = keras.regularizers.get(bias_regularizer)
        self.activity_regularizer = keras.regularizers.get(activity_regularizer)
        self.kernel_constraint = keras.constraints.get(kernel_constraint)
        self.bias_constraint = keras.constraints.get(bias_constraint)
        self.input_spec = InputSpec(ndim=self.rank + 2)

    def build(self, input_shape):
        """Build."""
        if self.data_format == 'channels_first':
            channel_axis = 1
        else:
            channel_axis = -1
        if input_shape[channel_axis] is None:
            raise ValueError('The channel dimension of the inputs '
                             'should be defined. Found `None`.')
        input_dim = input_shape[channel_axis]
        if input_dim % self.groups != 0:
            raise ValueError(
                f'The number of input channels must be evenly divisible by the number '
                f'of groups. Received groups={self.groups}, but the input has {input_dim} channels '
                f'(full input shape is {input_shape}).')

        kernel_shape = self.kernel_size + (input_dim // self.groups,
                                           self.filters)

        self.kernel = self.add_weight(shape=kernel_shape,
                                      initializer=self.kernel_initializer,
                                      name='kernel',
                                      regularizer=self.kernel_regularizer,
                                      constraint=self.kernel_constraint)
        if self.use_bias:
            self.bias = self.add_weight(shape=(self.filters,),
                                        initializer=self.bias_initializer,
                                        name='bias',
                                        regularizer=self.bias_regularizer,
                                        constraint=self.bias_constraint)
        else:
            self.bias = None
        # Set input spec.
        self.input_spec = InputSpec(ndim=self.rank + 2,
                                    axes={channel_axis: input_dim})
        self.built = True

    def call(self, inputs):
        """GroupConv."""
        if self.rank == 1:
            outputs = K.conv1d(
                inputs,
                self.kernel,
                strides=self.strides[0],
                padding=self.padding,
                data_format=self.data_format,
                dilation_rate=self.dilation_rate[0])
        if self.rank == 2:
            outputs = K.conv2d(
                inputs,
                self.kernel,
                strides=self.strides,
                padding=self.padding,
                data_format=self.data_format,
                dilation_rate=self.dilation_rate)
        if self.rank == 3:
            outputs = K.conv3d(
                inputs,
                self.kernel,
                strides=self.strides,
                padding=self.padding,
                data_format=self.data_format,
                dilation_rate=self.dilation_rate)

        if self.use_bias:
            outputs = K.bias_add(
                outputs,
                self.bias,
                data_format=self.data_format)

        if self.activation is not None:
            return self.activation(outputs)
        return outputs

    def compute_output_shape(self, input_shape):
        """Computes output shape."""
        if self.data_format == 'channels_last':
            space = input_shape[1:-1]
        elif self.data_format == 'channels_first':
            space = input_shape[2:]
        new_space = []
        for i in range(len(space)):
            new_dim = conv_utils.conv_output_length(
                space[i],
                self.kernel_size[i],
                padding=self.padding,
                stride=self.strides[i],
                dilation=self.dilation_rate[i])
            new_space.append(new_dim)
        if self.data_format == 'channels_last':
            return (input_shape[0],) + tuple(new_space) + (self.filters,)
        return (input_shape[0], self.filters) + tuple(new_space)

    def get_config(self):
        """Keras layer get config."""
        config = {
            'rank': self.rank,
            'filters': self.filters,
            'kernel_size': self.kernel_size,
            'strides': self.strides,
            'padding': self.padding,
            'data_format': self.data_format,
            'dilation_rate': self.dilation_rate,
            'activation': keras.activations.serialize(self.activation),
            'use_bias': self.use_bias,
            'groups': self.groups,
            'kernel_initializer': keras.initializers.serialize(self.kernel_initializer),
            'bias_initializer': keras.initializers.serialize(self.bias_initializer),
            'kernel_regularizer': keras.regularizers.serialize(self.kernel_regularizer),
            'bias_regularizer': keras.regularizers.serialize(self.bias_regularizer),
            'activity_regularizer':
                keras.regularizers.serialize(self.activity_regularizer),
            'kernel_constraint': keras.constraints.serialize(self.kernel_constraint),
            'bias_constraint': keras.constraints.serialize(self.bias_constraint)
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))


CUSTOM_OBJS = {
    "SliceLayer": SliceLayer,
    'InstanceNormalization': InstanceNormalization,
    "ImageResizeLayer": ImageResizeLayer,
    "EqualLayer": EqualLayer,
    "MultiplyLayer": MultiplyLayer,
    "DivideLayer": DivideLayer,
    "AddLayer": AddLayer,
    "SubtractLayer": SubtractLayer,
    "WhereLayer": WhereLayer,
    "ExpandLayer": ExpandLayer,
    "GatherLayer": GatherLayer,
    "ReshapeLayer": ReshapeLayer,
    "ZeroPadding1D_NCW": ZeroPadding1D_NCW,
    "GroupConv": GroupConv
}
