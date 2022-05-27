"""Neural Network classes and helper functions for PyTorch."""
from abc import ABC
import logging
from typing import Any, Iterable, List, Optional, Tuple, Type, Union, cast

import torch
import torch.nn as nn
import torchvision.models as tv_models

from bitfount.backends.pytorch.models.torch_functions.mish import Mish
from bitfount.models.nn import _ConvNeuralNet, _FeedForwardNeuralNet, _NeuralNet

logger = logging.getLogger(__name__)

TORCHVISION_CLASSIFICATION_MODELS = {
    name: func
    for name, func in vars(tv_models).items()
    if callable(func) and not isinstance(func, type)
}


class _PyTorchNeuralNet(nn.Module, _NeuralNet, ABC):
    """Base abstract class for all PyTorch-implemented neural networks."""

    pass


class _PyTorchConvNeuralNet(_PyTorchNeuralNet, _ConvNeuralNet):
    """Simple convolutional neural network architecture in PyTorch."""

    def __init__(
        self,
        layer_sizes: Iterable[Tuple[int, int]],
        dropout_probs: List[float],
        mish: bool,
        head_sizes: Iterable[Tuple[int, int]],
        ff_layer_sizes: Iterable[Tuple[int, int]],
        ff_dropout_probs: List[float],
        kernel_size: int,
        padding: int,
        stride: int,
        pooling_function: str,
    ):
        super().__init__()
        # CONVOLUTIONAL BLOCKS
        self.layers = nn.ModuleList(
            [
                nn.Conv2d(
                    in_, out_, kernel_size=kernel_size, stride=stride, padding=padding
                )
                for in_, out_ in layer_sizes
            ]
        )
        activation_function = Mish if mish else nn.ReLU
        self.activations = nn.ModuleList([activation_function() for _ in layer_sizes])
        self.batch_norms = nn.ModuleList(
            [nn.BatchNorm2d(size) for _, size in layer_sizes]
        )
        self.dropouts = nn.ModuleList([nn.Dropout2d(i) for i in dropout_probs])
        pooling_module: Union[Type[nn.AvgPool2d], Type[nn.MaxPool2d]]
        if pooling_function == "max":
            pooling_module = nn.MaxPool2d
        elif pooling_function == "avg":
            pooling_module = nn.AvgPool2d

        self.pooling_functions = nn.ModuleList(
            [pooling_module(kernel_size=2) for _ in layer_sizes]
        )

        # FEEDFORWARD LAYERS
        self.ff_layers = nn.ModuleList(
            [nn.Linear(in_, out_) for in_, out_ in ff_layer_sizes]
        )
        self.ff_activations = nn.ModuleList(
            [activation_function() for _ in ff_layer_sizes]
        )
        self.ff_batch_norms = nn.ModuleList(
            [nn.BatchNorm1d(size) for _, size in ff_layer_sizes]
        )
        self.ff_dropouts = nn.ModuleList([nn.Dropout(i) for i in ff_dropout_probs])

        # OUTPUT LAYER
        self.heads = nn.ModuleList([nn.Linear(in_, out_) for in_, out_ in head_sizes])

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        """Forward pass in model."""
        for layer, activation, batchnorm, dropout, pooling_function in zip(
            self.layers,
            self.activations,
            self.batch_norms,
            self.dropouts,
            self.pooling_functions,
        ):
            x = layer(x)
            x = activation(x)
            x = batchnorm(x)
            x = dropout(x)
            x = pooling_function(x)

        x = x.view(x.size(0), -1)

        for layer, activation, batchnorm, dropout in zip(
            self.ff_layers, self.ff_activations, self.ff_batch_norms, self.ff_dropouts
        ):
            x = layer(x)
            x = activation(x)
            x = batchnorm(x)
            x = dropout(x)

        return tuple(head(x) for head in self.heads)


