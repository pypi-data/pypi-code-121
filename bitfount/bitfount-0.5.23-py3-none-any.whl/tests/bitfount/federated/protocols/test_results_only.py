"""Tests for the results only protocol."""
from pathlib import Path
import re
from typing import Callable, cast
from unittest.mock import Mock, create_autospec

import pytest
from pytest import fixture
from pytest_mock import MockerFixture

from bitfount import BitfountSchema, ModelEvaluation, SqlQuery
from bitfount.backends.pytorch.models.models import PyTorchTabularClassifier
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.federated.algorithms.column_avg import ColumnAverage
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.train_and_evaluate import (
    ModelTrainingAndEvaluation,
)
from bitfount.federated.protocols import results_only
import bitfount.federated.protocols.base as protocols
from bitfount.federated.protocols.base import (
    _BaseModellerProtocol,
    _BaseProtocol,
    _BaseWorkerProtocol,
)
from bitfount.federated.protocols.results_only import (
    ResultsOnly,
    _ModellerSide,
    _ResultsOnlyCompatibleAlgoFactory_,
    _ResultsOnlyCompatibleModelAlgoFactory,
    _ResultsOnlyCompatibleModeller,
    _ResultsOnlyDataCompatibleWorker,
    _ResultsOnlyDataIncompatibleWorker,
    _WorkerSide,
)
from bitfount.federated.transport.modeller_transport import _ModellerMailbox
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils import PytestRequest
from tests.utils.helper import backend_test, create_datastructure, unit_test


@unit_test
class TestWorkerSide:
    """Tests worker-side of ResultsOnly."""

    @fixture
    def mock_datasource(self) -> Mock:
        """Mock _BaseSource."""
        mock_datasource: Mock = create_autospec(_BaseSource, instance=True)
        return mock_datasource

    @fixture
    def mock_mailbox(self) -> Mock:
        """Mock WorkerMailbox."""
        mock_mailbox: Mock = create_autospec(_WorkerMailbox, instance=True)
        return mock_mailbox

    @fixture
    def worker_side_factory(self, mock_mailbox: Mock) -> Callable[[Mock], _WorkerSide]:
        """Factory to create WorkerSide instances from mock algorithms."""

        def _create(algo: Mock) -> _WorkerSide:
            return _WorkerSide(
                algorithm=algo,
                mailbox=mock_mailbox,
            )

        return _create

    async def test_run_with_data_algo(
        self,
        mock_datasource: Mock,
        mock_mailbox: Mock,
        worker_side_factory: Callable[[Mock], _WorkerSide],
    ) -> None:
        """Tests WorkerSide.run() with an algorithm needing data."""
        mock_data_algorithm: Mock = create_autospec(
            _ResultsOnlyDataCompatibleWorker, instance=True
        )
        worker_side: _WorkerSide = worker_side_factory(mock_data_algorithm)

        await worker_side.run(mock_datasource)

        mock_data_algorithm.initialise.assert_called_once()
        mock_data_algorithm.run.assert_called_once_with(data=mock_datasource)
        mock_mailbox.send_evaluation_results.assert_awaited_once_with(
            mock_data_algorithm.run.return_value
        )
        mock_mailbox.get_task_complete_update.assert_called_once()

    async def test_run_with_non_data_algo(
        self,
        mock_datasource: Mock,
        mock_mailbox: Mock,
        worker_side_factory: Callable[[Mock], _WorkerSide],
    ) -> None:
        """Tests WorkerSide.run() with an algorithm not needing data."""
        mock_algorithm: Mock = create_autospec(
            _ResultsOnlyDataIncompatibleWorker, instance=True
        )
        worker_side: _WorkerSide = worker_side_factory(mock_algorithm)

        await worker_side.run(mock_datasource)

        mock_algorithm.initialise.assert_called_once()
        mock_algorithm.run.assert_called_once_with()
        mock_mailbox.send_evaluation_results.assert_awaited_once_with(
            mock_algorithm.run.return_value
        )

    async def test_run_with_model_algorithm(
        self,
        mock_datasource: Mock,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        worker_side_factory: Callable[[Mock], _WorkerSide],
    ) -> None:
        """Tests WorkerrSide.run() receives parameters if model algo."""
        mock_algorithm: Mock = create_autospec(_BaseWorkerModelAlgorithm, instance=True)
        mock_algorithm.model = Mock()
        mock_algorithm.run = Mock()
        worker_side: _WorkerSide = worker_side_factory(mock_algorithm)
        mock_receive_parameters = mocker.patch.object(
            worker_side, "_receive_parameters"
        )

        await worker_side.run(mock_datasource)

        mock_receive_parameters.assert_awaited_once()
        mock_algorithm.initialise.assert_called_once()
        mock_algorithm.run.assert_called_once()
        mock_mailbox.send_evaluation_results.assert_awaited_once_with(
            mock_algorithm.run.return_value
        )

    async def test_receive_parameters(
        self,
        mock_datasource: Mock,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        worker_side_factory: Callable[[Mock], _WorkerSide],
    ) -> None:
        """Test _receive_parameters awaits _get_model_parameters."""
        mock_algorithm: Mock = create_autospec(
            _ResultsOnlyDataIncompatibleWorker, instance=True
        )
        mock_get_model_parameters = mocker.patch(
            "bitfount.federated.protocols.results_only._get_model_parameters"
        )
        worker_side: _WorkerSide = worker_side_factory(mock_algorithm)

        await worker_side._receive_parameters()

        mock_get_model_parameters.assert_awaited_once_with(mock_mailbox)


