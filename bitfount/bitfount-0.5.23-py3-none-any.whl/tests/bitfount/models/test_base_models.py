"""Tests for base model classes."""
from __future__ import annotations

from typing import Any, cast
from unittest.mock import Mock

from marshmallow import fields
from pytest import fixture

from bitfount.data.datastructure import DataStructure
from bitfount.models.base_models import (
    MAIN_MODEL_REGISTRY,
    EarlyStopping,
    FeedForwardModelStructure,
    NeuralNetworkMixIn,
    NeuralNetworkModelStructure,
    Optimizer,
    Scheduler,
)
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import create_datastructure, unit_test


class _NeuralNetworkMixIn_(NeuralNetworkMixIn):
    def __init__(self, datastructure: DataStructure, **kwargs: Any):
        self.datastructure = datastructure
        self.class_name = type(self).__name__

        super().__init__(**kwargs)
        fields_dict = {  # noqa: F841
            "datastructure": fields.Raw(),
        }

    @staticmethod
    def _get_optimizer(  # type:ignore[override] # reason, used just for testing
        optimizer: Optimizer,
    ) -> None:
        return None

    @staticmethod
    def _get_scheduler(  # type:ignore[override] # reason, used just for testing
        scheduler: Scheduler,
    ) -> None:
        return None


@unit_test
class TestNeuralNetworkMixIn:
    """Tests for the NeuralNetworkMixIn."""

    @fixture
    def model_structure(self) -> NeuralNetworkModelStructure:
        """Model structure fixture."""
        return NeuralNetworkModelStructure()

    @fixture
    def mock_datastructure(self) -> Mock:
        """Mock datastructure fixture."""
        return Mock(multihead_col=None)

    def test_scheduler_structure_works_with_params(
        self, mock_datastructure: Mock, model_structure: NeuralNetworkModelStructure
    ) -> None:
        """Tests the scheduler loads parameters correctly."""
        nn = _NeuralNetworkMixIn_(
            datastructure=mock_datastructure,
            model_structure=model_structure,
            epochs=1,
            scheduler=Scheduler("OneCycleLR", {"max_lr": 0.01}),
        )

        model_scheduler = cast(Scheduler, nn.scheduler)
        assert model_scheduler.name == "OneCycleLR"
        assert model_scheduler.params == {"max_lr": 0.01}

    def test_scheduler_structure_works_no_params(
        self, mock_datastructure: Mock, model_structure: NeuralNetworkModelStructure
    ) -> None:
        """Tests the scheduler loads correctly when no scheduler_params given."""
        nn = _NeuralNetworkMixIn_(
            datastructure=mock_datastructure,
            model_structure=model_structure,
            epochs=1,
            scheduler=Scheduler("OneCycleLR"),
        )

        model_scheduler = cast(Scheduler, nn.scheduler)
        assert model_scheduler.name == "OneCycleLR"
        assert model_scheduler.params == {}

    def test_early_stopping(
        self, mock_datastructure: Mock, model_structure: NeuralNetworkModelStructure
    ) -> None:
        """Tests early stopping loads parameters correctly."""
        early_stopping_params = dict(
            monitor="validation_loss",
            min_delta=0.00,
            patience=2,
            verbose=True,
            mode="min",
        )
        nn = _NeuralNetworkMixIn_(
            datastructure=mock_datastructure,
            model_structure=model_structure,
            epochs=10,
            early_stopping=EarlyStopping(early_stopping_params),
        )
        model_es = cast(EarlyStopping, nn.early_stopping)
        assert model_es.params == early_stopping_params
        assert model_es is not None

    def test_optimizer(
        self, mock_datastructure: Mock, model_structure: NeuralNetworkModelStructure
    ) -> None:
        """Tests the optimizer loads parameters correctly."""
        optimizer = Optimizer(name="SGD", params={"lr": 0.1})
        nn = _NeuralNetworkMixIn_(
            datastructure=mock_datastructure,
            model_structure=model_structure,
            epochs=1,
            optimizer=optimizer,
        )
        model_optimizer = nn.optimizer
        assert model_optimizer.name == "SGD"
        assert model_optimizer.params == {"lr": 0.1}

    def test_no_optimizer_no_params(
        self, mock_datastructure: Mock, model_structure: NeuralNetworkModelStructure
    ) -> None:
        """Tests the default optimizer with defined params loads correctly."""
        nn = _NeuralNetworkMixIn_(
            datastructure=mock_datastructure,
            model_structure=model_structure,
            epochs=1,
        )
        model_optimizer = nn.optimizer
        assert model_optimizer.name == "AdamW"
        assert model_optimizer.params == {"lr": 0.01}

    def test_optimizer_no_params(
        self, mock_datastructure: Mock, model_structure: NeuralNetworkModelStructure
    ) -> None:
        """Tests the optimizer loads params correctly with no optimizer_params."""
        optimizer = Optimizer(name="SGD")
        nn = _NeuralNetworkMixIn_(
            datastructure=mock_datastructure,
            model_structure=model_structure,
            epochs=1,
            optimizer=optimizer,
        )
        model_optimizer = nn.optimizer
        assert model_optimizer.name == "SGD"
        assert model_optimizer.params == {}

    def test_serialization_deserialization(self, mock_datastructure: Mock) -> None:
        """Tests (de)serialization of the NeuralNetworkMixin class."""
        nn = _NeuralNetworkMixIn_(
            datastructure=create_datastructure(),
            model_structure=FeedForwardModelStructure(),
            batch_size=1,
            epochs=1,
            steps=None,  # as only one of epochs/steps can be specified
            optimizer=Optimizer(name="blah", params={"blah": 1}),
            scheduler=Scheduler("blah", {"blah": 1}),
            custom_loss_func=None,
            early_stopping=EarlyStopping({"blah": 1}),
        )

        # Dump and reload the class variables
        dumped = bf_dump(nn)
        loaded = bf_load(dumped, MAIN_MODEL_REGISTRY)

        # We compare across __dict__ as NeuralNetworkMixIn does not have
        # an __eq__ method.
        assert loaded.__dict__ == nn.__dict__
