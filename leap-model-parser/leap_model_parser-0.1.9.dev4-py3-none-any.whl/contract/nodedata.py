from dataclasses import dataclass
from typing import Union
from enum import Enum
from typing import List


class ActivationsEnum(Enum):
    relu = "relu"
    softmax = "softmax"
    selu = "selu"
    softplus = "softplus"
    softsign = "softsign"
    tanh = "tanh"
    sigmoid = "sigmoid"
    hard_sigmoid = "hard_sigmoid"
    exponential = "exponential"
    linear = "linear"
    elu = "elu"
    swish = "swish"


class PaddingEnum(Enum):
    valid = "valid"
    same = "same"


class InitializersEnum(Enum):
    glorot_uniform = "glorot_uniform"
    glorot_normal = "glorot_normal"
    lecun_uniform = "lecun_uniform"
    he_normal = "he_normal"
    lecun_normal = "lecun_normal"
    he_uniform = "he_uniform"
    Identity = "Identity"
    Orthogonal = "Orthogonal"
    Zeros = "Zeros"
    Ones = "Ones"
    RandomNormal = "RandomNormal"
    RandomUniform = "RandomUniform"


class RegularizerEnum(Enum):
    L1 = "L1"
    L1L2 = "L1L2"
    L2 = "L2"


class ConstraintEnum(Enum):
    MaxNorm = "MaxNorm"
    MinMaxNorm = "MinMaxNorm"
    NonNeg = "NonNeg"
    RadialConstraint = "RadialConstraint"
    UnitNorm = "UnitNorm"


class InitializerEnum(Enum):
    glorot_uniform = "glorot_uniform"
    glorot_normal = "glorot_normal"
    lecun_uniform = "lecun_uniform"
    he_normal = "he_normal"
    lecun_normal = "lecun_normal"
    he_uniform = "he_uniform"
    Identity = "Identity"
    Orthogonal = "Orthogonal"
    Zeros = "Zeros"
    Ones = "Ones"
    RandomNormal = "RandomNormal"
    RandomUniform = "RandomUniform"


