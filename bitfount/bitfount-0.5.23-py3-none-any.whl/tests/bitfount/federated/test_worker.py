"""Tests worker.py."""
from typing import Any, Mapping, Union, cast
from unittest.mock import AsyncMock, Mock, PropertyMock, create_autospec

from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
import pandas as pd
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
import sqlalchemy

from bitfount import BitfountSchema, DataStructure
from bitfount.data.datasets import _IterableBitfountDataset
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.intermine_source import IntermineSource
from bitfount.data.datasplitters import PercentageSplitter
from bitfount.data.exceptions import DataStructureError
from bitfount.data.types import DataSplit, SchemaOverrideMapping
from bitfount.data.utils import DatabaseConnection
from bitfount.federated.aggregators.base import _BaseAggregatorFactory
from bitfount.federated.aggregators.base import _registry as aggregator_registry
from bitfount.federated.algorithms.base import _BaseAlgorithmFactory
from bitfount.federated.algorithms.base import _registry as algorithm_registry
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithmFactory,
)
from bitfount.federated.authorisation_checkers import (
    _AuthorisationChecker,
    _LocalAuthorisation,
)
from bitfount.federated.protocols.base import _BaseProtocolFactory
from bitfount.federated.protocols.base import _registry as protocol_registry
from bitfount.federated.protocols.fed_avg import FederatedAveraging
from bitfount.federated.types import (
    SerializedAggregator,
    SerializedAlgorithm,
    SerializedProtocol,
)
from bitfount.federated.utils import _DISTRIBUTED_MODELS
from bitfount.federated.worker import _Worker
from bitfount.types import DistributedModelProtocol, _JSONDict
from tests.utils.helper import (
    create_dataset,
    create_datasource,
    integration_test,
    unit_test,
)