class _PyTorchFeedForwardNeuralNet(_PyTorchNeuralNet, _FeedForwardNeuralNet):
    """Simple feedforward neural network architecture in PyTorch."""

    def __init__(
        self,
        embedding_sizes: Iterable[Tuple[int, int]],
        emb_dropout: float,
        n_cont: int,
        layer_sizes: Iterable[Tuple[int, int]],
        dropout_probs: List[float],
        mish: bool,
        head_sizes: Iterable[Tuple[int, int]],
    ):
        super().__init__()

        # INPUT LAYER
        self.embeddings = nn.ModuleList(
            [nn.Embedding(categories, size) for categories, size in embedding_sizes]
        )
        self.emb_drop = nn.Dropout(emb_dropout)
        self.bn_cont = nn.BatchNorm1d(n_cont)
        self.n_cont = n_cont
        # HIDDEN LAYERS
        self.layers = nn.ModuleList([nn.Linear(in_, out_) for in_, out_ in layer_sizes])
        activation_function = Mish if mish else nn.ReLU
        self.activations = nn.ModuleList([activation_function() for _ in layer_sizes])
        self.batch_norms = nn.ModuleList(
            [nn.BatchNorm1d(size) for _, size in layer_sizes]
        )
        self.dropouts = nn.ModuleList([nn.Dropout(i) for i in dropout_probs])

        # OUTPUT LAYER
        self.heads = nn.ModuleList([nn.Linear(in_, out_) for in_, out_ in head_sizes])

    def forward(self, x: Tuple[torch.Tensor, torch.Tensor]) -> Tuple[torch.Tensor, ...]:
        """Forward pass in model."""
        x_cat, x_cont = x
        if x_cont.nelement() != 0 and x_cat.nelement() != 0:
            fwd_pass_cat = [
                cast(torch.Tensor, embedding(x_cat[idx]))
                for idx, embedding in enumerate(self.embeddings)
            ]
            fwd_pass = torch.cat(fwd_pass_cat, 1)
            fwd_pass = self.emb_drop(fwd_pass)
            fwd_pass2 = self.bn_cont(x_cont)
            fwd_pass = torch.cat([fwd_pass, fwd_pass2], 1)
        elif x_cont.nelement() != 0:
            fwd_pass = self.bn_cont(x_cont)
        elif x_cat.nelement() != 0:
            fwd_pass_cat = [
                cast(torch.Tensor, embedding(x_cat[idx]))
                for idx, embedding in enumerate(self.embeddings)
            ]
            fwd_pass = torch.cat(fwd_pass_cat, 1)
            fwd_pass = self.emb_drop(fwd_pass)

        for layer, activation, batchnorm, dropout in zip(
            self.layers, self.activations, self.batch_norms, self.dropouts
        ):
            fwd_pass = layer(fwd_pass)
            fwd_pass = activation(fwd_pass)
            fwd_pass = batchnorm(fwd_pass)
            fwd_pass = dropout(fwd_pass)

        return tuple(head(fwd_pass) for head in self.heads)


