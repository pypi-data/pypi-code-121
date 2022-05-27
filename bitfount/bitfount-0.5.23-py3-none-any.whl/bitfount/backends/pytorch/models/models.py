"""Model implementations using PyTorch."""
from __future__ import annotations

import logging
from typing import Any, ClassVar, List, Optional, Tuple, Union, cast

from marshmallow import fields
import pandas as pd
from pytorch_tabnet.tab_model import TabNetClassifier as TabNetClassifier_
import torch
from torch import nn as nn
from torch.nn import Module

from bitfount.backends.pytorch.data.dataloaders import (
    _BasePyTorchBitfountDataLoader,
    _PyTorchBitfountDataLoader,
)
from bitfount.backends.pytorch.models.base_models import (
    _OPTIMIZERS,
    _SCHEDULERS,
    BasePyTorchModel,
    BaseTabNetModel,
    PyTorchClassifierMixIn,
    _calculate_embedding_sizes,
)
from bitfount.backends.pytorch.models.nn import (
    _get_torchvision_classification_model,
    _PyTorchConvNeuralNet,
    _PyTorchFeedForwardNeuralNet,
    _PyTorchLogisticRegression,
)
from bitfount.backends.pytorch.types import (
    ImgAndTabDataSplit,
    ImgDataReturnType,
    ImgFwdTypes,
    ImgXorTabDataSplit,
    TabDataReturnType,
)
from bitfount.data.datastructure import DataStructure
from bitfount.data.types import SemanticType
from bitfount.models.base_models import (
    CNNModelStructure,
    FeedForwardModelStructure,
    NeuralNetworkModelStructure,
    NeuralNetworkPredefinedModel,
    Scheduler,
)
from bitfount.types import T_FIELDS_DICT
from bitfount.utils import DEFAULT_SEED

logger = logging.getLogger(__name__)


