"""Test protocol.py with pytorch backend."""
import copy
from typing import List, Optional, Union, cast
from unittest.mock import AsyncMock, Mock, create_autospec

from _pytest.logging import LogCaptureFixture
import pytest
from pytest import fixture
from pytest_mock import MockerFixture

from bitfount.backends.pytorch.federated.shim import PyTorchBackendTensorShim
from bitfount.backends.pytorch.models.models import PyTorchTabularClassifier
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.federated.aggregators.aggregator import (
    Aggregator,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.aggregators.secure import SecureAggregator
from bitfount.federated.algorithms.model_algorithms import federated_training
from bitfount.federated.algorithms.model_algorithms.federated_training import (
    FederatedModelTraining,
    _BaseModelTrainingMixIn,
)
from bitfount.federated.protocols.fed_avg import (
    FederatedAveraging,
    _FederatedAveragingCompatibleAlgoFactory,
)
from bitfount.federated.secure import SecureShare
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.types import DistributedModelProtocol, _SerializedWeights, _StrAnyDict
from tests.bitfount import TEST_SECURITY_FILES
from tests.utils import PytestRequest
from tests.utils.helper import (
    backend_test,
    create_dataset,
    create_datastructure,
    create_schema,
    unit_test,
)


@fixture
def datasource() -> DataFrameSource:
    """Returns datasource."""
    dataset = create_dataset()
    return DataFrameSource(dataset)


@fixture
def datastructure() -> DataStructure:
    """Fixture for datastructure."""
    return create_datastructure()


@fixture
def schema() -> BitfountSchema:
    """Fixture for schema."""
    return create_schema(classification=True)


@fixture
def aggregator(request: PytestRequest) -> Union[Aggregator, SecureAggregator]:
    """Returns mock aggregator."""
    # request.param denotes whether we should use secure aggregator
    if request.param:
        return SecureAggregator(
            secure_share=SecureShare(),
        )
    return Aggregator()


@fixture
def mock_aggregator() -> Mock:
    """A mock that implements the aggregator (factory) interface."""
    mock_aggregator: Mock = create_autospec(spec=Aggregator, instance=True)

    mock_modeller_side = create_autospec(spec=_ModellerSide, instance=True)
    mock_aggregator.modeller.return_value = mock_modeller_side

    mock_worker_side = create_autospec(spec=_WorkerSide, instance=True)
    mock_aggregator.worker.return_value = mock_worker_side
    # Autospec is not auto setting this as async for some reason, so we do it manually.
    mock_worker_side.run = AsyncMock()

    return mock_aggregator


@fixture
def mock_modeller_mailbox() -> Mock:
    """Returns mock mailbox."""
    mock_mailbox: Mock = create_autospec(_ModellerMailbox, instance=True)
    return mock_mailbox


@fixture
def model(datastructure: DataStructure) -> PyTorchTabularClassifier:
    """Returns distributed model."""
    return PyTorchTabularClassifier(
        datastructure=datastructure, schema=BitfountSchema(), epochs=1
    )


@fixture
def federated_algorithm_with_model(
    model: PyTorchTabularClassifier,
) -> FederatedModelTraining:
    """Returns federated algorithm with embedded distributed model."""
    return FederatedModelTraining(model=model)


@fixture
def federated_algorithm(
    datastructure: DataStructure, request: PytestRequest
) -> FederatedModelTraining:
    """Returns federated algorithm with configurable iterations."""
    epochs, steps = request.param
    schema = create_schema(classification=True)
    return FederatedModelTraining(
        model=PyTorchTabularClassifier(
            datastructure=datastructure,
            schema=schema,
            epochs=epochs,
            steps=steps,
        )
    )


@fixture
def mock_federated_algorithm(request: PytestRequest) -> Mock:
    """Creates a mock that matches the federated algorithm.

    Uses request parameters to set the number of steps/epochs.
    """
    epochs, steps = request.param

    mock_algo_factory: Mock = create_autospec(
        _FederatedAveragingCompatibleAlgoFactory, instance=True
    )

    mock_worker_side: Mock = create_autospec(
        federated_training._WorkerSide, instance=True
    )
    mock_algo_factory.worker.return_value = mock_worker_side

    mock_modeller_side = create_autospec(
        federated_training._ModellerSide, instance=True
    )
    mock_algo_factory.modeller.return_value = mock_modeller_side
    mock_modeller_side.epochs = epochs
    mock_modeller_side.steps = steps

    return mock_algo_factory


@fixture
def mock_modeller_run_method(mocker: MockerFixture) -> AsyncMock:
    """Mocks out the Modeller.run() method in protocol.py."""
    mock_run_method: AsyncMock = mocker.patch(
        "bitfount.federated.protocols.base._Modeller.run"
    )
    return mock_run_method


@fixture
def pod_identifiers() -> List[str]:
    """A list of pod identifiers."""
    return ["bitfount/adult", "bitfount/adult2"]


@backend_test
class TestFederatedAveraging:
    """Tests FederatedAveraging protocol with pytorch models."""

    # TODO: [BIT-983] Should these tests mostly be on the main protocol tests
    #       rather than backend? Or should they be @integration_test marked?

    @unit_test
    @pytest.mark.parametrize(
        "federated_algorithm, epochs_between_parameter_updates, steps_between_parameter_updates",  # noqa: B950
        [
            # The first tuple is the (epochs, steps) args for federated_algorithm
            ((3, None), None, 1),
            ((None, 30), 10, None),
            ((None, 30), None, 31),
            ((30, None), 31, None),
        ],
        indirect=["federated_algorithm"],
    )
    @pytest.mark.parametrize("aggregator", [False], indirect=True)
    def test_iterations_incompatible_raises_value_error(
        self,
        aggregator: Union[Aggregator, SecureAggregator],
        epochs_between_parameter_updates: Optional[int],
        federated_algorithm: FederatedModelTraining,
        mock_modeller_mailbox: Mock,
        steps_between_parameter_updates: Optional[int],
    ) -> None:
        """Ensure algorithm steps/epochs is the same as model."""
        with pytest.raises(ValueError):
            protocol_factory = FederatedAveraging(
                algorithm=federated_algorithm,
                aggregator=aggregator,
                steps_between_parameter_updates=steps_between_parameter_updates,
                epochs_between_parameter_updates=epochs_between_parameter_updates,
            )
            protocol = protocol_factory.modeller(mailbox=mock_modeller_mailbox)
            protocol.perform_iterations_checks()

    @unit_test
    @pytest.mark.parametrize(
        "mock_federated_algorithm, epochs_between_parameter_updates, steps_between_parameter_updates, expected_result",  # noqa: B950
        [
            # The first tuple is the (epochs, steps) args for federated_algorithm
            ((10, None), 1, None, 10),
            ((10, None), 3, None, 3),
            ((None, 10), None, 2, 5),
            ((None, 20), None, 7, 2),
        ],
        indirect=["mock_federated_algorithm"],
    )
    def test_get_num_federated_iterations(
        self,
        epochs_between_parameter_updates: Optional[int],
        expected_result: int,
        mock_aggregator: Mock,
        mock_federated_algorithm: FederatedModelTraining,
        mock_modeller_mailbox: Mock,
        steps_between_parameter_updates: Optional[int],
    ) -> None:
        """Assert number of federated iterations is calculated correctly."""
        # TODO: [BIT-983] This should probably be a test on protocol, rather than on the
        #       backend, as it's testing core functionality.
        protocol_factory = FederatedAveraging(
            algorithm=mock_federated_algorithm,
            aggregator=mock_aggregator,
            steps_between_parameter_updates=steps_between_parameter_updates,
            epochs_between_parameter_updates=epochs_between_parameter_updates,
        )
        protocol = protocol_factory.modeller(mailbox=mock_modeller_mailbox)
        assert protocol.get_num_federated_iterations() == expected_result

    @unit_test
    @pytest.mark.parametrize(
        "federated_algorithm, epochs_between_parameter_updates, steps_between_parameter_updates",  # noqa: B950
        [
            # The first tuple is the (epochs, steps) args for federated_algorithm
            ((10, None), 1, None),
            ((10, None), 3, None),
            ((None, 10), None, 2),
            ((None, 20), None, 7),
        ],
        indirect=["federated_algorithm"],
    )
    async def test_worker_model_training_for_appropriate_amount(
        self,
        datasource: DataFrameSource,
        epochs_between_parameter_updates: Optional[int],
        federated_algorithm: FederatedModelTraining,
        mock_aggregator: Mock,
        mocker: MockerFixture,
        schema: BitfountSchema,
        steps_between_parameter_updates: Optional[int],
    ) -> None:
        """Test underlying worker model iterations updated correctly during training."""
        # Create mailbox and mock out relevant functions
        mock_worker_mailbox = create_autospec(_WorkerMailbox, instance=True)
        mock_get_model_updates = mocker.patch(
            "bitfount.federated.protocols.fed_avg._get_model_parameters"
        )
        mock_send_model_updates = mocker.patch(
            "bitfount.federated.protocols.fed_avg._send_parameter_update"
        )
        # Mock out so training complete never returns truthy value prematurely
        mock_worker_mailbox.get_training_iteration_complete_update.return_value = False

        # Create protocol and initialise model
        protocol_factory = FederatedAveraging(
            algorithm=federated_algorithm,
            aggregator=mock_aggregator,
            steps_between_parameter_updates=steps_between_parameter_updates,
            epochs_between_parameter_updates=epochs_between_parameter_updates,
        )
        protocol = protocol_factory.worker(mailbox=mock_worker_mailbox, hub=Mock())
        protocol.algorithm.initialise(datasource=datasource)
        num_federated_iterations = protocol.get_num_federated_iterations()
        expected_total_num_iterations = num_federated_iterations * cast(
            int, steps_between_parameter_updates or epochs_between_parameter_updates
        )

        async def mock_get_model_updates_coroutine(
            _mailbox: _WorkerMailbox,
        ) -> _SerializedWeights:
            """Mock out get_model_parameters."""
            params = cast(
                _BaseModelTrainingMixIn, protocol.algorithm
            ).get_param_states()
            model_params = copy.deepcopy(cast(_StrAnyDict, params))
            for name, param in model_params.items():
                model_params[name] = PyTorchBackendTensorShim.to_list(param)
            return model_params

        mock_get_model_updates.side_effect = mock_get_model_updates_coroutine

        await protocol.run(datasource=datasource)

        # We expect to send and receive updates in each federated iteration (and
        # receive one extra "update" at the very beginning).
        assert mock_send_model_updates.call_count == num_federated_iterations

        # One initial set of parameters and then one per federated iteration
        assert mock_get_model_updates.await_count == num_federated_iterations + 1

        # Check that the iterations are correct, whichever form we're using.
        # If we are using epochs, we can only check that the epoch number is right on
        # the final iteration. If we are using steps, instead we check that the total
        # number of iterations is correct.
        assert isinstance(federated_algorithm.model, DistributedModelProtocol)
        if epochs_between_parameter_updates:
            # The `current_epoch` attribute denotes the epoch number of the epoch
            # about to be trained on the next iteration (starting from 0)
            assert (
                federated_algorithm.model._pl_trainer.current_epoch  # type: ignore[attr-defined] # Reason: Model has _pl_trainer # noqa: B950
                == epochs_between_parameter_updates
            )
        else:
            assert (
                expected_total_num_iterations
                == federated_algorithm.model._total_num_batches_trained
            )

    @unit_test
    def test_helper_run_method_with_algorithm(
        self,
        federated_algorithm_with_model: FederatedModelTraining,
        mock_bitfount_session: Mock,
        mock_modeller_run_method: Mock,
        pod_identifiers: List[str],
    ) -> None:
        """Tests protocol helper run method with algorithm."""
        protocol = FederatedAveraging(algorithm=federated_algorithm_with_model)

        protocol.run(
            pod_identifiers=pod_identifiers,
            private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
        )

        mock_modeller_run_method.assert_called_once_with(pod_identifiers)

    @unit_test
    def test_helper_run_method_with_model(
        self,
        mock_bitfount_session: Mock,
        mock_modeller_run_method: Mock,
        model: PyTorchTabularClassifier,
        pod_identifiers: List[str],
    ) -> None:
        """Tests helper run method with a model."""
        protocol = FederatedAveraging(algorithm=FederatedModelTraining(model=model))
        protocol.run(
            pod_identifiers=pod_identifiers,
            private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
        )

        mock_modeller_run_method.assert_called_once_with(pod_identifiers)

    @unit_test
    def test_helper_run_method_with_model_and_algorithm(
        self,
        caplog: LogCaptureFixture,
        federated_algorithm_with_model: FederatedModelTraining,
        mock_bitfount_session: Mock,
        mock_modeller_run_method: Mock,
        pod_identifiers: List[str],
    ) -> None:
        """Tests helper run method with an algorithm and a model.

        This tests that the run method will still run but that it just issues a warning
        regarding the extra model argument.
        """
        mock_model = Mock()
        protocol = FederatedAveraging(
            model=mock_model, algorithm=federated_algorithm_with_model
        )
        protocol.run(
            pod_identifiers=pod_identifiers,
            private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
        )

        mock_modeller_run_method.assert_called_once_with(pod_identifiers)
        mock_model.assert_not_called()
        mock_model.backend_tensor_shim.assert_not_called()
        assert "Ignoring provided model. Algorithm already has a model." in caplog.text