class NodeType(Enum):
    Activation = "Activation"
    ActivityRegularization = "ActivityRegularization"
    Add = "Add"
    AdditiveAttention = "AdditiveAttention"
    AlphaDropout = "AlphaDropout"
    Average = "Average"
    AveragePooling1D = "AveragePooling1D"
    AveragePooling2D = "AveragePooling2D"
    AveragePooling3D = "AveragePooling3D"
    BatchNormalization = "BatchNormalization"
    Bidirectional = "Bidirectional"
    CategoryEncoding = "CategoryEncoding"
    CenterCrop = "CenterCrop"
    Concatenate = "Concatenate"
    Conv1D = "Conv1D"
    Conv1DTranspose = "Conv1DTranspose"
    Conv2D = "Conv2D"
    Conv2DTranspose = "Conv2DTranspose"
    Conv3D = "Conv3D"
    Conv3DTranspose = "Conv3DTranspose"
    ConvLSTM1D = "ConvLSTM1D"
    ConvLSTM2D = "ConvLSTM2D"
    ConvLSTM3D = "ConvLSTM3D"
    Cropping1D = "Cropping1D"
    Cropping2D = "Cropping2D"
    Cropping3D = "Cropping3D"
    CuDNNGRU = "CuDNNGRU"
    CuDNNLSTM = "CuDNNLSTM"
    Dense = "Dense"
    DepthwiseConv1D = "DepthwiseConv1D"
    DepthwiseConv2D = "DepthwiseConv2D"
    Discretization = "Discretization"
    Dot = "Dot"
    Dropout = "Dropout"
    ELU = "ELU"
    Embedding = "Embedding"
    Flatten = "Flatten"
    GRU = "GRU"
    GRUCell = "GRUCell"
    GRUCellV1 = "GRUCellV1"
    GRUCellV2 = "GRUCellV2"
    GRUV1 = "GRUV1"
    GRUV2 = "GRUV2"
    GaussianDropout = "GaussianDropout"
    GaussianNoise = "GaussianNoise"
    GlobalAveragePooling1D = "GlobalAveragePooling1D"
    GlobalAveragePooling2D = "GlobalAveragePooling2D"
    GlobalAveragePooling3D = "GlobalAveragePooling3D"
    GlobalMaxPooling1D = "GlobalMaxPooling1D"
    GlobalMaxPooling2D = "GlobalMaxPooling2D"
    GlobalMaxPooling3D = "GlobalMaxPooling3D"
    IntegerLookup = "IntegerLookup"
    LSTM = "LSTM"
    LSTMCell = "LSTMCell"
    LSTMCellV1 = "LSTMCellV1"
    LSTMCellV2 = "LSTMCellV2"
    LSTMV1 = "LSTMV1"
    LSTMV2 = "LSTMV2"
    LayerNormalization = "LayerNormalization"
    LeakyReLU = "LeakyReLU"
    Masking = "Masking"
    MaxPooling1D = "MaxPooling1D"
    MaxPooling2D = "MaxPooling2D"
    MaxPooling3D = "MaxPooling3D"
    Maximum = "Maximum"
    Minimum = "Minimum"
    MultiHeadAttention = "MultiHeadAttention"
    Multiply = "Multiply"
    Normalization = "Normalization"
    PReLU = "PReLU"
    Permute = "Permute"
    RandomContrast = "RandomContrast"
    RandomCrop = "RandomCrop"
    RandomFlip = "RandomFlip"
    RandomFourierFeatures = "RandomFourierFeatures"
    RandomHeight = "RandomHeight"
    RandomRotation = "RandomRotation"
    RandomTranslation = "RandomTranslation"
    RandomWidth = "RandomWidth"
    RandomZoom = "RandomZoom"
    ReLU = "ReLU"
    RepeatVector = "RepeatVector"
    Reshape = "Reshape"
    Resizing = "Resizing"
    SeparableConv1D = "SeparableConv1D"
    SeparableConv2D = "SeparableConv2D"
    SimpleRNN = "SimpleRNN"
    SimpleRNNCell = "SimpleRNNCell"
    Softmax = "Softmax"
    SpatialDropout1D = "SpatialDropout1D"
    SpatialDropout2D = "SpatialDropout2D"
    SpatialDropout3D = "SpatialDropout3D"
    StringLookup = "StringLookup"
    Subtract = "Subtract"
    SyncBatchNormalization = "SyncBatchNormalization"
    TextVectorization = "TextVectorization"
    ThresholdedReLU = "ThresholdedReLU"
    TimeDistributed = "TimeDistributed"
    UpSampling1D = "UpSampling1D"
    UpSampling2D = "UpSampling2D"
    UpSampling3D = "UpSampling3D"
    ZeroPadding1D = "ZeroPadding1D"
    ZeroPadding2D = "ZeroPadding2D"
    ZeroPadding3D = "ZeroPadding3D"
    BinaryCrossentropy = "BinaryCrossentropy"
    BinaryFocalCrossentropy = "BinaryFocalCrossentropy"
    CategoricalCrossentropy = "CategoricalCrossentropy"
    CategoricalHinge = "CategoricalHinge"
    CosineSimilarity = "CosineSimilarity"
    Hinge = "Hinge"
    Huber = "Huber"
    KLDivergence = "KLDivergence"
    LogCosh = "LogCosh"
    MeanAbsoluteError = "MeanAbsoluteError"
    MeanAbsolutePercentageError = "MeanAbsolutePercentageError"
    MeanSquaredError = "MeanSquaredError"
    MeanSquaredLogarithmicError = "MeanSquaredLogarithmicError"
    Poisson = "Poisson"
    SquaredHinge = "SquaredHinge"
    Adadelta = "Adadelta"
    Adagrad = "Adagrad"
    Adam = "Adam"
    Adamax = "Adamax"
    Ftrl = "Ftrl"
    Nadam = "Nadam"
    RMSprop = "RMSprop"
    SGD = "SGD"
    OnnxHardSigmoid = "OnnxHardSigmoid"
    Dataset = "Dataset"
    RepresentationBlock = "RepresentationBlock"
    GroundTruth = "GroundTruth"
    CustomLoss = "CustomLoss"
    Visualizer = "Visualizer"
    Lambda = "Lambda"
    Repeat = "Repeat"
    Variable = "Variable"
    Gather = "Gather"


