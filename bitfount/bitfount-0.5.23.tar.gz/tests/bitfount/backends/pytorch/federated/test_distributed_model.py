"""Distributed tests with pytorch models."""

from typing import Optional

import pytest
import pytorch_lightning as pl
import torch

from bitfount.backends.pytorch.models.models import PyTorchTabularClassifier
from bitfount.backends.pytorch.types import _AdaptorForPyTorchTensor
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from tests.bitfount.backends.pytorch.helper import get_params_mean
from tests.utils.helper import (
    backend_test,
    create_datasource,
    create_datastructure,
    unit_test,
)


@pytest.fixture
def datastructure() -> DataStructure:
    """Fixture for datastructure."""
    return create_datastructure()


@pytest.fixture
def datasource(datastructure: DataStructure) -> _BaseSource:
    """Fixture for datasource."""
    return create_datasource(classification=True)


@backend_test
class TestDistributedModel:
    """Test distributed model methods with PyTorch models."""

    @unit_test
    def test_set_model_training_iterations_epochs(
        self, datastructure: DataStructure
    ) -> None:
        """Test setting of model training iterations with epochs."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), seed=42, epochs=2
        )
        model.set_model_training_iterations(7)
        assert model.epochs == 7
        assert model.steps is None

    @unit_test
    def test_set_model_training_iterations_steps(
        self, datastructure: DataStructure
    ) -> None:
        """Test setting of model training iterations with steps."""
        model = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), seed=42, steps=122
        )
        model.set_model_training_iterations(7)
        assert model.steps == 7
        assert model.epochs is None

    @unit_test
    def test_model_update_params(
        self, datasource: _BaseSource, datastructure: DataStructure
    ) -> None:
        """Check that updating model params works properly."""
        model1 = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), seed=42, epochs=2
        )
        model1.initialise_model(datasource)
        model1_original_params = model1.get_param_states()

        model2 = PyTorchTabularClassifier(
            datastructure=datastructure, schema=BitfountSchema(), seed=43, epochs=2
        )
        model2.initialise_model(datasource)
        model2_original_params = model2.get_param_states()

        assert not torch.isclose(
            get_params_mean(model1_original_params),
            get_params_mean(model2_original_params),
            atol=1e-4,
        )
        model1.update_params(model2_original_params)
        assert torch.isclose(
            get_params_mean(model1.get_param_states()),
            get_params_mean(model2_original_params),
            atol=1e-4,
        )

    @unit_test
    def test_model_diff_params(self) -> None:
        """Check that diffing model params works properly."""
        old_params = {
            "layer1": _AdaptorForPyTorchTensor(torch.tensor([1.0, 2.0, 3.0, 4.0]))
        }
        new_params = {
            "layer1": _AdaptorForPyTorchTensor(torch.tensor([10.0, 20.0, 30.0, 40.0]))
        }
        expected_param_diff = torch.tensor([9.0, 18.0, 27.0, 36.0])
        param_diff = PyTorchTabularClassifier.diff_params(old_params, new_params)
        if isinstance(param_diff["layer1"], _AdaptorForPyTorchTensor):
            for i, j in zip(param_diff["layer1"].torchtensor, expected_param_diff):
                assert torch.isclose(i, j)

    @unit_test
    @pytest.mark.parametrize("epochs,steps", [(1, None), (None, 1)])
    def test_reset_trainer(self, epochs: Optional[int], steps: Optional[int]) -> None:
        """Tests resetting of trainer."""
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            epochs=epochs,
            steps=steps,
        )
        model.initialise_model(create_datasource(classification=True))
        model._pl_trainer.random_attribute = 5  # type: ignore[attr-defined] # Reason: integral to test # noqa: B950
        model._total_num_batches_trained = 5
        model.reset_trainer()
        assert isinstance(model._pl_trainer, pl.Trainer)
        # Check that new trainer does not have the random attribute to ensure it is new
        assert not hasattr(model._pl_trainer, "random_attribute")
        # Check that the number of steps to be trained is updated correctly
        if steps:
            assert model.steps == steps
            assert (
                model._pl_trainer.max_steps == model._total_num_batches_trained + steps
            )
        # Check that the number of epochs to be trained is updated correctly
        elif epochs:
            assert model.epochs == epochs
            assert model._pl_trainer.max_epochs == epochs

    @unit_test
    @pytest.mark.parametrize(
        "steps,total_num_batches_trained", [(1, 0), (3, 3), (5, 10)]
    )
    def test_reset_trainer_steps(
        self, steps: int, total_num_batches_trained: int
    ) -> None:
        """Tests resetting of trainer with steps specfied as the type of iteration.

        Checks that the `max_steps` attribute on the trainer is correctly set.
        """
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            steps=steps,
        )
        model.initialise_model(create_datasource(classification=True))
        model._total_num_batches_trained = total_num_batches_trained
        model.reset_trainer()

        assert model._pl_trainer.max_steps == steps + (
            total_num_batches_trained % len(model.train_dl)
        )