@unit_test
class TestWorker:
    """Tests Worker class."""

    @fixture
    def dummy_protocol(self) -> FederatedAveraging:
        """Returns a FederatedAveraging instance."""
        protocol = Mock(algorithm=Mock(spec=_BaseModelAlgorithmFactory))
        protocol.class_name = "FederatedAveraging"
        protocol.algorithm.class_name = "FederatedModelTraining"
        protocol.aggregator.class_name = "Aggregator"
        protocol.algorithm.model = Mock()
        protocol.algorithm.model.datastructure = create_autospec(DataStructure)
        protocol.algorithm.model.schema = create_autospec(BitfountSchema)
        protocol.worker.return_value = AsyncMock(algorithm=protocol.algorithm)
        return protocol

    @fixture
    def dummy_serializable_protocol(self) -> FederatedAveraging:
        """Returns a serializable FederatedAveraging instance."""
        mock_protocol_factory: Mock = create_autospec(FederatedAveraging, instance=True)
        dump_return_value = {
            "class_name": "bitfount.FederatedAveraging",
            "algorithm": {
                "class_name": "bitfount.FederatedModelTraining",
                "model": {
                    "class_name": "bitfount.PyTorchTabularClassifier",
                    "datastructure": create_autospec(DataStructure),
                    "schema": create_autospec(BitfountSchema),
                },
            },
            "aggregator": {"class_name": "bitfount.Aggregator"},
        }
        mock_protocol_factory.dump.return_value = dump_return_value
        return mock_protocol_factory

    @fixture
    def authoriser(self) -> _AuthorisationChecker:
        """An AuthorisationChecker object.

        An instance of LocalAuthorisation is returned because AuthorisationChecker
        cannot itself be instantiated.
        """
        return _LocalAuthorisation(
            Mock(),
            SerializedProtocol(
                class_name="bitfount.FederatedAveraging",
                algorithm=SerializedAlgorithm(
                    class_name="bitfount.FederatedModelTraining"
                ),
                aggregator=SerializedAggregator(class_name="bitfount.SecureAggregator"),
            ),
        )

    @fixture
    def mock_aggregator_cls_name(self) -> str:
        """Registry name for mock aggregator class."""
        return "mock_aggregator_cls"

    @fixture
    def mock_aggregator_cls_in_registry(
        self, mock_aggregator_cls_name: str, monkeypatch: MonkeyPatch
    ) -> Mock:
        """Places mock aggregator class in relevant registry."""
        mock_aggregator_cls: Mock = create_autospec(_BaseAggregatorFactory)
        # cast() needed as mypy cannot infer type correctly for MonkeyPatch.setitem()
        monkeypatch.setitem(
            aggregator_registry,
            mock_aggregator_cls_name,
            cast(Any, mock_aggregator_cls),
        )
        return mock_aggregator_cls

    @fixture
    def mock_algorithm_cls_name(self) -> str:
        """Registry name for mock algorithm class."""
        return "mock_algorithm_cls"

    @fixture
    def mock_algorithm_cls_in_registry(
        self, mock_algorithm_cls_name: str, monkeypatch: MonkeyPatch
    ) -> Mock:
        """Places mock algorithm class in relevant registry."""
        mock_algorithm_cls: Mock = create_autospec(_BaseAlgorithmFactory)
        # cast() needed as mypy cannot infer type correctly for MonkeyPatch.setitem()
        monkeypatch.setitem(
            algorithm_registry, mock_algorithm_cls_name, cast(Any, mock_algorithm_cls)
        )
        return mock_algorithm_cls

    @fixture
    def mock_model_cls_name(self) -> str:
        """Registry name for mock model class."""
        return "mock_model_cls"

    @fixture
    def mock_model_cls_in_registry(
        self, mock_model_cls_name: str, monkeypatch: MonkeyPatch
    ) -> Mock:
        """Places mock model class in relevant registry."""
        mock_model_cls: Mock = create_autospec(DistributedModelProtocol)
        mock_model_cls.Schema = Mock()
        # cast() needed as mypy cannot infer type correctly for MonkeyPatch.setitem()
        monkeypatch.setitem(
            _DISTRIBUTED_MODELS, mock_model_cls_name, cast(Any, mock_model_cls)
        )
        return mock_model_cls

    @fixture
    def mock_protocol_cls_name(self) -> str:
        """Registry name for mock protocol class."""
        return "mock_protocol_cls"

    @fixture
    def mock_protocol_cls_in_registry(
        self, mock_protocol_cls_name: str, monkeypatch: MonkeyPatch
    ) -> Mock:
        """Places mock protocol class in relevant registry."""
        mock_protocol_cls: Mock = create_autospec(_BaseProtocolFactory)
        # cast() needed as mypy cannot infer type correctly for MonkeyPatch.setitem()
        monkeypatch.setitem(
            protocol_registry, mock_protocol_cls_name, cast(Any, mock_protocol_cls)
        )
        return mock_protocol_cls

    @fixture
    def serialized_protocol_modelless(
        self, mock_algorithm_cls_name: str, mock_protocol_cls_name: str
    ) -> _JSONDict:
        """Serialized protocol dict without model."""
        return {
            "algorithm": {
                "class_name": mock_algorithm_cls_name,
            },
            "class_name": mock_protocol_cls_name,
        }

    @fixture
    def serialized_protocol_with_model(
        self,
        mock_aggregator_cls_name: str,
        mock_algorithm_cls_name: str,
        mock_model_cls_name: str,
        mock_protocol_cls_name: str,
    ) -> _JSONDict:
        """Serialized protocol dict with model (and aggregator)."""
        return {
            "algorithm": {
                "class_name": mock_algorithm_cls_name,
                "model": {"class_name": mock_model_cls_name},
            },
            "aggregator": {"class_name": mock_aggregator_cls_name},
            "class_name": mock_protocol_cls_name,
        }

    @fixture
    def mock_worker(self) -> Mock:
        """Mock Worker instance to use in `self` arg."""
        mock_worker = Mock(spec=_Worker, hub=Mock())
        return mock_worker

    async def test_worker_run_protocol_with_model_loads_datastructure_schema(
        self,
        authoriser: _AuthorisationChecker,
        dummy_protocol: FederatedAveraging,
        dummy_serializable_protocol: FederatedAveraging,
        mocker: MockerFixture,
    ) -> None:
        """Tests that the datastructure and schema are taken from model."""
        mocker.patch.object(
            authoriser, "check_authorisation", return_value=Mock(messages=None)
        )
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        worker = _Worker(
            Mock(),
            AsyncMock(),
            Mock(),
            authoriser,
            pod_identifier="dummy_id",
            serialized_protocol=dummy_serializable_protocol.dump(),
        )
        mock_data = mocker.patch.object(worker, "_load_data_for_worker")
        await worker.run()
        mock_data.assert_called_once_with(
            datastructure=dummy_protocol.algorithm.model.datastructure,
        )

    async def test_worker_run_protocol_without_model_no_datastructure(
        self,
        authoriser: _AuthorisationChecker,
        dummy_protocol: FederatedAveraging,
        dummy_serializable_protocol: FederatedAveraging,
        mocker: MockerFixture,
    ) -> None:
        """Tests that the datastructure and schema are None if no model."""
        dummy_protocol.algorithm = Mock()
        mocker.patch.object(
            authoriser, "check_authorisation", return_value=Mock(messages=None)
        )
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        worker = _Worker(
            Mock(),
            AsyncMock(),
            Mock(),
            authoriser,
            pod_identifier="dummy_id",
            serialized_protocol=dummy_serializable_protocol.dump(),
        )
        mock_data = mocker.patch.object(worker, "_load_data_for_worker")
        await worker.run()
        mock_data.assert_called_once_with(datastructure=None)

    def test__load_data_for_worker(
        self, dummy_protocol: FederatedAveraging, mocker: MockerFixture
    ) -> None:
        """Tests that the worker loads the data."""
        datasource = create_datasource(classification=True)
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        worker = _Worker(
            datasource,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier="dummy_id",
            serialized_protocol=Mock(spec=SerializedProtocol),
        )

        def mock_load_data(self_: _BaseSource, **kwargs: Any) -> None:
            self_._data_is_loaded = True
            self_.data = Mock(spec=pd.DataFrame)

        mocker.patch(
            "bitfount.federated.worker._BaseSource.load_data",
            autospec=True,
            side_effect=mock_load_data,
        )

        # Assert that a datasource is returned is constructed
        worker._load_data_for_worker()
        assert worker.datasource is not None
        assert isinstance(worker.datasource, _BaseSource)

    @pytest.mark.parametrize(
        "sql_query, schema_types_override",
        [
            (
                'SELECT "Date", "TARGET" FROM dummy_data',
                {"categorical": [{"TARGET": {"0": 0, "1": 1}}], "text": ["Date"]},
            ),
            (
                """SELECT d1."Date", d2."A" from dummy_data d1
            JOIN dummy_data_2 d2
            ON d1."Date" = d2."Date"
            """,
                {"continuous": ["A"], "text": ["Date"]},
            ),
        ],
    )
    def test__load_data_for_worker_table_as_query_pod_id(
        self,
        dummy_protocol: FederatedAveraging,
        mock_engine: sqlalchemy.engine.base.Engine,
        mocker: MockerFixture,
        schema_types_override: SchemaOverrideMapping,
        sql_query: str,
    ) -> None:
        """Tests sql query provided by datastructure is applied to datasource."""
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        db_conn = DatabaseConnection(
            mock_engine, table_names=["dummy_data", "dummy_data_2"]
        )
        pod_id = "dummy_pod_id"

        ds = DatabaseSource(db_conn, seed=420)
        datastructure = DataStructure(
            query={pod_id: sql_query},  # dictionary of pod_id to sql query
            schema_types_override={pod_id: schema_types_override},
        )
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        worker._load_data_for_worker(
            datastructure=datastructure,
        )

    @pytest.mark.parametrize(
        "sql_query, schema_types_override",
        [
            (
                'SELECT "Date", "TARGET" FROM dummy_data',
                {"categorical": [{"TARGET": {"0": 0, "1": 1}}], "text": ["Date"]},
            ),
            (
                """SELECT d1."Date", d2."A" from dummy_data d1
            JOIN dummy_data_2 d2
            ON d1."Date" = d2."Date"
            """,
                {"continuous": ["A"], "text": ["Date"]},
            ),
        ],
    )
    def test__load_data_for_worker_table_as_query(
        self,
        dummy_protocol: FederatedAveraging,
        mock_engine: sqlalchemy.engine.base.Engine,
        mocker: MockerFixture,
        schema_types_override: SchemaOverrideMapping,
        sql_query: str,
    ) -> None:
        """Tests sql query provided by datastructure is applied to datasource."""
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        db_conn = DatabaseConnection(
            mock_engine, table_names=["dummy_data", "dummy_data_2"]
        )
        pod_id = "dummy_pod_id"

        ds = DatabaseSource(db_conn, seed=420)
        datastructure = DataStructure(
            query=sql_query,  # standalone sql query
            schema_types_override=schema_types_override,
        )
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        worker._load_data_for_worker(
            datastructure=datastructure,
        )

    @pytest.mark.parametrize("table", ["dummy_data", {"dummy_pod_id": "dummy_data"}])
    def test__load_data_for_worker_single_table(
        self,
        dummy_protocol: FederatedAveraging,
        mock_engine: sqlalchemy.engine.base.Engine,
        mock_pandas_read_sql_query: None,
        mocker: MockerFixture,
        table: Union[dict, str],
    ) -> None:
        """Tests table name provided by datastructure is applied to datasource."""
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        db_conn = DatabaseConnection(mock_engine, table_names=["dummy_data"])
        pod_id = "dummy_pod_id"

        ds = DatabaseSource(db_conn, seed=420)
        datastructure = DataStructure(table=table)
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        worker._load_data_for_worker(
            datastructure=datastructure,
        )

        assert worker.datasource.data is not None
        assert isinstance(worker.datasource.data, pd.DataFrame)

    def test__load_data_for_worker_intermine(self, mocker: MockerFixture) -> None:
        """Tests table name provided by datastructure is applied to datasource."""
        pod_id = "dummy_pod_id"
        table_name = "table_name"
        service_url = "https://fake_url"
        mocker.patch("bitfount.federated.worker.bf_load")
        mock_service = mocker.patch(
            "bitfount.data.datasources.intermine_source.Service"
        )
        ds = IntermineSource(service_url, token=None)
        mocker.patch.object(
            IntermineSource, "table_names", PropertyMock(return_value=[table_name])
        )
        mocker.patch.object(
            IntermineSource, "_template_to_df", return_value=create_dataset()
        )
        datastructure = DataStructure(table=table_name)
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        worker._load_data_for_worker(
            datastructure=datastructure,
        )

        assert worker.datasource.data is not None
        mock_service.assert_called_once_with(service_url, token=None)
        assert isinstance(worker.datasource.data, pd.DataFrame)

    def test__load_data_for_worker_errors_wrong_pod_id_query(
        self,
        dummy_protocol: FederatedAveraging,
        mocker: MockerFixture,
    ) -> None:
        """Test error raised if DataStructure has no map for workers pod id."""
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        sql_query = 'SELECT "Date", "TARGET" FROM dummy_data'
        worker_pod_id = "worker_pod_id"
        query = {"different_pod_id": sql_query}
        schema_override: Mapping[str, SchemaOverrideMapping]
        schema_override = {"different_pod_id": {"text": ["Date", "TARGET"]}}
        ds = create_datasource(classification=True)
        datastructure = DataStructure(
            query=query, schema_types_override=schema_override
        )
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=worker_pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        with pytest.raises(DataStructureError):
            worker._load_data_for_worker(datastructure=datastructure)

    def test__load_data_for_worker_errors_wrong_pod_id_table(
        self,
        dummy_protocol: FederatedAveraging,
        mocker: MockerFixture,
    ) -> None:
        """Test error raised if DataStructure has no map for workers pod id."""
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        worker_pod_id = "worker_pod_id"
        ds_table = {"different_pod_id": "table_name"}
        ds = create_datasource(classification=True)
        datastructure = DataStructure(table=ds_table)
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=worker_pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        with pytest.raises(DataStructureError):
            worker._load_data_for_worker(datastructure=datastructure)

    def test__load_data_for_worker_errors_incompatiable_ds(
        self,
        dummy_protocol: FederatedAveraging,
        mocker: MockerFixture,
    ) -> None:
        """Test error raised with incompatible DataStructure and DatabaseSource.

        If the datastructure table is given as a SQL query but the datasource
        is a dataframe an ValueError should be raised.
        """
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        sql_query = 'SELECT "Date", "TARGET" FROM dummy_data'
        pod_id = "dummy_pod_id"
        schema_override: Mapping[str, SchemaOverrideMapping]
        schema_override = {pod_id: {"continuous": ["a", "b", "c"]}}
        ds = create_datasource(classification=True)
        datastructure = DataStructure(
            query={pod_id: sql_query},
            schema_types_override=schema_override,
        )
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        with pytest.raises(ValueError):
            worker._load_data_for_worker(datastructure=datastructure)

    async def test_worker_adds_hub_instance_to_serialized_bitfount_model_reference(
        self,
        authoriser: _AuthorisationChecker,
        caplog: LogCaptureFixture,
        dummy_protocol: FederatedAveraging,
        dummy_serializable_protocol: FederatedAveraging,
        mocker: MockerFixture,
    ) -> None:
        """Tests that the worker adds hub to serialized bitfount model reference.

        The worker should add the hub instance to the serialized bitfount model
        reference because the hub is not serialized as part of the protocol but is
        required to retrieve the custom model from the hub.
        """
        caplog.set_level("DEBUG")
        mocker.patch.object(
            authoriser, "check_authorisation", return_value=Mock(messages=None)
        )
        mocker.patch("bitfount.federated.worker.bf_load", return_value=dummy_protocol)
        protocol_with_bitfount_model_reference = dummy_serializable_protocol.dump()
        protocol_with_bitfount_model_reference["algorithm"]["model"][
            "class_name"
        ] = "BitfountModelReference"
        worker = _Worker(
            Mock(),
            AsyncMock(),
            Mock(),
            authoriser,
            pod_identifier="dummy_id",
            serialized_protocol=protocol_with_bitfount_model_reference,
        )
        mocker.patch.object(worker, "_load_data_for_worker")
        await worker.run()
        assert "Patching model reference hub." in [i.message for i in caplog.records]