@dataclass
class Activation:
    activation: ActivationsEnum
    type: NodeType


@dataclass
class ActivityRegularization:
    l1: float
    l2: float
    type: NodeType


@dataclass
class Add:
    type: NodeType


@dataclass
class AdditiveAttention:
    use_scale: bool
    type: NodeType


@dataclass
class AlphaDropout:
    rate: float
    noise_shape: List[int]
    seed: List[int]
    type: NodeType


@dataclass
class Average:
    type: NodeType


@dataclass
class AveragePooling1D:
    pool_size: int
    strides: int
    padding: PaddingEnum
    type: NodeType


@dataclass
class AveragePooling2D:
    pool_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    type: NodeType


@dataclass
class AveragePooling3D:
    pool_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    type: NodeType


@dataclass
class BatchNormalization:
    axis: int
    momentum: float
    epsilon: float
    center: bool
    scale: bool
    beta_initializer: InitializersEnum
    gamma_initializer: InitializersEnum
    moving_mean_initializer: InitializersEnum
    moving_variance_initializer: InitializersEnum
    beta_regularizer: RegularizerEnum
    gamma_regularizer: RegularizerEnum
    beta_constraint: ConstraintEnum
    gamma_constraint: ConstraintEnum
    type: NodeType


@dataclass
class Bidirectional:
    merge_mode: str
    weights: List[int]
    backward_layer: List[int]
    type: NodeType


@dataclass
class CategoryEncoding:
    num_tokens: List[int]
    output_mode: str
    sparse: bool
    type: NodeType


@dataclass
class CenterCrop:
    height: int
    width: int
    type: NodeType


@dataclass
class Concatenate:
    axis: int
    type: NodeType


@dataclass
class Conv1D:
    filters: int
    kernel_size: List[int]
    strides: int
    padding: PaddingEnum
    dilation_rate: int
    groups: int
    activation: ActivationsEnum
    use_bias: bool
    kernel_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class Conv1DTranspose:
    filters: int
    kernel_size: int
    strides: int
    padding: PaddingEnum
    output_padding: int
    dilation_rate: int
    activation: ActivationsEnum
    use_bias: bool
    kernel_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class Conv2D:
    filters: int
    kernel_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    dilation_rate: List[int]
    groups: int
    activation: ActivationsEnum
    use_bias: bool
    kernel_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class Conv2DTranspose:
    filters: int
    kernel_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    output_padding: List[int]
    dilation_rate: List[int]
    activation: ActivationsEnum
    use_bias: bool
    kernel_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class Conv3D:
    filters: int
    kernel_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    dilation_rate: List[int]
    groups: int
    activation: ActivationsEnum
    use_bias: bool
    kernel_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class Conv3DTranspose:
    filters: int
    kernel_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    output_padding: List[int]
    dilation_rate: List[int]
    activation: ActivationsEnum
    use_bias: bool
    kernel_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class ConvLSTM1D:
    filters: int
    kernel_size: List[int]
    strides: int
    padding: PaddingEnum
    dilation_rate: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    dropout: float
    recurrent_dropout: float
    type: NodeType


@dataclass
class ConvLSTM2D:
    filters: int
    kernel_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    dilation_rate: List[int]
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    dropout: float
    recurrent_dropout: float
    type: NodeType


@dataclass
class ConvLSTM3D:
    filters: int
    kernel_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    dilation_rate: List[int]
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    dropout: float
    recurrent_dropout: float
    type: NodeType


@dataclass
class Cropping1D:
    cropping: List[int]
    type: NodeType


@dataclass
class Cropping2D:
    cropping: List[int]
    type: NodeType


@dataclass
class Cropping3D:
    cropping: List[int]
    type: NodeType


@dataclass
class CuDNNGRU:
    units: int
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    type: NodeType


@dataclass
class CuDNNLSTM:
    units: int
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    type: NodeType


