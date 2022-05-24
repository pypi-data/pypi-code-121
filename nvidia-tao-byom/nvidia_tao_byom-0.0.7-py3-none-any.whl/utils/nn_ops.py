import logging
import tensorflow as tf
from tensorflow.python.framework import tensor_shape
from tensorflow.python.ops.nn_ops import _enclosing_tpu_context, \
    _get_strides_and_dilation_rate, _WithSpaceToBatch, \
    convolution_internal, _Convolution


"""Logger for Keras tensorflow backend."""
logger = logging.getLogger(__name__)


class Convolution(object):
  """Helper class for convolution.

  Note that this class assumes that shapes of input and filter passed to
  __call__ are compatible with input_shape and filter_shape passed to the
  constructor.

  Arguments
    input_shape: static shape of input. i.e. input.get_shape().
    filter_shape: static shape of the filter. i.e. filter.get_shape().
    padding:  see convolution.
    strides: see convolution.
    dilation_rate: see convolution.
    name: see convolution.
    data_format: see convolution.
  """

  def __init__(self,
               input_shape,
               filter_shape,
               padding,
               strides=None,
               dilation_rate=None,
               name=None,
               data_format=None,
               fused=False):
    """Helper function for convolution."""
    num_total_dims = filter_shape.ndims
    if num_total_dims is None:
      num_total_dims = input_shape.ndims
    if num_total_dims is None:
      raise ValueError("rank of input or filter must be known")

    num_spatial_dims = num_total_dims - 2

    try:
      input_shape.with_rank(num_spatial_dims + 2)
    except ValueError:
      raise ValueError(
          "input tensor must have rank %d" % (num_spatial_dims + 2))

    try:
      filter_shape.with_rank(num_spatial_dims + 2)
    except ValueError:
      raise ValueError(
          "filter tensor must have rank %d" % (num_spatial_dims + 2))

    if data_format is None or not data_format.startswith("NC"):
      input_channels_dim = tensor_shape.dimension_at_index(
          input_shape, num_spatial_dims + 1)
      spatial_dims = range(1, num_spatial_dims + 1)
    else:
      input_channels_dim = tensor_shape.dimension_at_index(input_shape, 1)
      spatial_dims = range(2, num_spatial_dims + 2)

    filter_dim = tensor_shape.dimension_at_index(filter_shape, num_spatial_dims)
    if not (input_channels_dim % filter_dim).is_compatible_with(0):
      raise ValueError(
          "The number of input channels is not divisible by the corresponding "
          f"number of output filters. Received: input.shape={input_shape} with "
          f"{input_channels_dim} channels and filters.shape={filter_shape} "
          f"with {filter_dim} output filters.")


    strides, dilation_rate = _get_strides_and_dilation_rate(
        num_spatial_dims, strides, dilation_rate)

    self.input_shape = input_shape
    self.filter_shape = filter_shape
    self.data_format = data_format
    self.strides = strides
    self.padding = padding
    self.name = name
    self.dilation_rate = dilation_rate
    # We call CUDNN convolutions when dealing with convolutions with 1D/2D
    # space + dilation or convolutions with no dilation. CUDNN is not used for
    # 3D convolutions with dilation because that would result in "no algorithm
    # worked" errors from CUDNN.
    conv_dims = input_shape.ndims - 2
    build_op = (self._build_op_atrous if fused and conv_dims <= 2 else
                self._build_op_non_atrous)
    self.conv_op = _WithSpaceToBatch(
        input_shape,
        dilation_rate=dilation_rate,
        padding=padding,
        build_op=build_op,
        filter_shape=filter_shape,
        spatial_dims=spatial_dims,
        data_format=data_format,
        fused=fused)

  def _build_op_non_atrous(self, _, padding):
    return _Convolution(
        self.input_shape,
        filter_shape=self.filter_shape,
        padding=padding,
        data_format=self.data_format,
        strides=self.strides,
        name=self.name)

  def _build_op_atrous(self, _, padding):
    return _Convolution(
        self.input_shape,
        filter_shape=self.filter_shape,
        padding=padding,
        data_format=self.data_format,
        strides=self.strides,
        dilation_rate=self.dilation_rate,
        name=self.name)

  def __call__(self, inp, filter):  # pylint: disable=redefined-builtin
    # copybara:strip_begin
    # TODO(b/138808492): Remove code inside copybara
    # to make TPU code and CPU code consistent.
    # TPU convolution supports dilations greater than 1.
    if _enclosing_tpu_context() is not None:
      return convolution_internal(
          inp,
          filter,
          strides=self.strides,
          padding=self.padding,
          data_format=self.data_format,
          dilations=self.dilation_rate,
          name=self.name,
          call_from_convolution=False)
    else:
      return self.conv_op(inp, filter)
    # copybara:strip_end
    # copybara:insert return self.conv_op(inp, filter)


def _patch_tf_function(f):
    """Patch tf functionality.

    Args:
        f (func): a function with the same name as exists in the tf.
    """
    name = f.__name__
    logger.debug("Patching %s", name)
    tf.python.nn_ops.__setattr__(name, f)

def patch():
    """Apply the patches to the module."""
    _patch_tf_function(Convolution)