@unit_test
class TestModellerSide:
    """Tests modeller-side of ResultsOnly."""

    @fixture
    def mock_datasource(self) -> Mock:
        """Mock DataSource."""
        mock_datasource: Mock = create_autospec(_BaseSource, instance=True)
        return mock_datasource

    @fixture
    def mock_mailbox(self) -> Mock:
        """Mock ModellerMailbox."""
        mock_mailbox: Mock = create_autospec(_ModellerMailbox, instance=True)
        return mock_mailbox

    @fixture
    def modeller_side_factory(
        self, mock_mailbox: Mock
    ) -> Callable[[Mock], _ModellerSide]:
        """Factory to create ModellerSide instances from mock algorithms."""

        def _create(algo: Mock) -> _ModellerSide:
            return _ModellerSide(
                algorithm=algo,
                mailbox=mock_mailbox,
            )

        return _create

    async def test_run(
        self,
        mock_mailbox: Mock,
        modeller_side_factory: Callable[[Mock], _ModellerSide],
    ) -> None:
        """Tests ModellerSide.run() with an algorithm not needing data."""
        mock_algorithm: Mock = create_autospec(
            _ResultsOnlyCompatibleModeller, instance=True
        )
        modeller_side: _ModellerSide = modeller_side_factory(mock_algorithm)

        await modeller_side.run()

        mock_algorithm.initialise.assert_called_once()
        mock_algorithm.run.assert_called_once()
        mock_mailbox.get_evaluation_results_from_workers.assert_awaited_once()

    async def test_run_with_model_algorithm(
        self,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        modeller_side_factory: Callable[[Mock], _ModellerSide],
    ) -> None:
        """Tests ModellerSide.run() sends parameters if model algo."""
        mock_algorithm: Mock = create_autospec(
            _BaseModellerModelAlgorithm, instance=True
        )
        mock_algorithm.model = Mock()
        mock_algorithm.run = Mock()
        modeller_side: _ModellerSide = modeller_side_factory(mock_algorithm)
        mock_send_parameters = mocker.patch.object(modeller_side, "_send_parameters")

        await modeller_side.run()

        mock_send_parameters.assert_awaited_once()
        mock_algorithm.initialise.assert_called_once()
        mock_algorithm.run.assert_called_once()
        mock_mailbox.get_evaluation_results_from_workers.assert_awaited_once()

    async def test_send_parameters(
        self,
        mock_mailbox: Mock,
        mocker: MockerFixture,
        modeller_side_factory: Callable[[Mock], _ModellerSide],
    ) -> None:
        """Test _receive_parameters awaits _get_model_parameters."""
        mock_algorithm: Mock = create_autospec(
            _ResultsOnlyDataIncompatibleWorker, instance=True
        )
        new_parameters = Mock()
        mock_send_model_parameters = mocker.patch(
            "bitfount.federated.protocols.results_only._send_model_parameters"
        )
        modeller_side: _ModellerSide = modeller_side_factory(mock_algorithm)

        await modeller_side._send_parameters(new_parameters)

        mock_send_model_parameters.assert_awaited_once_with(
            new_parameters, mock_mailbox
        )