@dataclass
class Dense:
    units: int
    activation: ActivationsEnum
    use_bias: bool
    kernel_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class DepthwiseConv1D:
    kernel_size: int
    strides: int
    padding: PaddingEnum
    depth_multiplier: int
    dilation_rate: int
    activation: ActivationsEnum
    use_bias: bool
    depthwise_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    depthwise_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    depthwise_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class DepthwiseConv2D:
    kernel_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    depth_multiplier: int
    dilation_rate: List[int]
    activation: ActivationsEnum
    use_bias: bool
    depthwise_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    depthwise_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    depthwise_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class Discretization:
    bin_boundaries: List[int]
    num_bins: List[int]
    epsilon: float
    output_mode: str
    sparse: bool
    type: NodeType


@dataclass
class Dot:
    axes: List[int]
    normalize: bool
    type: NodeType


@dataclass
class Dropout:
    rate: float
    noise_shape: List[int]
    seed: List[int]
    type: NodeType


@dataclass
class ELU:
    alpha: float
    type: NodeType


@dataclass
class Embedding:
    input_dim: int
    output_dim: int
    embeddings_initializer: str
    embeddings_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    embeddings_constraint: ConstraintEnum
    mask_zero: bool
    input_length: List[int]
    type: NodeType


@dataclass
class Flatten:
    type: NodeType


@dataclass
class GRU:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    unroll: bool
    time_major: bool
    reset_after: bool
    type: NodeType


@dataclass
class GRUCell:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    reset_after: bool
    type: NodeType


@dataclass
class GRUCellV1:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    reset_after: bool
    type: NodeType


@dataclass
class GRUCellV2:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    reset_after: bool
    type: NodeType


@dataclass
class GRUV1:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    unroll: bool
    reset_after: bool
    type: NodeType


@dataclass
class GRUV2:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    unroll: bool
    time_major: bool
    reset_after: bool
    type: NodeType


@dataclass
class GaussianDropout:
    rate: float
    seed: List[int]
    type: NodeType


@dataclass
class GaussianNoise:
    stddev: str
    seed: List[int]
    type: NodeType


@dataclass
class GlobalAveragePooling1D:
    type: NodeType


@dataclass
class GlobalAveragePooling2D:
    keepdims: bool
    type: NodeType


@dataclass
class GlobalAveragePooling3D:
    keepdims: bool
    type: NodeType


@dataclass
class GlobalMaxPooling1D:
    keepdims: bool
    type: NodeType


@dataclass
class GlobalMaxPooling2D:
    keepdims: bool
    type: NodeType


@dataclass
class GlobalMaxPooling3D:
    keepdims: bool
    type: NodeType


@dataclass
class IntegerLookup:
    max_tokens: List[int]
    num_oov_indices: int
    mask_token: List[int]
    oov_token: int
    vocabulary: List[int]
    vocabulary_dtype: str
    idf_weights: List[int]
    invert: bool
    output_mode: str
    sparse: bool
    pad_to_max_tokens: bool
    type: NodeType


@dataclass
class LSTM:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    time_major: bool
    unroll: bool
    type: NodeType


@dataclass
class LSTMCell:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    type: NodeType


@dataclass
class LSTMCellV1:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    type: NodeType


@dataclass
class LSTMCellV2:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    type: NodeType


@dataclass
class LSTMV1:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    unroll: bool
    type: NodeType


@dataclass
class LSTMV2:
    units: int
    activation: ActivationsEnum
    recurrent_activation: str
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    unit_forget_bias: bool
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    time_major: bool
    unroll: bool
    type: NodeType


@dataclass
class LayerNormalization:
    axis: int
    epsilon: float
    center: bool
    scale: bool
    beta_initializer: InitializersEnum
    gamma_initializer: InitializersEnum
    beta_regularizer: RegularizerEnum
    gamma_regularizer: RegularizerEnum
    beta_constraint: ConstraintEnum
    gamma_constraint: ConstraintEnum
    type: NodeType


@dataclass
class LeakyReLU:
    alpha: float
    type: NodeType


@dataclass
class Masking:
    mask_value: float
    type: NodeType


@dataclass
class MaxPooling1D:
    pool_size: int
    strides: int
    padding: PaddingEnum
    type: NodeType


@dataclass
class MaxPooling2D:
    pool_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    type: NodeType


@dataclass
class MaxPooling3D:
    pool_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    type: NodeType


