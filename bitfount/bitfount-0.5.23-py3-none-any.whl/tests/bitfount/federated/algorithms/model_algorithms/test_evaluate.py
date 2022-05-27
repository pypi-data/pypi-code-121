"""Tests for the model evaluation algorithm."""
from typing import TYPE_CHECKING
from unittest.mock import Mock, create_autospec

import pytest
from pytest_mock import MockerFixture

from bitfount import BitfountSchema
from bitfount.backends.pytorch.models.models import PyTorchTabularClassifier
from bitfount.federated.algorithms.base import (
    _BaseAlgorithm,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms import evaluate
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithm,
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.evaluate import (
    ModelEvaluation,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.utils import _ALGORITHMS
from bitfount.hub import BitfountHub
from bitfount.schemas.utils import bf_dump, bf_load
from tests.bitfount.backends.pytorch.models.test_models import assert_vars_equal
from tests.utils.helper import backend_test, create_datastructure, unit_test


class TestModelEvaluation:
    """Test Evaluate algorithm."""

    @unit_test
    def test_modeller_types(self, model: Mock) -> None:
        """Test modeller method."""
        algorithm_factory = ModelEvaluation(model=model)
        algorithm = algorithm_factory.modeller()
        for type_ in [
            _BaseAlgorithm,
            _BaseModellerAlgorithm,
            _BaseModelAlgorithm,
            _BaseModellerModelAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    @unit_test
    def test_worker_types(self, model: Mock) -> None:
        """Test worker method."""
        algorithm_factory = ModelEvaluation(model=model)
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

    @unit_test
    def test_attribute_error_raised(self) -> None:
        """Test non abstract class without run method raises AttributeError."""
        err_msg = "does not have a run method"
        for type_ in [
            _BaseWorkerAlgorithm,
            _BaseWorkerModelAlgorithm,
        ]:
            with pytest.raises(AttributeError) as e_info:

                class NoRunMethod(type_):  # type: ignore[valid-type, misc] # reason: test child methods need run method # noqa: B950
                    pass

            assert err_msg in str(e_info)

    @unit_test
    def test_worker_run(self, mocker: MockerFixture, model: Mock) -> None:
        """Tests that worker run does metric calculation."""
        worker = evaluate._WorkerSide(model=model)
        mock_metrics = Mock()
        mocker.patch(
            "bitfount.metrics.MetricCollection.create_from_model", mock_metrics
        )
        worker.run()
        model.evaluate.assert_called_once()
        mock_metrics.assert_called_once()

    @unit_test
    def test_modeller_run(self, model: Mock) -> None:
        """Tests that modeller run returns results."""
        modeller = evaluate._ModellerSide(model=model)
        results = [{"AUC": 0.5}]
        assert results == modeller.run(results=results)


@backend_test
@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for column average algorithm."""

    def test_serialization(self) -> None:
        """Test dump and load for ModelEvaluation."""
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            epochs=2,
        )
        algorithm_factory = ModelEvaluation(model=model)
        dumped = bf_dump(algorithm_factory)
        loaded = bf_load(dumped, _ALGORITHMS)

        assert algorithm_factory.class_name == loaded.class_name
        assert_vars_equal(vars(algorithm_factory.model), vars(loaded.model))


# Static tests for algorithm-protocol compatibility
if TYPE_CHECKING:
    from typing import cast

    from bitfount.federated.protocols.results_only import (
        _ResultsOnlyCompatibleModelAlgoFactory,
        _ResultsOnlyCompatibleModeller,
        _ResultsOnlyDataIncompatibleWorker,
    )
    from bitfount.types import (
        DistributedModelProtocol,
        _DistributedModelTypeOrReference,
    )

    # Check compatible with ResultsOnly
    _algo_factory: _ResultsOnlyCompatibleModelAlgoFactory = ModelEvaluation(
        model=cast(_DistributedModelTypeOrReference, object())
    )
    _modeller_side: _ResultsOnlyCompatibleModeller = _ModellerSide(
        model=cast(DistributedModelProtocol, object())
    )
    _worker_side: _ResultsOnlyDataIncompatibleWorker = _WorkerSide(
        model=cast(DistributedModelProtocol, object())
    )