class PyTorchImageClassifier(PyTorchClassifierMixIn, BasePyTorchModel):
    """A Pytorch model designed specifically for image classification problems.

    The model can handle binary, multiclass and multilabel classification problems.

    Raises:
        ValueError: If the model structure is not an instance of `CNNModelStructure` or
            `NeuralNetworkPredefinedModel`.
        ValueError: If the loss function is not `nn.BCEWithLogitsLoss` or
            `nn.CrossEntropyLoss`.

    :::info

    Currently images are scaled to 224 x 224.

    :::
    """

    train_dl: _BasePyTorchBitfountDataLoader
    datastructure: DataStructure
    input_dim: int = 224  # default input images are 224 x 224

    def __init__(self, **kwargs: Any):
        model_structure = kwargs.pop("model_structure", CNNModelStructure())
        if not isinstance(
            model_structure, (CNNModelStructure, NeuralNetworkPredefinedModel)
        ):
            raise ValueError("Model structure does not match model")

        super().__init__(model_structure=model_structure, **kwargs)
        if self.loss_func is None:
            if self.multilabel:
                self.loss_func = nn.BCEWithLogitsLoss
            else:
                self.loss_func = nn.CrossEntropyLoss
        elif self.loss_func not in [nn.BCEWithLogitsLoss, nn.CrossEntropyLoss]:
            raise ValueError("This loss function is not currently supported")

    def forward(self, x: ImgFwdTypes) -> Any:  # type: ignore[override] # Reason: see below # noqa: B950
        """Performs a forward pass of the model."""
        # override as the forward function is incompatible with pl.LightningModule
        if self.datastructure.number_of_images > 1:
            aux = []
            for i in range(len(x)):
                aux.append(self._model(x[i]))  # type: ignore[misc] # reason: model should be initialised already # noqa: B950
            return torch.cat([item[0] for item in aux], 1)
        else:
            return self._model(x)  # type: ignore[misc] # reason: model should be initialised already # noqa: B950

    def _split_dataloader_output(
        self,
        data: Union[
            ImgAndTabDataSplit,
            ImgXorTabDataSplit,
        ],
    ) -> Union[ImgDataReturnType, TabDataReturnType]:
        """Splits dataloader output into image tensor, weights and category."""
        images, sup = cast(Tuple[torch.Tensor, torch.Tensor], data)
        weights = sup[:, 0].float()
        category: Optional[torch.Tensor]
        if sup.shape[1] > 2:
            category = sup[:, -1:].long()
        else:
            category = None

        return images, weights, category

    def _get_convolution_final_output_dimension(self) -> int:
        """Calculates the output size of the final convolutional layer.

        This will become the input size of the first feedforward layer
        """
        input_dim: float = self.input_dim
        if isinstance(self.model_structure, CNNModelStructure):
            # self.model_structure.layers is set in post_init, so we can just cast
            for _ in cast(List[int], self.model_structure.layers):
                output_dim = self._get_convolution_output_dimension(
                    input_dim,
                    self.model_structure.kernel_size,
                    self.model_structure.padding,
                    self.model_structure.stride,
                )
                output_dim = output_dim / 2  # due to pooling
                input_dim = output_dim

            return int(
                (output_dim**2) * cast(List[int], self.model_structure.layers)[-1]
            )
        else:
            raise TypeError("This method only works with the cnn model structure.")

    @staticmethod
    def _get_convolution_output_dimension(
        input_size: Union[int, float], kernel_size: int, padding: int, stride: int
    ) -> float:
        """Gets convolution output dimension."""
        return ((input_size - kernel_size + (2 * padding)) / stride) + 1

    def _create_model(self) -> nn.Module:
        """Creates the model to use.

        If `self.model_structure` is a `NeuralNetworkPredefinedModel`, then calls
        `get_torchvision_classification_model` to adapt model head for the task
        before returning the model

        Otherwise, creates model as defined by `CNNModelStructure`
        """
        table_schema = self.datastructure.get_table_schema(
            schema=self.schema, pod_identifier=self.pod_identifier
        )

        self.set_number_of_classes(table_schema)

        if isinstance(self.model_structure, NeuralNetworkPredefinedModel):
            kwargs = self.model_structure.kwargs or {}
            model = _get_torchvision_classification_model(
                self.model_structure.name,
                self.model_structure.pretrained,
                self.n_classes,
                **kwargs,
            )
        elif isinstance(self.model_structure, CNNModelStructure):
            # self.model_structure.layers is set in post_init, so we can just cast
            layer_sizes = self._get_layer_sizes(
                cast(List[int], self.model_structure.layers), 3
            )

            head_sizes = [
                (self.model_structure.ff_layers[-1], self.n_classes)
                for _ in range(self.model_structure.num_heads)
            ]
            ff_layer_sizes = self._get_layer_sizes(
                self.model_structure.ff_layers,
                self._get_convolution_final_output_dimension(),
            )
            logger.debug(f"Creating model with {self.model_structure.num_heads} heads")
            # self.model_structure.dropout_probs is set in post_init,
            # so we can just cast below
            model = _PyTorchConvNeuralNet(
                layer_sizes,
                cast(List[float], self.model_structure.dropout_probs),
                self.model_structure.mish_activation_function,
                head_sizes,
                ff_layer_sizes,
                self.model_structure.ff_dropout_probs,
                self.model_structure.kernel_size,
                self.model_structure.padding,
                self.model_structure.stride,
                self.model_structure.pooling_function,
            )
        return model