@dataclass
class Maximum:
    type: NodeType


@dataclass
class Minimum:
    type: NodeType


@dataclass
class MultiHeadAttention:
    num_heads: int
    key_dim: int
    value_dim: List[int]
    dropout: float
    use_bias: bool
    output_shape: List[int]
    attention_axes: List[int]
    kernel_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class Multiply:
    type: NodeType


@dataclass
class Normalization:
    axis: int
    mean: List[int]
    variance: List[int]
    type: NodeType


@dataclass
class PReLU:
    alpha_initializer: InitializersEnum
    alpha_regularizer: RegularizerEnum
    alpha_constraint: ConstraintEnum
    shared_axes: List[int]
    type: NodeType


@dataclass
class Permute:
    dims: List[int]
    type: NodeType


@dataclass
class RandomContrast:
    factor: List[int]
    seed: List[int]
    type: NodeType


@dataclass
class RandomCrop:
    height: int
    width: int
    seed: List[int]
    type: NodeType


@dataclass
class RandomFlip:
    mode: str
    seed: List[int]
    type: NodeType


@dataclass
class RandomFourierFeatures:
    output_dim: int
    kernel_initializer: InitializersEnum
    scale: List[int]
    trainable: bool
    type: NodeType


@dataclass
class RandomHeight:
    factor: List[int]
    interpolation: str
    seed: List[int]
    type: NodeType


@dataclass
class RandomRotation:
    factor: List[int]
    fill_mode: str
    interpolation: str
    seed: List[int]
    fill_value: float
    type: NodeType


@dataclass
class RandomTranslation:
    height_factor: List[int]
    width_factor: List[int]
    fill_mode: str
    interpolation: str
    seed: List[int]
    fill_value: float
    type: NodeType


@dataclass
class RandomWidth:
    factor: List[int]
    interpolation: str
    seed: List[int]
    type: NodeType


@dataclass
class RandomZoom:
    height_factor: List[int]
    width_factor: List[int]
    fill_mode: str
    interpolation: str
    seed: List[int]
    fill_value: float
    type: NodeType


@dataclass
class ReLU:
    max_value: List[int]
    negative_slope: float
    threshold: float
    type: NodeType


@dataclass
class RepeatVector:
    n: int
    type: NodeType


@dataclass
class Reshape:
    target_shape: List[int]
    type: NodeType


@dataclass
class Resizing:
    height: int
    width: int
    interpolation: str
    crop_to_aspect_ratio: bool
    type: NodeType


@dataclass
class SeparableConv1D:
    filters: int
    kernel_size: int
    strides: int
    padding: PaddingEnum
    dilation_rate: int
    depth_multiplier: int
    activation: ActivationsEnum
    use_bias: bool
    depthwise_initializer: InitializersEnum
    pointwise_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    depthwise_regularizer: RegularizerEnum
    pointwise_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    depthwise_constraint: ConstraintEnum
    pointwise_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class SeparableConv2D:
    filters: int
    kernel_size: List[int]
    strides: List[int]
    padding: PaddingEnum
    dilation_rate: List[int]
    depth_multiplier: int
    activation: ActivationsEnum
    use_bias: bool
    depthwise_initializer: InitializersEnum
    pointwise_initializer: InitializersEnum
    bias_initializer: InitializersEnum
    depthwise_regularizer: RegularizerEnum
    pointwise_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    depthwise_constraint: ConstraintEnum
    pointwise_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    type: NodeType


@dataclass
class SimpleRNN:
    units: int
    activation: ActivationsEnum
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    activity_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    return_sequences: bool
    return_state: bool
    go_backwards: bool
    stateful: bool
    unroll: bool
    type: NodeType


@dataclass
class SimpleRNNCell:
    units: int
    activation: ActivationsEnum
    use_bias: bool
    kernel_initializer: InitializersEnum
    recurrent_initializer: str
    bias_initializer: InitializersEnum
    kernel_regularizer: RegularizerEnum
    recurrent_regularizer: RegularizerEnum
    bias_regularizer: RegularizerEnum
    kernel_constraint: ConstraintEnum
    recurrent_constraint: ConstraintEnum
    bias_constraint: ConstraintEnum
    dropout: float
    recurrent_dropout: float
    type: NodeType


