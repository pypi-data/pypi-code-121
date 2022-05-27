"""Tests for the federated model training algorithm."""
from typing import TYPE_CHECKING
from unittest.mock import Mock, create_autospec

import numpy as np
from pytest_mock import MockerFixture

from bitfount import BitfountSchema
from bitfount.backends.pytorch.models.models import PyTorchTabularClassifier
from bitfount.federated.algorithms.base import (
    _BaseAlgorithm,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithm,
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.federated_training import (
    FederatedModelTraining,
    _BaseModelTrainingMixIn,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.utils import _ALGORITHMS
from bitfount.hub import BitfountHub
from bitfount.schemas.utils import bf_dump, bf_load
from tests.bitfount.backends.pytorch.models.test_models import assert_vars_equal
from tests.utils.helper import backend_test, create_datastructure, unit_test


class TestFederatedModelTraining:
    """Test Federated Model Training algorithm."""

    @unit_test
    def test_modeller(self, model: Mock) -> None:
        """Test modeller method."""
        algorithm_factory = FederatedModelTraining(model=model)
        algorithm = algorithm_factory.modeller()
        for type_ in [
            _BaseAlgorithm,
            _BaseModellerAlgorithm,
            _BaseModelAlgorithm,
            _BaseModellerModelAlgorithm,
        ]:
            assert isinstance(algorithm, type_)
        assert algorithm.steps == 10

    @unit_test
    def test_worker(self, model: Mock) -> None:
        """Test worker method."""
        algorithm_factory = FederatedModelTraining(model=model)
        algorithm = algorithm_factory.worker(
            hub=create_autospec(BitfountHub, instance=True)
        )
        for type_ in [
            _BaseAlgorithm,
            _BaseWorkerAlgorithm,
            _BaseModelAlgorithm,
            _BaseWorkerModelAlgorithm,
        ]:
            assert isinstance(algorithm, type_)
        assert algorithm.steps == 10

    @unit_test
    def test_modeller_logs_validation_metrics(
        self, mocker: MockerFixture, model: Mock
    ) -> None:
        """Test that the validation metrics are logged for the modeller."""
        mocker.patch.object(
            _BaseModelTrainingMixIn,
            "get_param_states",
            return_value={"layer1": np.ndarray([0, 1, 2, 3])},
        )
        mock_model_log = Mock()
        mocker.patch.object(model, "log_", mock_model_log)

        algorithm_factory = FederatedModelTraining(model=model)
        algorithm = algorithm_factory.modeller()

        algorithm.run(validation_metrics={"AUC": 0.8})
        mock_model_log.assert_called()

    @unit_test
    def test_worker_run_calls_diff_params(
        self, mocker: MockerFixture, model: Mock
    ) -> None:
        """Test worker run method calls diff_params.

        Test we return the difference between the old and new model parameters.
        """
        algorithm_factory = FederatedModelTraining(model=model)
        algorithm = algorithm_factory.worker(
            hub=create_autospec(BitfountHub, instance=True)
        )
        mock_diff_params = mocker.patch.object(algorithm, "diff_params")
        data = Mock()
        serialized_model_params = Mock()
        algorithm.run(data, serialized_model_params, iterations=1)
        mock_diff_params.assert_called_once()


@backend_test
@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for column average algorithm."""

    def test_serialization(self) -> None:
        """Test Marshmallow Serialization for column average algorithm."""
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            epochs=2,
        )
        algorithm_factory = FederatedModelTraining(model=model)
        dumped = bf_dump(algorithm_factory)
        loaded = bf_load(dumped, _ALGORITHMS)

        assert algorithm_factory.class_name == loaded.class_name
        assert_vars_equal(vars(algorithm_factory.model), vars(loaded.model))


# Static tests for algorithm-protocol compatibility
if TYPE_CHECKING:
    from typing import cast

    from bitfount.federated.protocols.fed_avg import (
        _FederatedAveragingCompatibleAlgoFactory,
        _FederatedAveragingCompatibleModeller,
        _FederatedAveragingCompatibleWorker,
    )
    from bitfount.types import (
        DistributedModelProtocol,
        _DistributedModelTypeOrReference,
    )

    # Check compatible with FederatedAveraging
    _algo_factory: _FederatedAveragingCompatibleAlgoFactory = FederatedModelTraining(
        model=cast(_DistributedModelTypeOrReference, object())
    )
    _modeller_side: _FederatedAveragingCompatibleModeller = _ModellerSide(
        model=cast(DistributedModelProtocol, object())
    )
    _worker_side: _FederatedAveragingCompatibleWorker = _WorkerSide(
        model=cast(DistributedModelProtocol, object())
    )
