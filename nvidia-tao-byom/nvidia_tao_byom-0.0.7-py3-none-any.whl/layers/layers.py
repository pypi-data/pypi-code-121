# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.
"""Node to conversion function mapping."""

from tao_byom.layers.convolution_layers import convert_conv, convert_convtranspose
from tao_byom.layers.activation_layers import convert_relu, convert_elu, convert_lrelu, convert_selu, \
    convert_sigmoid, convert_tanh, convert_softmax, convert_prelu, convert_softplus
from tao_byom.layers.operation_layers import convert_clip, convert_exp, convert_reduce_sum, convert_reduce_mean, \
    convert_log, convert_pow, convert_sqrt, convert_split, convert_cast, convert_floor, convert_identity, \
    convert_argmax, convert_reduce_l2, convert_reduce_max, convert_where
from tao_byom.layers.elementwise_layers import convert_elementwise_div, convert_elementwise_add, convert_elementwise_mul, convert_elementwise_sub, convert_max, convert_min, convert_mean, convert_elementwise_equal
from tao_byom.layers.linear_layers import convert_gemm, convert_matmul
from tao_byom.layers.reshape_layers import convert_transpose, convert_shape, convert_gather, convert_unsqueeze, \
    convert_concat, convert_reshape, convert_flatten, convert_slice, convert_squeeze, convert_expand
from tao_byom.layers.constant_layers import convert_constant, convert_constant_of_shape
from tao_byom.layers.tensor_layer import convert_range, convert_tile
from tao_byom.layers.normalization_layers import convert_batchnorm, convert_instancenorm, convert_dropout, convert_lrn
from tao_byom.layers.pooling_layers import convert_avgpool, convert_maxpool, convert_global_avg_pool
from tao_byom.layers.padding_layers import convert_padding
from tao_byom.layers.upsampling_layers import convert_upsample


AVAILABLE_CONVERTERS = {
    'Add': convert_elementwise_add,
    'ArgMax': convert_argmax,
    'AveragePool': convert_avgpool,
    'BatchNormalization': convert_batchnorm,
    'Cast': convert_cast,
    'Clip': convert_clip,
    'Concat': convert_concat,
    'Constant': convert_constant,
    'ConstantOfShape': convert_constant_of_shape,
    'Conv': convert_conv,
    'ConvTranspose': convert_convtranspose,
    'Div': convert_elementwise_div,
    'Dropout': convert_dropout,
    'Elu': convert_elu,
    'Equal': convert_elementwise_equal,
    'Exp': convert_exp,
    'Expand': convert_expand,
    'Flatten': convert_flatten,
    'Floor': convert_floor,
    'Gather': convert_gather,
    'Gemm': convert_gemm,
    'GlobalAveragePool': convert_global_avg_pool,
    'Identity': convert_identity,
    'InstanceNormalization': convert_instancenorm,
    'LeakyRelu': convert_lrelu,
    'Log': convert_log,
    'LRN': convert_lrn,
    'MatMul': convert_matmul,
    'MaxPool': convert_maxpool,
    'Max': convert_max,
    'Mean': convert_mean,
    'Min': convert_min,
    'Mul': convert_elementwise_mul,
    'PRelu': convert_prelu,
    'Pad': convert_padding,
    'Pow': convert_pow,
    'Range': convert_range,
    'ReduceL2': convert_reduce_l2,
    'ReduceMax': convert_reduce_max,
    'ReduceMean': convert_reduce_mean,
    'ReduceSum': convert_reduce_sum,
    'Relu': convert_relu,
    'Reshape': convert_reshape,
    'Resize': convert_upsample,
    'Selu': convert_selu,
    'Shape': convert_shape,
    'Sigmoid': convert_sigmoid,
    'Slice': convert_slice,
    'Softmax': convert_softmax,
    'Softplus': convert_softplus,
    'Split': convert_split,
    'Sqrt': convert_sqrt,
    'Squeeze': convert_squeeze,
    'Sub': convert_elementwise_sub,
    'Sum': convert_elementwise_add,
    'Tanh': convert_tanh,
    'Tile': convert_tile,
    'Transpose': convert_transpose,
    'Unsqueeze': convert_unsqueeze,
    'Upsample': convert_upsample,
    'Where': convert_where,
}