class _PyTorchLogisticRegression(_PyTorchNeuralNet, _FeedForwardNeuralNet):
    def __init__(
        self,
        num_classes: int,
        input_dim: Optional[int] = None,
        num_continuous: Optional[int] = None,
        embedding_sizes: Optional[Iterable[Tuple[int, int]]] = None,
        embedding_dropout_frac: float = 0.04,
        bias: bool = True,
    ):
        """Create a new logistic regression model.

        Input size can either be specified directly (input_dim) or can be
        automatically calculated if using categorical embeddings by providing
        num_continuous and embedding_sizes.

        Args:
            num_classes: Number of classes in the target feature.
            input_dim: The size of the input vector to the model. Cannot be provided
                if num_continuous or embedding_sizes are.
            num_continuous: The number of continuous features in the input.
            embedding_sizes: The sizes of the categorical embeddings for the
                categorical features in the input.
            embedding_dropout_frac: The dropout probability to apply to categorical
                variables if using embed_categorical.
            bias: Whether the underlying linear layer should learn an additive bias.
                Default True.
        """
        super().__init__()

        # If input dimensions are specified, ignore any of the embedding settings
        if input_dim and any(i is not None for i in (num_continuous, embedding_sizes)):
            logger.warning(
                "Cannot specify both input_dim and either of num_continuous or"
                " embedding_sizes. Will default to using input_dim."
            )
            num_continuous = None
            embedding_sizes = None

        # If neither input_dim nor embedding settings are provided, throw error
        if input_dim is None and embedding_sizes is None:
            raise ValueError("One of input_dim or embedding_sizes must be provided.")

        # If embedding_sizes is provided, num_continuous must be, and vice-versa
        if (embedding_sizes is None) != (num_continuous is None):
            raise ValueError(
                "If one of embedding_sizes or num_continuous is provided, both must be"
            )

        self.num_classes = num_classes
        self.input_dim = input_dim
        self.num_continuous = num_continuous
        self.embedding_sizes = embedding_sizes
        self.embedding_dropout_frac = embedding_dropout_frac
        self.bias = bias

        # Calculate input dim if not explicitly provided
        if self.input_dim is None:
            # Above checks guarantee that if input_dim is None, these must be set
            assert self.num_continuous is not None  # nosec
            assert self.embedding_sizes is not None  # nosec
            # Input dim is equal to the number of continuous elements in the
            # input vector and the size of the embeddings for the categorical elements.
            self.input_dim = self.num_continuous + sum(
                size for _, size in self.embedding_sizes
            )

        # INPUT EMBEDDING LAYERS
        if self.embedding_sizes:
            self.category_embeddings: Optional[nn.ModuleList] = nn.ModuleList(
                [
                    nn.Embedding(categories, size)
                    for categories, size in self.embedding_sizes
                ]
            )
            self.category_embeddings_dropout: Optional[nn.Dropout] = nn.Dropout(
                self.embedding_dropout_frac
            )
        else:
            self.category_embeddings = None
            self.category_embeddings_dropout = None

        # MAIN LAYER
        self.linear = nn.Linear(
            in_features=self.input_dim, out_features=self.num_classes, bias=self.bias
        )

    def forward(self, x: Tuple[torch.Tensor, torch.Tensor]) -> torch.Tensor:
        # Split into continuous and categorical features
        x_categorical: torch.Tensor
        x_continuous: torch.Tensor
        x_categorical, x_continuous = x

        to_concat: List[torch.Tensor] = []

        # Handle categorical features, if any
        if x_categorical.nelement() != 0:
            if self.category_embeddings:
                # If category_embeddings is set, category_embeddings_dropout
                # must be too
                assert self.category_embeddings_dropout is not None  # nosec

                # Embed categorical if required
                fwd_pass_categorical = torch.cat(
                    [
                        embedding(x_categorical[idx])
                        for idx, embedding in enumerate(self.category_embeddings)
                    ],
                    dim=1,
                )
                fwd_pass_categorical = self.category_embeddings_dropout(
                    fwd_pass_categorical
                )
            else:
                # Otherwise, use as is
                fwd_pass_categorical = x_categorical

            to_concat.append(fwd_pass_categorical)

        # Add in continuous features if present
        if x_continuous.nelement() != 0:
            to_concat.append(x_continuous)

        # We return the unactivated output vector to allow it to be used
        # in various settings.
        input_vector = torch.cat(to_concat, dim=1)

        # Linear expects a FloatTensor, so if it's not (i.e. because we only have
        # non-embedded categorical features) we must treat it as such.
        if not torch.is_floating_point(input_vector):
            input_vector = input_vector.float()

        output_vector: torch.Tensor = self.linear(input_vector)
        return output_vector


def _get_torchvision_classification_model(
    model_name: str, pretrained: bool, num_classes: int, **kwargs: Any
) -> nn.Module:
    """Returns a pre-existing torchvision model.

    This function returns the torchvision classification model corresponding to
    `model_name`. Importantly, it resizes the final layer to make it appropriate
    for the task. Since this is different for every model, this must be hard-coded

    Adapted from pytorch docs/tutorials
    """
    # Convert model name for consistency
    model_name = model_name.lower()

    if "resnet" in model_name:
        model = TORCHVISION_CLASSIFICATION_MODELS[model_name](
            pretrained=pretrained, **kwargs
        )
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
    elif ("alexnet" in model_name) or ("vgg" in model_name):
        model = TORCHVISION_CLASSIFICATION_MODELS[model_name](
            pretrained=pretrained, **kwargs
        )
        num_ftrs = model.classifier[6].in_features
        model.classifier[6] = nn.Linear(num_ftrs, num_classes)
    elif "squeezenet" in model_name:
        model = TORCHVISION_CLASSIFICATION_MODELS[model_name](
            pretrained=pretrained, **kwargs
        )
        model.classifier[1] = nn.Conv2d(
            512, num_classes, kernel_size=(1, 1), stride=(1, 1)
        )
        model.num_classes = num_classes
    elif "densenet" in model_name:
        model = TORCHVISION_CLASSIFICATION_MODELS[model_name](
            pretrained=pretrained, **kwargs
        )
        num_ftrs = model.classifier.in_features
        model.classifier = nn.Linear(num_ftrs, num_classes)
    elif model_name in TORCHVISION_CLASSIFICATION_MODELS:
        raise ValueError("Model reshaping not implemented yet. Choose another model.")
    else:
        raise ValueError("Model name not recognised")

    return cast(nn.Module, model)
