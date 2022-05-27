"""Tests PyTorch NeuralNetwork-based classes."""
import re
from typing import List, Optional, Tuple, cast

from _pytest.logging import LogCaptureFixture
import pytest
from pytest import fixture
from pytest_lazyfixture import lazy_fixture
import torch
from torch.nn import Embedding

from bitfount.backends.pytorch.models.nn import (
    _get_torchvision_classification_model,
    _PyTorchLogisticRegression,
)
from tests.utils.helper import (
    backend_test,
    get_warning_logs,
    integration_test,
    unit_test,
)


@backend_test
@unit_test
class TestPyTorchLogisticRegression:
    """Tests for _PyTorchLogisticRegression model."""

    @fixture
    def embedding_sizes(self) -> List[Tuple[int, int]]:
        """A set of embedding sizes for categorical features."""
        return [(5, 10), (10, 5), (3, 4)]

    def test_init_prioritises_input_dim(
        self, caplog: LogCaptureFixture, embedding_sizes: List[Tuple[int, int]]
    ) -> None:
        """Tests input_dim given preference over embedding args.

        When both are supplied, the embedding-related args should be ignored in
        preference of using input_dim.
        """
        log_reg = _PyTorchLogisticRegression(
            num_classes=5,
            input_dim=10,
            num_continuous=5,
            embedding_sizes=embedding_sizes,
        )

        # Check warning logs
        warning_logs = get_warning_logs(caplog)
        assert (
            "Cannot specify both input_dim and either of num_continuous or "
            "embedding_sizes. Will default to using input_dim." in warning_logs
        )

        # Check correct attributes are set
        assert log_reg.input_dim == 10
        assert log_reg.num_continuous is None
        assert log_reg.embedding_sizes is None

    def test_init_fails_if_neither_input_dim_or_embeddings_supplied(self) -> None:
        """Test init raises error if neither input_dim or embeddings supplied."""
        with pytest.raises(
            ValueError,
            match=re.escape("One of input_dim or embedding_sizes must be provided."),
        ):
            _PyTorchLogisticRegression(num_classes=5)

    @pytest.mark.parametrize(
        argnames=("embedding_sizes_arg", "num_continuous_arg"),
        argvalues=(
            pytest.param(
                lazy_fixture("embedding_sizes"), None, id="only embedding_sizes"
            ),
            pytest.param(None, 5, id="only num_continuous"),
        ),
    )
    def test_init_fails_if_mismatch_between_embedding_args(
        self,
        embedding_sizes_arg: Optional[List[Tuple[int, int]]],
        num_continuous_arg: Optional[int],
    ) -> None:
        """Test init raises error if only one embedding argument is provided.

        In particular, checks that embedding_sizes and num_continuous must both
        be provided or that neither must be.
        """
        # The error message will differ depending on which one is missing (no
        # embedding_sizes will get caught because there's also no input_dim) but
        # both cases should fail.
        with pytest.raises(ValueError):
            _PyTorchLogisticRegression(
                num_classes=5,
                embedding_sizes=embedding_sizes_arg,
                num_continuous=num_continuous_arg,
            )

    def test_init_when_using_embedding_args(
        self,
        embedding_sizes: List[Tuple[int, int]],
    ) -> None:
        """Tests init functions correctly when supplied embedding args.

        Checks that:
            - input_dim is created from supplied embedding-related args.
            - category embeddings are created
            - dropout is created
            - linear layer has correct sizes
        """
        num_classes = 10
        num_continuous = 5
        expected_input_dim = num_continuous + sum(size for _, size in embedding_sizes)

        log_reg = _PyTorchLogisticRegression(
            num_classes=num_classes,
            num_continuous=num_continuous,
            embedding_sizes=embedding_sizes,
        )

        # Check input_dim
        assert log_reg.input_dim == expected_input_dim
        # Check category embeddings
        assert log_reg.category_embeddings is not None
        for idx, embedding in enumerate(log_reg.category_embeddings):
            embedding = cast(Embedding, embedding)
            num_categories, category_embed_size = embedding_sizes[idx]
            assert embedding.num_embeddings == num_categories
            assert embedding.embedding_dim == category_embed_size
        # Check category embeddings dropout
        assert log_reg.category_embeddings_dropout is not None
        assert log_reg.category_embeddings_dropout.p == log_reg.embedding_dropout_frac
        # Check size of linear layer
        assert log_reg.linear.in_features == expected_input_dim
        assert log_reg.linear.out_features == num_classes

    def test_init_when_using_input_dim(self) -> None:
        """Tests init functions correctly when supplied input_dim.

        Checks that:
            - category embeddings are NOT created
            - dropout is NOT created
            - linear layer has correct sizes
        """
        num_classes = 10
        input_dim = 32

        log_reg = _PyTorchLogisticRegression(
            num_classes=num_classes,
            input_dim=input_dim,
        )

        # Check category embeddings
        assert log_reg.category_embeddings is None
        # Check category embeddings dropout
        assert log_reg.category_embeddings_dropout is None
        # Check size of linear layer
        assert log_reg.linear.in_features == input_dim
        assert log_reg.linear.out_features == num_classes

    @pytest.mark.parametrize(
        argnames=("embedding_sizes_arg", "num_continuous_arg"),
        argvalues=(
            pytest.param([], 10, id="continuous only"),
            pytest.param([(10, 20), (5, 15)], 0, id="categorical only"),
            pytest.param([(10, 20), (5, 15)], 10, id="categorical and continuous"),
        ),
    )
    def test_forward(
        self,
        embedding_sizes_arg: List[Tuple[int, int]],
        num_continuous_arg: int,
    ) -> None:
        """Test that forward works with various types of batch.

        Uses categorical embedding.

        Tests:
            - mixed categorical and continuous
            - categorical only
            - continuous only
        """
        # Construct appropriately shaped tensors
        batch_size = 32

        num_categorical = len(embedding_sizes_arg)
        categorical_tensor = torch.randint(
            low=0, high=5, size=(batch_size, num_categorical)
        )

        continuous_tensor = torch.rand(size=(batch_size, num_continuous_arg))

        # Categorical tensor must be transposed to allow it to pass through the
        # embedding layer; this is how it will be returned from
        # _split_dataloader_output.
        x = (categorical_tensor.t(), continuous_tensor)

        log_reg = _PyTorchLogisticRegression(
            num_classes=5,
            num_continuous=num_continuous_arg,
            embedding_sizes=embedding_sizes_arg,
        )

        # We don't assert anything on the results, we just want to check it
        # handles it without crashing.
        log_reg.forward(x)

    @pytest.mark.parametrize(
        argnames=("num_categorical_arg", "num_continuous_arg"),
        argvalues=(
            pytest.param(0, 10, id="continuous only"),
            pytest.param(5, 0, id="categorical only"),
            pytest.param(5, 10, id="categorical and continuous"),
        ),
    )
    def test_forward_without_categorical_embedding(
        self,
        num_categorical_arg: int,
        num_continuous_arg: int,
    ) -> None:
        """Test that forward works with various types of batch.

        Uses raw tensor embedding for categorical features.

        Tests:
            - mixed categorical and continuous
            - categorical only
            - continuous only
        """
        # Construct appropriately shaped tensors
        batch_size = 32

        categorical_tensor = torch.randint(
            low=0, high=5, size=(batch_size, num_categorical_arg)
        )

        continuous_tensor = torch.rand(size=(batch_size, num_continuous_arg))

        # Categorical tensor must NOT be transposed to allow it to pass through
        # the embedding layers. This is how it would be returned from
        # _split_dataloader_output.
        x = (categorical_tensor, continuous_tensor)

        log_reg = _PyTorchLogisticRegression(
            num_classes=5,
            input_dim=num_continuous_arg + num_categorical_arg,
        )

        # We don't assert anything on the results, we just want to check it
        # handles it without crashing.
        log_reg.forward(x)