class PyTorchTabularClassifier(PyTorchClassifierMixIn, BasePyTorchModel):
    """A Pytorch model designed specifically for tabular classification problems.

    The model can handle binary, multiclass and multilabel classification problems.

    Raises:
        ValueError: If the model structure is not an instance of
            `FeedForwardModelStructure`.
        ValueError: If the loss function is not `nn.BCEWithLogitsLoss` or
            `nn.CrossEntropyLoss`.
    """

    train_dl: _BasePyTorchBitfountDataLoader

    def __init__(self, **kwargs: Any):
        model_structure = kwargs.pop("model_structure", FeedForwardModelStructure())
        if (
            isinstance(model_structure, NeuralNetworkPredefinedModel)
            and model_structure.name == "TabNet"
        ):
            raise ValueError("Please create a TabNetClassifier directly.")
        elif not isinstance(model_structure, FeedForwardModelStructure):
            raise ValueError("Please provide a FeedForwardModelStructure")
        super().__init__(
            model_structure=cast(NeuralNetworkModelStructure, model_structure),
            **kwargs,
        )

        if self.loss_func is None:
            if hasattr(self, "multilabel") and (self.multilabel is not False):
                self.loss_func = nn.BCEWithLogitsLoss
            else:
                self.loss_func = nn.CrossEntropyLoss
        elif self.loss_func not in [nn.BCEWithLogitsLoss, nn.CrossEntropyLoss]:
            raise ValueError("This loss function is not currently supported")

    def _create_model(self) -> _PyTorchFeedForwardNeuralNet:
        """Creates model to use.

        Takes number of continuous features and number of heads. Creates and
        returns model.
        """
        ignore_cols_for_training = self.datastructure.get_columns_ignored_for_training()
        table_schema = self.datastructure.get_table_schema(
            schema=self.schema, pod_identifier=self.pod_identifier
        )
        self.set_number_of_classes(table_schema)

        num_continuous = len(
            [
                col
                for col in table_schema.get_feature_names(
                    SemanticType.CONTINUOUS,
                )
                if col not in ignore_cols_for_training
            ]
        )
        embedding_sizes = _calculate_embedding_sizes(
            table_schema.get_categorical_feature_sizes(ignore_cols_for_training)
        )
        self.model_structure = cast(FeedForwardModelStructure, self.model_structure)
        num_heads = self.model_structure.num_heads
        num_categorical = sum(size for _, size in embedding_sizes)
        # self.model_structure.layers is set in post_init, so we can just cast
        layer_sizes = self._get_layer_sizes(
            cast(
                List[int],
                self.model_structure.layers,
            ),
            num_continuous + num_categorical,
        )
        head_sizes = [
            (
                cast(
                    List[int],
                    self.model_structure.layers,
                )[-1],
                self.n_classes,
            )
            for _ in range(num_heads)
        ]
        # self.model_structure.dropout_probs is set in post_init,
        # so we can just cast below
        logger.debug(f"Creating model with {num_heads} heads")
        model = _PyTorchFeedForwardNeuralNet(
            embedding_sizes,
            self.model_structure.embedding_dropout,
            num_continuous,
            layer_sizes,
            cast(List[float], self.model_structure.dropout_probs),
            self.model_structure.mish_activation_function,
            head_sizes,
        )
        return model

    def _split_dataloader_output(
        self,
        data: Union[
            ImgAndTabDataSplit,
            ImgXorTabDataSplit,
        ],
    ) -> Union[ImgDataReturnType, TabDataReturnType]:
        """Splits dataloader output.

        Splits it into pieces for categorical, continuous, weights and categories.

        NB: `ignore_classes` is never returned
        """
        tab, sup = cast(ImgXorTabDataSplit, data)
        ignore_cols_for_training = self.datastructure.get_columns_ignored_for_training()

        table_schema = self.datastructure.get_table_schema(
            schema=self.schema, pod_identifier=self.pod_identifier
        )
        n_cat = len(
            _calculate_embedding_sizes(
                table_schema.get_categorical_feature_sizes(ignore_cols_for_training)
            )
        )
        n_cont = len(
            [
                col
                for col in table_schema.get_feature_names(
                    SemanticType.CONTINUOUS,
                )
                if col not in ignore_cols_for_training
            ]
        )
        # Get items according to the order they are in the tensor
        cat_pos = n_cat
        cont_pos = cat_pos + n_cont
        x_1 = tab[:, :cat_pos].long()  # categorical features
        x_2 = tab[:, cat_pos:cont_pos].float()  # continuous features
        weights = sup[:, 0].float()
        # If category is present, return it, otherwise return None
        category: Optional[torch.Tensor]
        if sup.shape[1] > 2:
            category = sup[:, -1:].long()
        else:
            category = None
        return (x_1.t(), x_2), weights, category