@dataclass
class Softmax:
    axis: int
    type: NodeType


@dataclass
class SpatialDropout1D:
    rate: float
    type: NodeType


@dataclass
class SpatialDropout2D:
    rate: float
    type: NodeType


@dataclass
class SpatialDropout3D:
    rate: float
    type: NodeType


@dataclass
class StringLookup:
    max_tokens: List[int]
    num_oov_indices: int
    mask_token: List[int]
    oov_token: str
    vocabulary: List[int]
    idf_weights: List[int]
    encoding: List[int]
    invert: bool
    output_mode: str
    sparse: bool
    pad_to_max_tokens: bool
    type: NodeType


@dataclass
class Subtract:
    type: NodeType


@dataclass
class SyncBatchNormalization:
    axis: int
    momentum: float
    epsilon: float
    center: bool
    scale: bool
    beta_initializer: InitializersEnum
    gamma_initializer: InitializersEnum
    moving_mean_initializer: InitializersEnum
    moving_variance_initializer: InitializersEnum
    beta_regularizer: RegularizerEnum
    gamma_regularizer: RegularizerEnum
    beta_constraint: ConstraintEnum
    gamma_constraint: ConstraintEnum
    type: NodeType


@dataclass
class TextVectorization:
    max_tokens: List[int]
    standardize: str
    split: str
    ngrams: List[int]
    output_mode: str
    output_sequence_length: List[int]
    pad_to_max_tokens: bool
    vocabulary: List[int]
    idf_weights: List[int]
    sparse: bool
    ragged: bool
    type: NodeType


@dataclass
class ThresholdedReLU:
    theta: float
    type: NodeType


@dataclass
class TimeDistributed:
    type: NodeType


@dataclass
class UpSampling1D:
    size: int
    type: NodeType


@dataclass
class UpSampling2D:
    size: List[int]
    interpolation: str
    type: NodeType


@dataclass
class UpSampling3D:
    size: List[int]
    type: NodeType


@dataclass
class ZeroPadding1D:
    padding: PaddingEnum
    type: NodeType


@dataclass
class ZeroPadding2D:
    padding: List[int]
    type: NodeType


@dataclass
class ZeroPadding3D:
    padding: List[int]
    type: NodeType


@dataclass
class BinaryCrossentropy:
    from_logits: bool
    label_smoothing: float
    axis: int
    type: NodeType


@dataclass
class BinaryFocalCrossentropy:
    gamma: float
    from_logits: bool
    label_smoothing: float
    axis: int
    type: NodeType


@dataclass
class CategoricalCrossentropy:
    from_logits: bool
    label_smoothing: float
    axis: int
    type: NodeType


@dataclass
class CategoricalHinge:
    type: NodeType


@dataclass
class CosineSimilarity:
    axis: int
    type: NodeType


@dataclass
class Hinge:
    type: NodeType


@dataclass
class Huber:
    delta: float
    type: NodeType


@dataclass
class KLDivergence:
    type: NodeType


@dataclass
class LogCosh:
    type: NodeType


@dataclass
class MeanAbsoluteError:
    type: NodeType


@dataclass
class MeanAbsolutePercentageError:
    type: NodeType


@dataclass
class MeanSquaredError:
    type: NodeType


@dataclass
class MeanSquaredLogarithmicError:
    type: NodeType


@dataclass
class Poisson:
    type: NodeType


@dataclass
class SquaredHinge:
    type: NodeType


@dataclass
class Adadelta:
    learning_rate: float
    rho: float
    epsilon: float
    type: NodeType


@dataclass
class Adagrad:
    learning_rate: float
    initial_accumulator_value: float
    epsilon: float
    type: NodeType


@dataclass
class Adam:
    learning_rate: float
    beta_1: float
    beta_2: float
    epsilon: float
    amsgrad: bool
    type: NodeType


@dataclass
class Adamax:
    learning_rate: float
    beta_1: float
    beta_2: float
    epsilon: float
    type: NodeType