@unit_test
class TestResultsOnly:
    """Test Results Only protocol."""

    @fixture(scope="function", params=[None, "/mock/file"])
    def remote_algorithm(self, request: PytestRequest) -> ModelTrainingAndEvaluation:
        """Returns remote algorithm."""
        return ModelTrainingAndEvaluation(model=Mock(), pretrained_file=request.param)

    def test_modeller(
        self, mock_modeller_mailbox: Mock, remote_algorithm: ModelTrainingAndEvaluation
    ) -> None:
        """Test modeller method."""
        protocol_factory = ResultsOnly(algorithm=remote_algorithm)
        protocol = protocol_factory.modeller(mailbox=mock_modeller_mailbox)
        for type_ in [
            _BaseProtocol,
            _BaseModellerProtocol,
            results_only._ModellerSide,
        ]:
            assert isinstance(protocol, type_)

    def test_worker(
        self,
        mock_hub: Mock,
        mock_worker_mailbox: Mock,
        remote_algorithm: ModelTrainingAndEvaluation,
    ) -> None:
        """Test worker method."""
        protocol_factory = ResultsOnly(algorithm=remote_algorithm)
        protocol = protocol_factory.worker(mailbox=mock_worker_mailbox, hub=mock_hub)
        for type_ in [
            _BaseProtocol,
            _BaseWorkerProtocol,
            results_only._WorkerSide,
        ]:
            assert isinstance(protocol, type_)

    def test__validate_algorithm_accepts(self) -> None:
        """Tests _validate_algorithm accepts compatible."""
        # Test with ResultsOnlyCompatibleAlgoFactory
        mock_algorithm: Mock = create_autospec(
            _ResultsOnlyCompatibleAlgoFactory_, instance=True
        )
        ResultsOnly._validate_algorithm(mock_algorithm)

        # Test with ResultsOnlyCompatibleModelAlgoFactory
        mock_algorithm = create_autospec(
            _ResultsOnlyCompatibleModelAlgoFactory, instance=True
        )
        ResultsOnly._validate_algorithm(mock_algorithm)

    def test__validate_algorithm_rejects(self) -> None:
        """Tests _validate_algorithm rejects incompatible."""
        mock_algorithm: Mock = Mock(spec_set=["__name__"])
        with pytest.raises(
            TypeError,
            match=re.escape(
                f"The {ResultsOnly.__name__} protocol does not "
                f"support the {type(mock_algorithm).__name__} algorithm."
            ),
        ):
            ResultsOnly._validate_algorithm(mock_algorithm)

    @unit_test
    def test_run_protocol(self, mocker: MockerFixture) -> None:
        """Tests we can run a protocol."""
        algorithm = ColumnAverage(field="TARGET", table_name="fake")
        # Mock out Modeller creation
        mock_modeller = mocker.patch(
            "bitfount.federated.protocols.base._Modeller", autospec=True
        )
        mock_modeller.return_value = mock_modeller  # for __init__
        mock_modeller.run.return_value = None

        protocol = ResultsOnly(algorithm=algorithm)
        protocol.run(
            pod_identifiers=["fake/fake"],
            hub=Mock(),
            message_service=Mock(),
            private_key_or_file=Path("fake.pem"),
        )

        mock_modeller.run.assert_called_once_with(["fake/fake"])

    @unit_test
    def test_run_protocol_idp_is_set(self, mocker: MockerFixture) -> None:
        """Tests that the idp url gets initialized."""
        algorithm = ColumnAverage(field="TARGET", table_name="fake")

        # Mock out Modeller creation
        mock_modeller = mocker.patch(
            "bitfount.federated.protocols.base._Modeller", autospec=True
        )
        mock_modeller.return_value = mock_modeller  # for __init__
        mock_modeller.run.return_value = None
        mock_idp_url = mocker.patch(
            "bitfount.federated.protocols.base._get_idp_url",
            return_value="https://idp-url.unit-test.bitfount.com",
        )

        protocol = ResultsOnly(algorithm=algorithm)
        protocol.run(
            pod_identifiers=["fake/fake"],
            hub=Mock(),
            message_service=Mock(),
            private_key_or_file=Path("fake.pem"),
        )

        mock_idp_url.assert_called_once()


@backend_test
@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for column average algorithm."""

    def test_serialization_model_algorithm(self) -> None:
        """Test Marshmallow Serialization for a model algorithm."""
        model = PyTorchTabularClassifier(
            datastructure=create_datastructure(),
            schema=BitfountSchema(),
            epochs=2,
        )
        algorithm_factory = ModelEvaluation(model=model)
        results_only = ResultsOnly(algorithm=algorithm_factory)
        dumped = bf_dump(results_only)
        loaded = bf_load(dumped, protocols.registry)
        assert results_only.class_name == loaded.class_name
        from tests.bitfount.backends.pytorch.models.test_models import assert_vars_equal

        assert_vars_equal(
            vars(
                cast(
                    _ResultsOnlyCompatibleModelAlgoFactory, results_only.algorithm
                ).model
            ),
            vars(loaded.algorithm.model),
        )

    def test_serialization_sql_algorithm(self) -> None:
        """Test Marshmallow Serialization for sql query algorithm."""
        algorithm_factory = SqlQuery(query="SELECT * FROM df")
        results_only = ResultsOnly(algorithm=algorithm_factory)
        dumped = bf_dump(results_only)
        loaded = bf_load(dumped, protocols.registry)
        assert results_only.class_name == loaded.class_name
        assert results_only.algorithm.__dict__ == loaded.algorithm.__dict__
