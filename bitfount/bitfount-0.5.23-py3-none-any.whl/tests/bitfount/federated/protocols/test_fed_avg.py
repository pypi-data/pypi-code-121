"""Tests for the federated averaging protocol."""
from pathlib import Path
import re
from typing import Dict, Tuple, cast
from unittest import mock
from unittest.mock import ANY, AsyncMock, MagicMock, Mock, create_autospec

from _pytest.logging import LogCaptureFixture
import pytest
from pytest import fixture
from pytest_mock import MockerFixture

from bitfount import BitfountModelReference, BitfountSchema
from bitfount.backends.pytorch import PyTorchTabularClassifier
from bitfount.data.datasources.base_source import _BaseSource
import bitfount.federated.aggregators
import bitfount.federated.aggregators.aggregator
from bitfount.federated.aggregators.aggregator import Aggregator
from bitfount.federated.aggregators.base import _AggregatorWorkerFactory
from bitfount.federated.aggregators.secure import _InterPodAggregatorWorkerFactory
from bitfount.federated.algorithms.model_algorithms import federated_training
from bitfount.federated.algorithms.model_algorithms.federated_training import (
    FederatedModelTraining,
)
from bitfount.federated.helper import _create_aggregator
from bitfount.federated.protocols import fed_avg
import bitfount.federated.protocols.base as protocols
from bitfount.federated.protocols.base import (
    _BaseModellerProtocol,
    _BaseProtocol,
    _BaseProtocolFactory,
    _BaseWorkerProtocol,
)
from bitfount.federated.protocols.fed_avg import (
    FederatedAveraging,
    _FederatedAveragingCompatibleAlgoFactory,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import (
    _InterPodWorkerMailbox,
    _WorkerMailbox,
)
from bitfount.schemas.utils import bf_dump, bf_load
from bitfount.types import _JSONDict
from tests.bitfount.backends.pytorch.models.test_models import assert_vars_equal
from tests.utils import PytestRequest
from tests.utils.helper import backend_test, create_datastructure, unit_test


def mocked_modeller_runner_functions(
    mocker: MockerFixture,
) -> Tuple[Aggregator, AsyncMock, Mock]:
    """Mock functions used in protocol.modeller.run."""
    mocker.patch.object(fed_avg._ModellerSide, "perform_iterations_checks")

    mock_algorithm_run = Mock()
    mocker.patch.object(
        federated_training._ModellerSide,
        "run",
        mock_algorithm_run,
    )

    mocker.patch.object(
        fed_avg._ModellerSide,
        "_send_parameters",
    )

    mocker.patch.object(
        fed_avg._ModellerSide,
        "_receive_parameter_updates",
        return_value=["some params"],
    )

    mocker.patch.object(
        fed_avg._ModellerSide,
        "get_num_federated_iterations",
        return_value=2,
    )

    mock_get_training_metrics = AsyncMock()
    mocker.patch.object(
        fed_avg._ModellerSide,
        "_get_training_metrics_updates",
        mock_get_training_metrics,
    )
    mock_get_training_metrics.return_value = {"AUC": "0.7"}

    mock_aggregator_run = Mock()

    mocker.patch.object(
        bitfount.federated.aggregators.aggregator._ModellerSide,
        "run",
        mock_aggregator_run,
    )
    mock_aggregator_run.return_value = {"some_weight": "some_value"}
    mocked_aggregator_factory = Aggregator()

    mock_task_complete = MagicMock()
    mock_task_complete.return_value.set_result(True)
    mocker.patch.object(
        _ModellerMailbox, "send_training_iteration_complete_update", mock_task_complete
    )
    mocker.patch.object(_ModellerMailbox, "send_task_complete_message")
    return mocked_aggregator_factory, mock_get_training_metrics, mock_algorithm_run


def mocked_worker_runner_functions(
    mocker: MockerFixture,
) -> Tuple[Aggregator, AsyncMock]:
    """Mock functions used in protocol.worker.run."""
    mocker.patch.object(fed_avg._WorkerSide, "perform_iterations_checks")

    mocker.patch.object(
        federated_training._WorkerSide,
        "run",
        return_value=([1, 2, 3], [{"AUC": "0.7"}]),
    )

    mocker.patch.object(
        federated_training._WorkerSide,
        "save_final_parameters",
    )

    mocker.patch.object(
        fed_avg._WorkerSide,
        "get_num_federated_iterations",
        return_value=2,
    )

    mocker.patch.object(
        fed_avg._WorkerSide,
        "_send_parameter_update",
    )
    mock_send_training_metrics = AsyncMock()
    mocker.patch.object(
        fed_avg._WorkerSide,
        "_send_training_metrics",
        mock_send_training_metrics,
    )

    mock_aggregator_run = AsyncMock()

    mocker.patch.object(
        bitfount.federated.aggregators.aggregator._WorkerSide,
        "run",
        mock_aggregator_run,
    )
    mocked_aggregator_factory = Aggregator()

    mock_task_complete = AsyncMock(return_value=True)
    mocker.patch.object(
        _WorkerMailbox, "get_training_iteration_complete_update", mock_task_complete
    )
    mocker.patch.object(_WorkerMailbox, "get_task_complete_update", mock_task_complete)
    return mocked_aggregator_factory, mock_send_training_metrics


class TestFederatedAveraging:
    """Test Federated Averaging protocol."""

    @fixture(scope="function", params=[None, "/mock/file"])
    def federated_algorithm(self, request: PytestRequest) -> FederatedModelTraining:
        """Returns federated algorithm."""
        return FederatedModelTraining(model=Mock(), pretrained_file=request.param)

    @fixture
    def mock_federated_algorithm(self) -> Mock:
        """Returns a mock algorithm compatible with FederatedAveraging."""
        mock_algorithm: Mock = create_autospec(
            _FederatedAveragingCompatibleAlgoFactory, instance=True
        )
        return mock_algorithm

    @fixture
    def mock_aggregator(self) -> Mock:
        """Returns mock aggregator."""
        mock_aggregator: Mock = create_autospec(Aggregator, instance=True)
        return mock_aggregator

    @fixture
    def mocked_modeller_runner_fixture(
        self,
        mocker: MockerFixture,
    ) -> Tuple[Aggregator, AsyncMock, Mock]:
        """Fixture for getting the necessary mocks for modeller protocol runner."""
        return mocked_modeller_runner_functions(mocker)

    @fixture
    def mocked_worker_runner_fixture(
        self, mocker: MockerFixture
    ) -> Tuple[Aggregator, AsyncMock]:
        """Fixture for getting the necessary mocks for worker protocol runner."""
        return mocked_worker_runner_functions(mocker)

    @unit_test
    def test_algorithm_not_compatible_raises_type_error(
        self,
        mock_aggregator: Mock,
    ) -> None:
        """Check that TypeError is raised if algorithm is not compatible."""
        mock_algorithm: Mock = Mock(spec_set=["__name__"])
        with pytest.raises(
            TypeError,
            match=re.escape(
                f"The {FederatedAveraging.__name__} protocol does "
                f"not support the {type(mock_algorithm).__name__} algorithm."
            ),
        ):
            FederatedAveraging(
                algorithm=mock_algorithm,
                aggregator=mock_aggregator,
                steps_between_parameter_updates=2,
            )

    @unit_test
    def test_modeller(
        self,
        federated_algorithm: FederatedModelTraining,
        mock_aggregator: Mock,
        mock_modeller_mailbox: Mock,
    ) -> None:
        """Test modeller method."""
        protocol_factory = FederatedAveraging(
            algorithm=federated_algorithm,
            aggregator=mock_aggregator,
            steps_between_parameter_updates=2,
        )
        protocol = protocol_factory.modeller(mailbox=mock_modeller_mailbox)

        for type_ in [
            _BaseProtocol,
            _BaseModellerProtocol,
            fed_avg._ModellerSide,
        ]:
            assert isinstance(protocol, type_)

    @unit_test
    def test_worker(
        self,
        federated_algorithm: FederatedModelTraining,
        mock_aggregator: Mock,
        mock_hub: Mock,
        mock_worker_mailbox: Mock,
    ) -> None:
        """Test worker method."""
        protocol_factory = FederatedAveraging(
            algorithm=federated_algorithm,
            aggregator=mock_aggregator,
            steps_between_parameter_updates=2,
        )
        protocol = protocol_factory.worker(mailbox=mock_worker_mailbox, hub=mock_hub)

        for type_ in [
            _BaseProtocol,
            _BaseWorkerProtocol,
            fed_avg._WorkerSide,
        ]:
            assert isinstance(protocol, type_)

    @unit_test
    def test_worker_with_different_aggregator_types(
        self,
        mock_federated_algorithm: Mock,
        mock_hub: Mock,
        mock_worker_mailbox: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Test worker method with different aggregator types."""
        # Mock out WorkerSide constructor
        mock_worker_side_cls = mocker.patch(
            "bitfount.federated.protocols.fed_avg._WorkerSide", autospec=True
        )

        # Test with an instance of AggregatorWorkerFactory
        mock_aggregator: Mock = create_autospec(_AggregatorWorkerFactory, instance=True)
        protocol_factory = FederatedAveraging(
            algorithm=mock_federated_algorithm,
            aggregator=mock_aggregator,
            steps_between_parameter_updates=2,
        )
        protocol = protocol_factory.worker(mailbox=mock_worker_mailbox, hub=mock_hub)
        # Check WorkerSide constructed as expected
        assert protocol == mock_worker_side_cls.return_value
        mock_worker_side_cls.assert_called_once_with(
            algorithm=mock_federated_algorithm.worker.return_value,
            aggregator=mock_aggregator.worker.return_value,
            steps_between_parameter_updates=2,
            epochs_between_parameter_updates=None,
            auto_eval=ANY,
            mailbox=mock_worker_mailbox,
        )
        # Check aggregator.worker() called as expected
        mock_aggregator.worker.assert_called_once_with()

        # Test with an instance of InterPodAggregatorWorkerFactory
        mock_worker_side_cls.reset_mock()
        mock_aggregator = create_autospec(
            _InterPodAggregatorWorkerFactory, instance=True
        )
        mock_interpod_worker_mailbox = create_autospec(
            _InterPodWorkerMailbox, instance=True
        )
        protocol_factory = FederatedAveraging(
            algorithm=mock_federated_algorithm,
            aggregator=mock_aggregator,
            steps_between_parameter_updates=2,
        )
        protocol = protocol_factory.worker(
            mailbox=mock_interpod_worker_mailbox, hub=mock_hub
        )
        # Check WorkerSide constructed as expected
        assert protocol == mock_worker_side_cls.return_value
        mock_worker_side_cls.assert_called_once_with(
            algorithm=mock_federated_algorithm.worker.return_value,
            aggregator=mock_aggregator.worker.return_value,
            steps_between_parameter_updates=2,
            epochs_between_parameter_updates=None,
            auto_eval=ANY,
            mailbox=mock_interpod_worker_mailbox,
        )
        # Check aggregator.worker() called as expected
        mock_aggregator.worker.assert_called_once_with(
            mailbox=mock_interpod_worker_mailbox
        )

        # Test with an unknown type of aggregator instance
        mock_aggregator = Mock()
        protocol_factory = FederatedAveraging(
            algorithm=mock_federated_algorithm,
            aggregator=mock_aggregator,
            steps_between_parameter_updates=2,
        )
        with pytest.raises(TypeError, match="Unrecognised aggregator factory"):
            protocol_factory.worker(mailbox=mock_worker_mailbox, hub=mock_hub)

    @unit_test
    def test_helper_run_method_without_algorithm_raises_type_error(
        self,
    ) -> None:
        """Tests helper run method without algorithm raises TypeError."""
        with pytest.raises(TypeError):
            FederatedAveraging()  # type: ignore[call-arg] # Reason: this is what we are testing for # noqa: B950

    @unit_test
    def test_helper_run_method_with_algorithm(
        self, mock_hub: Mock, mocker: MockerFixture
    ) -> None:
        """Tests helper run method with algorithm."""
        federated_algorithm_with_model = FederatedModelTraining(model=Mock())
        mock_run_protocol = mocker.patch.object(_BaseProtocolFactory, "run")
        mock_create_aggregator = mocker.patch(
            "bitfount.federated.protocols.fed_avg._create_aggregator"
        )

        protocol = FederatedAveraging(algorithm=federated_algorithm_with_model)

        protocol.run(
            pod_identifiers=["bitfount/fake", "bitfount/fake2"],
            hub=mock_hub,
            private_key_or_file=Path("fake.testkey"),
        )

        mock_run_protocol.assert_called_once()
        mock_create_aggregator.assert_called()

    @unit_test
    def test_helper_run_method_with_model(
        self, mock_hub: Mock, mocker: MockerFixture
    ) -> None:
        """Tests helper run method with a model."""
        federated_model = Mock()

        mock_run_protocol = mocker.patch.object(_BaseProtocolFactory, "run")
        mock_create_aggregator = mocker.patch(
            "bitfount.federated.protocols.fed_avg._create_aggregator"
        )
        protocol = FederatedAveraging(
            algorithm=FederatedModelTraining(model=federated_model)
        )

        protocol.run(
            pod_identifiers=["bitfount/fake", "bitfount/fake2"],
            hub=mock_hub,
            private_key_or_file=Path("fake.testkey"),
        )

        mock_run_protocol.assert_called_once()
        mock_create_aggregator.assert_called()

    @unit_test
    def test_helper_run_method_with_model_and_algorithm(
        self, caplog: LogCaptureFixture, mock_hub: Mock, mocker: MockerFixture
    ) -> None:
        """Tests helper run method with an algorithm and a model.

        This tests that the run method will still run but that it just issues a warning
        regarding the extra model argument.
        """
        model = Mock()
        federated_algorithm_with_model = FederatedModelTraining(model=Mock())

        mock_run_protocol = mocker.patch.object(_BaseProtocolFactory, "run")
        mock_create_aggregator = mocker.patch(
            "bitfount.federated.protocols.fed_avg._create_aggregator",
        )

        protocol = FederatedAveraging(
            model=model, algorithm=federated_algorithm_with_model
        )
        protocol.run(
            pod_identifiers=["bitfount/fake", "bitfount/fake2"],
            hub=mock_hub,
            private_key_or_file=Path("fake.testkey"),
        )

        mock_run_protocol.assert_called_once()
        mock_create_aggregator.assert_called()

        model.assert_not_called()
        model.backend_tensor_shim.assert_not_called()
        assert (
            caplog.records[0].msg
            == "Ignoring provided model. Algorithm already has a model."
        )

    @unit_test
    async def test_worker_auto_eval_true(
        self,
        federated_algorithm: FederatedModelTraining,
        mock_aggregator: Mock,
        mock_hub: Mock,
        mock_worker_mailbox: Mock,
        mocked_worker_runner_fixture: Tuple[Aggregator, AsyncMock],
    ) -> None:
        """Test worker method, validation metrics sent to modeller."""
        (
            mocked_aggregator_factory,
            mock_send_training_metrics,
        ) = mocked_worker_runner_fixture

        protocol_factory = FederatedAveraging(
            algorithm=federated_algorithm,
            aggregator=mocked_aggregator_factory,
            steps_between_parameter_updates=2,
            auto_eval=True,
        )
        protocol = protocol_factory.worker(mailbox=mock_worker_mailbox, hub=mock_hub)
        await protocol.run(datasource=create_autospec(_BaseSource, instance=True))
        mock_send_training_metrics.assert_called_once()

    @unit_test
    async def test_worker_auto_eval_false(
        self,
        federated_algorithm: FederatedModelTraining,
        mock_aggregator: Mock,
        mock_hub: Mock,
        mock_worker_mailbox: Mock,
        mocked_worker_runner_fixture: Tuple[Aggregator, AsyncMock],
    ) -> None:
        """Test worker method no validation metrics sent."""
        (
            mocked_aggregator_factory,
            mock_send_training_metrics,
        ) = mocked_worker_runner_fixture

        protocol_factory = FederatedAveraging(
            algorithm=federated_algorithm,
            aggregator=mocked_aggregator_factory,
            steps_between_parameter_updates=2,
            auto_eval=False,
        )
        protocol = protocol_factory.worker(mailbox=mock_worker_mailbox, hub=mock_hub)
        await protocol.run(datasource=create_autospec(_BaseSource, instance=True))
        mock_send_training_metrics.assert_not_called()

    @unit_test
    def test_worker_raises_exception_interpod_communication_incorrect(
        self,
        mock_hub: Mock,
        mock_worker_mailbox: Mock,
    ) -> None:
        """Tests exception raised if interpod mailbox needed but not provided."""
        protocol_factory = FederatedAveraging(
            algorithm=Mock(),
            aggregator=create_autospec(_InterPodAggregatorWorkerFactory, instance=True),
        )

        with pytest.raises(
            TypeError,
            match=re.escape(
                "Inter-pod aggregators require an inter-pod worker mailbox."
            ),
        ):
            protocol_factory.worker(mock_worker_mailbox, mock_hub)

    @unit_test
    async def test_modeller_auto_eval_true(
        self,
        federated_algorithm: FederatedModelTraining,
        mock_aggregator: Mock,
        mock_hub: Mock,
        mock_modeller_mailbox: Mock,
        mocked_modeller_runner_fixture: Tuple[Aggregator, AsyncMock, Mock],
    ) -> None:
        """Test worker method no validation metrics sent."""
        (
            mocked_aggregator_factory,
            mock_get_training_metrics,
            mock_algorithm_run,
        ) = mocked_modeller_runner_fixture

        protocol_factory = FederatedAveraging(
            algorithm=federated_algorithm,
            aggregator=mocked_aggregator_factory,
            steps_between_parameter_updates=1,
        )
        protocol = protocol_factory.modeller(
            mailbox=mock_modeller_mailbox, hub=mock_hub
        )
        await protocol.run()
        mock_get_training_metrics.assert_called()
        assert protocol.validation_results == [{"AUC": "0.7"}, {"AUC": "0.7"}]
        algorithm_mock_calls = [
            mock.call(update=None),
            mock.call(
                update={"some_weight": "some_value"}, validation_metrics={"AUC": "0.7"}
            ),
            mock.call(
                update={"some_weight": "some_value"}, validation_metrics={"AUC": "0.7"}
            ),
        ]
        assert mock_algorithm_run.mock_calls == algorithm_mock_calls

    @unit_test
    async def test_modeller_auto_eval_false(
        self,
        federated_algorithm: FederatedModelTraining,
        mock_aggregator: Mock,
        mock_hub: Mock,
        mock_modeller_mailbox: Mock,
        mocked_modeller_runner_fixture: Tuple[Aggregator, AsyncMock, Mock],
    ) -> None:
        """Test worker method no validation metrics sent."""
        (
            mocked_aggregator_factory,
            mock_get_training_metrics,
            mock_algorithm_run,
        ) = mocked_modeller_runner_fixture
        protocol_factory = FederatedAveraging(
            algorithm=federated_algorithm,
            aggregator=mocked_aggregator_factory,
            steps_between_parameter_updates=2,
            auto_eval=False,
        )
        protocol = protocol_factory.modeller(
            mailbox=mock_modeller_mailbox, hub=mock_hub
        )
        await protocol.run()
        mock_get_training_metrics.assert_not_called()
        assert protocol.validation_results == []
        algorithm_mock_calls = [
            mock.call(update=None),
            mock.call(update={"some_weight": "some_value"}),
            mock.call(update={"some_weight": "some_value"}),
        ]
        assert mock_algorithm_run.mock_calls == algorithm_mock_calls

    @unit_test
    @pytest.mark.parametrize(
        "iterations, model_reference",
        [
            ({"epochs": 1, "steps": None}, True),
            ({"epochs": None, "steps": 1}, True),
            ({"epochs": 1, "steps": None}, False),
            ({"epochs": None, "steps": 1}, False),
        ],
    )
    async def test_federated_averaging_protocol_no_iter(
        self, iterations: Dict[str, int], mock_aggregator: Mock, model_reference: bool
    ) -> None:
        """Tests FederatedAveraging with no iteration provided.

        Tests that iterations is set to a default value if no value
        is provided.
        """
        if model_reference:
            model = create_autospec(BitfountModelReference)
            model.hyperparameters = iterations
        else:
            model = Mock(**iterations)
        algorithm = FederatedModelTraining(model=model)

        protocol = FederatedAveraging(
            algorithm=algorithm,
            aggregator=mock_aggregator,
            steps_between_parameter_updates=None,
            epochs_between_parameter_updates=None,
            auto_eval=False,
        )

        if iterations.get("steps"):
            assert protocol.steps_between_parameter_updates == 1
            assert protocol.epochs_between_parameter_updates is None
        else:
            assert protocol.epochs_between_parameter_updates == 1
            assert protocol.steps_between_parameter_updates is None

    @unit_test
    @pytest.mark.parametrize("secure_aggregation", [True, False])
    async def test_federated_averaging_protocol_successfully(
        self, secure_aggregation: bool
    ) -> None:
        """Tests that FederatedAveraging works as expected."""
        model = Mock(epochs=1)

        algorithm = FederatedModelTraining(model=model)

        aggregator = _create_aggregator(secure_aggregation=secure_aggregation)
        protocol = FederatedAveraging(
            algorithm=algorithm,
            aggregator=aggregator,
            steps_between_parameter_updates=None,
            epochs_between_parameter_updates=2,
            auto_eval=False,
        )
        assert isinstance(protocol, FederatedAveraging)
        assert protocol.epochs_between_parameter_updates == 2
        assert protocol.steps_between_parameter_updates is None


@backend_test
@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for FederatedAveraging protocol."""

    def test_serialization_model_algorithm(self) -> None:
        """Test Marshmallow Serialization for FederatedAveraging protocol."""
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            epochs=2,
        )
        algorithm_factory = FederatedModelTraining(model=model)
        fed_avg = FederatedAveraging(
            algorithm=algorithm_factory, aggregator=Aggregator()
        )

        dumped = bf_dump(fed_avg)
        loaded = bf_load(dumped, protocols.registry)

        assert vars(fed_avg).keys() == vars(loaded).keys()
        assert fed_avg.algorithm.class_name == loaded.algorithm.class_name
        assert fed_avg.aggregator.class_name == loaded.aggregator.class_name

        assert_vars_equal(vars(fed_avg.algorithm.model), vars(loaded.algorithm.model))

    def test_serialization_model_algorithm_from_protocol(self) -> None:
        """Test Marshmallow Serialization for FederatedAveraging protocol."""
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            epochs=2,
        )
        algorithm_factory = FederatedModelTraining(model=model)
        fed_avg = FederatedAveraging(
            algorithm=algorithm_factory, aggregator=Aggregator()
        )

        dumped = fed_avg.dump()
        loaded = bf_load(cast(_JSONDict, dumped), protocols.registry)

        assert vars(fed_avg).keys() == vars(loaded).keys()
        assert fed_avg.algorithm.class_name == loaded.algorithm.class_name
        assert fed_avg.aggregator.class_name == loaded.aggregator.class_name

        assert_vars_equal(vars(fed_avg.algorithm.model), vars(loaded.algorithm.model))