class PyTorchLogisticRegressionClassifier(PyTorchClassifierMixIn, BasePyTorchModel):
    """A Logistic Regression classifier implemented in PyTorch.

    Utilises softmax regression to allow extension to more than 2 classes.

    The input and output dimensions are calculated from the data automatically.
    """

    train_dl: _PyTorchBitfountDataLoader
    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "bias": fields.Boolean(),
        "l1_regularization_weight": fields.Float(allow_none=True),
        "l2_regularization_weight": fields.Float(allow_none=True),
        "embed_categorical": fields.Boolean(),
        "embed_categorical_dropout": fields.Float(),
    }

    def __init__(
        self,
        bias: bool = True,
        l1_regularization_weight: Optional[float] = None,
        l2_regularization_weight: Optional[float] = None,
        embed_categorical: bool = True,
        embed_categorical_dropout: float = 0.04,
        **kwargs: Any,
    ) -> None:
        """Create a logistic regression classifier using PyTorch.

        A softmax regressor is used to ensure this can work on multi-class
        problems.

        Args:
            bias: Whether the underlying linear layer should learn an additive
                bias. Default True.
            l1_regularization_weight: The weight of L1 regularization to apply, if any.
            l2_regularization_weight: The weight of L2 regularization to apply, if any.
            embed_categorical: Whether to use categorical embedding layers to handle
                categorical variables, or to treat them as inherently label-encoded.
                Default True.
            embed_categorical_dropout: The dropout probability to apply to categorical
                variables if using embed_categorical.
            **kwargs: Other keyword arguments for the model.
        """
        # Override model_structure; model_structure is required by the
        # NeuralNetworkMixin, but is not used in this class, so we override it
        # with an empty one and log out that this has happened
        # Have to use empty lists as otherwise they get overwritten with defaults
        empty_model_structure = FeedForwardModelStructure(
            layers=[], dropout_probs=[], mish_activation_function=False
        )
        try:
            if kwargs["model_structure"] != empty_model_structure:
                logger.warning(
                    f"Specified model structure is not compatible with "
                    f"{self.__class__.__name__}; will be overridden."
                )
                kwargs["model_structure"] = empty_model_structure
        except KeyError:
            kwargs["model_structure"] = empty_model_structure

        super().__init__(**kwargs)

        # Multilabel LogReg is not supported
        if self.multilabel:
            raise ValueError(
                f"{self.__class__.__name__} does not support multilabel "
                f"classification problems."
            )
        # Multihead LogReg is not supported
        try:
            model_structure = cast(NeuralNetworkModelStructure, self.model_structure)
            if model_structure.num_heads != 1:
                logger.warning("Multihead LogReg is not supported, setting to 1.")
                model_structure.num_heads = 1
        except AttributeError:
            pass

        # Set loss function. Only CrossEntropyLoss is currently supported.
        if self.loss_func is None:
            self.loss_func = nn.CrossEntropyLoss
        elif self.loss_func is not nn.CrossEntropyLoss:
            raise ValueError("This loss function is not currently supported")

        self.bias = bias
        self.l1_regularization_weight = l1_regularization_weight
        self.l2_regularization_weight = l2_regularization_weight
        self.embed_categorical = embed_categorical
        self.embed_categorical_dropout = embed_categorical_dropout

    def _create_model(self) -> nn.Module:
        table_schema = self.datastructure.get_table_schema(
            schema=self.schema, pod_identifier=self.pod_identifier
        )
        # Set number of output classes from datastructure
        self.set_number_of_classes(table_schema)

        # Get details on continuous and categorical features
        ignore_cols_for_training = self.datastructure.get_columns_ignored_for_training()

        if self.embed_categorical:
            # If categorical embedding requested, calculate embedding sizes
            logger.info("Generating Categorical Embeddings for categorical features.")
            embedding_sizes = _calculate_embedding_sizes(
                table_schema.get_categorical_feature_sizes(ignore_cols_for_training)
            )
            num_continuous = table_schema.get_num_continuous(
                ignore_cols=ignore_cols_for_training
            )
            model = _PyTorchLogisticRegression(
                num_classes=self.n_classes,
                num_continuous=num_continuous,
                embedding_sizes=embedding_sizes,
                embedding_dropout_frac=self.embed_categorical_dropout,
                bias=self.bias,
            )
        else:
            # Treat categorical values as label encoded
            logger.info(
                "No categorical embedding requested;"
                " categorical data should be label-encoded."
            )
            num_categorical = table_schema.get_num_categorical(
                ignore_cols=ignore_cols_for_training
            )
            num_continuous = table_schema.get_num_continuous(
                ignore_cols=ignore_cols_for_training
            )
            input_dim = num_continuous + num_categorical
            model = _PyTorchLogisticRegression(
                num_classes=self.n_classes,
                input_dim=input_dim,
                bias=self.bias,
            )

        return model

    def _split_dataloader_output(
        self,
        data: Union[
            ImgAndTabDataSplit,
            ImgXorTabDataSplit,
        ],
    ) -> Union[ImgDataReturnType, TabDataReturnType]:
        """Splits dataloader output.

        Splits it into pieces for categorical, continuous, weights and
        (optionally) categories.

        Depending on whether embed_categorical is True or not will affect the shape
        of the returned categorical data tensor, either to ensure it can pass through
        the embedding layers correctly or to treat it as inherently label-encoded.

        NB: `ignore_classes` is never returned
        """
        # Split into the tabular data and supplementary data
        tab, sup = cast(ImgXorTabDataSplit, data)

        # Gather schema-related information
        ignore_cols_for_training = self.datastructure.get_columns_ignored_for_training()
        table_schema = self.datastructure.get_table_schema(
            schema=self.schema, pod_identifier=self.pod_identifier
        )

        # Calculate the number of continuous and categorical columns
        n_categorical = table_schema.get_num_categorical(
            ignore_cols=ignore_cols_for_training
        )
        n_continuous = table_schema.get_num_continuous(
            ignore_cols=ignore_cols_for_training
        )

        # Split tensor into categorical and continuous items
        end_categorical_idx = n_categorical
        x_categorical = tab[:, :end_categorical_idx].long()  # categorical features
        end_continuous_idx = end_categorical_idx + n_continuous
        x_continuous = tab[
            :, end_categorical_idx:end_continuous_idx
        ].float()  # continuous features

        # Weights will be first entry in the supplementary tensor
        weights = sup[:, 0].float()

        # If category is present (the remaining entries in the supplementary tensor),
        # return it, otherwise return None
        category: Optional[torch.Tensor]
        if sup.shape[1] > 2:
            category = sup[:, -1:].long()
        else:
            category = None

        if self.embed_categorical:
            # Return (transposed categorical tensor, continuous tensor), weights
            # tensor and category tensor (or None).
            # Categorical must be transposed to allow it to pass through the
            # embedding layers correctly.
            return (x_categorical.t(), x_continuous), weights, category
        else:
            # Otherwise, return categorical as is, expecting it to be label-encoded.
            # Return (categorical tensor, continuous tensor), weights tensor and
            # category tensor (or None).
            return (x_categorical, x_continuous), weights, category

    def _get_loss(
        self,
        output: torch.Tensor,
        target: torch.Tensor,
        loss_modifiers: Tuple[torch.Tensor, ...],
    ) -> torch.Tensor:
        """Computes the appropriate (weighted) loss.

        Applies L1 and L2 regularization if requested.

        Args:
            output: The model output.
            target: The expected output.
            loss_modifiers: A tuple of tensors representing additional loss modifiers:
                - 0: weightings for each sample in this batch
                - 1: categories

        Returns:
            A scalar tensor representing the loss.
        """
        loss = super()._get_loss(output, target, loss_modifiers)

        sample_weight: torch.Tensor = loss_modifiers[0]
        weight_sum = sample_weight.squeeze().sum()

        # Apply L1 regularisation if requested
        if (
            self.l1_regularization_weight is not None
            and self.l1_regularization_weight > 0
        ):
            model: Module = cast(Module, self._model)
            linear_layer: Module = cast(Module, model.linear)
            weight_tensor: torch.Tensor = cast(torch.Tensor, linear_layer.weight)

            l1_reg_term = weight_tensor.abs().sum()
            # As loss is already a (weighted) average we need to similarly divide the
            # regularisation term by the total weight.
            l1_reg_term /= weight_sum
            loss += self.l1_regularization_weight * l1_reg_term

        # Apply L2 regularisation if requested
        if (
            self.l2_regularization_weight is not None
            and self.l2_regularization_weight > 0
        ):
            model = cast(Module, self._model)
            linear_layer = cast(Module, model.linear)
            weight_tensor = cast(torch.Tensor, linear_layer.weight)

            l2_reg_term = weight_tensor.pow(2).sum()
            # As loss is already a (weighted) average we need to similarly divide the
            # regularisation term by the total weight.
            l2_reg_term /= weight_sum
            loss += self.l2_regularization_weight * l2_reg_term

        return loss