@backend_test
@integration_test
class TestTorchvisionClassificationModels:
    """Tests retrieval of existing Torchvision models."""

    def test_unimplemented_model(self) -> None:
        """Tests error thrown if model exists but not supported."""
        with pytest.raises(
            ValueError,
            match="Model reshaping not implemented yet. Choose another model.",
        ):
            _get_torchvision_classification_model("googlenet", False, 2)

    def test_unrecognised_model(self) -> None:
        """Tests error thrown if model name not recognized."""
        with pytest.raises(ValueError, match="Model name not recognised"):
            _get_torchvision_classification_model("blahblahmodel", False, 2)

    def test_resnet(self) -> None:
        """Tests resnet* retrieval."""
        model = _get_torchvision_classification_model("resnet18", False, 2)
        assert model.fc.out_features == 2  # type: ignore[union-attr]  # Reason: test will fail if wrong type  # noqa: B950

    def test_alexnet(self) -> None:
        """Tests alexnet retrieval."""
        model = _get_torchvision_classification_model("alexnet", False, 2)
        assert model.classifier[6].out_features == 2  # type: ignore[index,union-attr]  # Reason: test will fail if wrong type  # noqa: B950

    def test_vgg(self) -> None:
        """Tests vgg* retrieval."""
        model = _get_torchvision_classification_model("vgg16", False, 2)
        assert model.classifier[6].out_features == 2  # type: ignore[index,union-attr]  # Reason: test will fail if wrong type  # noqa: B950

    def test_densenet(self) -> None:
        """Tests densenet* retrieval."""
        model = _get_torchvision_classification_model("densenet169", False, 2)
        assert model.classifier.out_features == 2  # type: ignore[union-attr]  # Reason: test will fail if wrong type  # noqa: B950

    def test_squeezenet(self) -> None:
        """Tests squeezenet* retrieval."""
        model = _get_torchvision_classification_model("squeezenet1_0", False, 2)
        assert model.classifier[1].out_channels == 2  # type: ignore[index,union-attr]  # Reason: test will fail if wrong type  # noqa: B950
        assert model.num_classes == 2