@dataclass
class Ftrl:
    learning_rate: float
    learning_rate_power: float
    initial_accumulator_value: float
    l1_regularization_strength: float
    l2_regularization_strength: float
    l2_shrinkage_regularization_strength: float
    beta: float
    type: NodeType


@dataclass
class Nadam:
    learning_rate: float
    beta_1: float
    beta_2: float
    epsilon: float
    type: NodeType


@dataclass
class RMSprop:
    learning_rate: float
    rho: float
    momentum: float
    epsilon: float
    centered: bool
    type: NodeType


@dataclass
class SGD:
    learning_rate: float
    momentum: float
    nesterov: bool
    type: NodeType


@dataclass
class OnnxHardSigmoid:
    alpha: float
    beta: float
    type: NodeType


@dataclass
class Dataset:
    type: NodeType


@dataclass
class RepresentationBlock:
    type: NodeType


@dataclass
class GroundTruth:
    type: NodeType


@dataclass
class CustomLoss:
    type: NodeType


@dataclass
class Visualizer:
    type: NodeType


@dataclass
class Lambda:
    type: NodeType


@dataclass
class Repeat:
    repeats: List[int]
    axis: int
    type: NodeType


@dataclass
class Variable:
    var_shape: List[int]
    initializer: InitializerEnum
    type: NodeType


@dataclass
class Gather:
    indices: List[int]
    axis: int
    type: NodeType


@dataclass
class NodeDataTypes:
    props: Union[Activation, ActivityRegularization, Add, AdditiveAttention, AlphaDropout, Average, AveragePooling1D, 
                 AveragePooling2D, AveragePooling3D, BatchNormalization, Bidirectional, CategoryEncoding, CenterCrop, 
                 Concatenate, Conv1D, Conv1DTranspose, Conv2D, Conv2DTranspose, Conv3D, Conv3DTranspose, ConvLSTM1D, 
                 ConvLSTM2D, ConvLSTM3D, Cropping1D, Cropping2D, Cropping3D, CuDNNGRU, CuDNNLSTM, Dense, 
                 DepthwiseConv1D, DepthwiseConv2D, Discretization, Dot, Dropout, ELU, Embedding, Flatten, GRU, GRUCell, 
                 GRUCellV1, GRUCellV2, GRUV1, GRUV2, GaussianDropout, GaussianNoise, GlobalAveragePooling1D, 
                 GlobalAveragePooling2D, GlobalAveragePooling3D, GlobalMaxPooling1D, GlobalMaxPooling2D, 
                 GlobalMaxPooling3D, IntegerLookup, LSTM, LSTMCell, LSTMCellV1, LSTMCellV2, LSTMV1, LSTMV2, 
                 LayerNormalization, LeakyReLU, Masking, MaxPooling1D, MaxPooling2D, MaxPooling3D, Maximum, Minimum, 
                 MultiHeadAttention, Multiply, Normalization, PReLU, Permute, RandomContrast, RandomCrop, RandomFlip, 
                 RandomFourierFeatures, RandomHeight, RandomRotation, RandomTranslation, RandomWidth, RandomZoom, ReLU, 
                 RepeatVector, Reshape, Resizing, SeparableConv1D, SeparableConv2D, SimpleRNN, SimpleRNNCell, Softmax, 
                 SpatialDropout1D, SpatialDropout2D, SpatialDropout3D, StringLookup, Subtract, SyncBatchNormalization, 
                 TextVectorization, ThresholdedReLU, TimeDistributed, UpSampling1D, UpSampling2D, UpSampling3D, 
                 ZeroPadding1D, ZeroPadding2D, ZeroPadding3D, BinaryCrossentropy, BinaryFocalCrossentropy, 
                 CategoricalCrossentropy, CategoricalHinge, CosineSimilarity, Hinge, Huber, KLDivergence, LogCosh, 
                 MeanAbsoluteError, MeanAbsolutePercentageError, MeanSquaredError, MeanSquaredLogarithmicError, Poisson, 
                 SquaredHinge, Adadelta, Adagrad, Adam, Adamax, Ftrl, Nadam, RMSprop, SGD, OnnxHardSigmoid, Dataset, 
                 RepresentationBlock, GroundTruth, CustomLoss, Visualizer, Lambda, Repeat, Variable, Gather]