class TabNetClassifier(PyTorchClassifierMixIn, BaseTabNetModel):
    """TabNet Classifier for binary and multiclass tabular classification problems.

    See base class for more information.
    """

    train_dl: _PyTorchBitfountDataLoader

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def _create_model(self) -> TabNetClassifier_:
        """Create model for Binary or Multiclass classification."""
        ignore_cols_for_training = self.datastructure.get_columns_ignored_for_training()

        table_schema = self.datastructure.get_table_schema(
            schema=self.schema, pod_identifier=self.pod_identifier
        )
        self.set_number_of_classes(table_schema)

        # Only consider the tabular part
        X: pd.DataFrame
        if isinstance(self.train_dl.get_x_dataframe(), tuple):
            X, _ = self.train_dl.get_x_dataframe()
        elif isinstance(self.train_dl.get_x_dataframe(), pd.DataFrame):
            X = cast(pd.DataFrame, self.train_dl.get_x_dataframe())
        cat_idxs = [
            i
            for i, f in enumerate(X.columns)
            if f
            in table_schema.get_feature_names(
                SemanticType.CATEGORICAL,
            )
            if f not in ignore_cols_for_training
        ]

        if self.embedding_sizes is None:

            embedding_sizes = _calculate_embedding_sizes(
                table_schema.get_categorical_feature_sizes(ignore_cols_for_training)
            )
            self.embedding_sizes = cast(List[int], [i[1] for i in embedding_sizes])

        return TabNetClassifier_(
            cat_idxs=cat_idxs,
            cat_dims=table_schema.get_categorical_feature_sizes(
                ignore_cols=ignore_cols_for_training
            ),
            cat_emb_dim=self.embedding_sizes,
            optimizer_fn=_OPTIMIZERS[self.optimizer.name],
            optimizer_params=self.optimizer.params,
            scheduler_params=cast(Scheduler, self.scheduler).params,
            scheduler_fn=_SCHEDULERS[cast(Scheduler, self.scheduler).name],
            mask_type=self.mask_type,
            seed=self.seed or DEFAULT_SEED,
        )