@integration_test
class TestWorkerDatabaseConnection:
    """Tests Worker class with an underlying database connection."""

    @pytest.mark.parametrize(
        "sql_query, schema_types_override",
        [
            (
                'SELECT "Date", "TARGET" FROM dummy_data',
                {"categorical": [{"TARGET": {"0": 0, "1": 1}}], "text": ["Date"]},
            ),
            (
                """SELECT d1."Date", d2."A" from dummy_data d1
            JOIN dummy_data_2 d2
            ON d1."Date" = d2."Date"
            """,
                {"continuous": ["A"], "text": ["Date"]},
            ),
        ],
    )
    def test__load_data_for_worker_table_as_query_pod_id(
        self,
        db_session: sqlalchemy.engine.base.Engine,
        mocker: MockerFixture,
        schema_types_override: SchemaOverrideMapping,
        sql_query: str,
    ) -> None:
        """Tests sql query provided by datastructure is applied to datasource."""
        mocker.patch("bitfount.federated.worker.bf_load")
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )
        pod_id = "dummy_pod_id"
        expected_output = pd.read_sql(sql_query, con=db_conn.con)
        ds = DatabaseSource(db_conn, seed=420, data_splitter=PercentageSplitter(0, 0))
        datastructure = DataStructure(
            query={pod_id: sql_query},  # dictionary of pod_id to sql query
            schema_types_override={pod_id: schema_types_override},
        )
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        worker._load_data_for_worker(
            datastructure=datastructure,
        )

        cumulative_len = 0

        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(ds, Mock(), Mock(), Mock(), Mock())

        for df in dataset.yield_dataset_split(DataSplit.TRAIN):
            assert list(df.columns) == list(expected_output.columns)
            cumulative_len += len(df)

        assert cumulative_len == len(expected_output)

    @pytest.mark.parametrize(
        "sql_query, schema_types_override",
        [
            (
                'SELECT "Date", "TARGET" FROM dummy_data',
                {"categorical": [{"TARGET": {"0": 0, "1": 1}}], "text": ["Date"]},
            ),
            (
                """SELECT d1."Date", d2."A" from dummy_data d1
            JOIN dummy_data_2 d2
            ON d1."Date" = d2."Date"
            """,
                {"continuous": ["A"], "text": ["Date"]},
            ),
        ],
    )
    def test__load_data_for_worker_table_as_query(
        self,
        db_session: sqlalchemy.engine.base.Engine,
        mocker: MockerFixture,
        schema_types_override: SchemaOverrideMapping,
        sql_query: str,
    ) -> None:
        """Tests sql query provided by datastructure is applied to datasource."""
        mocker.patch("bitfount.federated.worker.bf_load")
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )
        pod_id = "dummy_pod_id"
        expected_output = pd.read_sql(sql_query, con=db_conn.con)
        ds = DatabaseSource(db_conn, seed=420, data_splitter=PercentageSplitter(0, 0))
        datastructure = DataStructure(
            query=sql_query,  # standalone sql query
            schema_types_override=schema_types_override,
        )
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        worker._load_data_for_worker(
            datastructure=datastructure,
        )
        cumulative_len = 0

        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(ds, Mock(), Mock(), Mock(), Mock())

        for df in dataset.yield_dataset_split(DataSplit.TRAIN):
            assert list(df.columns) == list(expected_output.columns)
            cumulative_len += len(df)

        assert cumulative_len == len(expected_output)

    @pytest.mark.parametrize("table", ["dummy_data", {"dummy_pod_id": "dummy_data"}])
    def test__load_data_for_worker_single_table(
        self,
        db_session: sqlalchemy.engine.base.Engine,
        mocker: MockerFixture,
        table: Union[dict, str],
    ) -> None:
        """Tests table name provided by datastructure is applied to datasource."""
        mocker.patch("bitfount.federated.worker.bf_load")
        pod_id = "dummy_pod_id"
        db_conn = DatabaseConnection(db_session, table_names=["dummy_data"])
        expected_output = pd.read_sql_table(table_name="dummy_data", con=db_conn.con)
        ds = DatabaseSource(db_conn, seed=420, data_splitter=PercentageSplitter(0, 0))
        datastructure = DataStructure(table=table)
        worker = _Worker(
            ds,
            AsyncMock(),
            Mock(),
            Mock(),
            pod_identifier=pod_id,
            serialized_protocol=Mock(spec=SerializedProtocol),
        )
        worker._load_data_for_worker(
            datastructure=datastructure,
        )

        cumulative_len = 0

        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(ds, Mock(), Mock(), Mock(), Mock())

        for df in dataset.yield_dataset_split(DataSplit.TRAIN):
            assert list(df.columns) == list(expected_output.columns)
            cumulative_len += len(df)

        assert cumulative_len == len(expected_output)
