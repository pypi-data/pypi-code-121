"""Tests for the sql query algorithm."""
from typing import TYPE_CHECKING
from unittest.mock import Mock, create_autospec

from _pytest.logging import LogCaptureFixture
import numpy as np
import pandas as pd
from pytest import fixture
from pytest_mock import MockerFixture
import sqlalchemy

from bitfount import DatabaseConnection
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datasources.intermine_source import IntermineSource
from bitfount.federated.algorithms.base import (
    _BaseAlgorithm,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.algorithms.sql_query import SqlQuery, _ModellerSide, _WorkerSide
from bitfount.federated.modeller import _Modeller
from bitfount.federated.utils import _ALGORITHMS
from bitfount.hub import BitfountHub
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import (
    backend_test,
    create_dataset,
    create_datasource,
    unit_test,
)


@unit_test
class TestSqlQuery:
    """Test SqlQuery algorithm."""

    @fixture
    def datasource(self) -> _BaseSource:
        """Fixture for datasource."""
        return create_datasource(classification=True)

    def test_modeller_types(self) -> None:
        """Test modeller method."""
        algorithm_factory = SqlQuery(query="SELECT * from df")
        algorithm = algorithm_factory.modeller()
        for type_ in [
            _BaseAlgorithm,
            _BaseModellerAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    def test_worker_types(self) -> None:
        """Test worker method."""
        algorithm_factory = SqlQuery(query="SELECT * from df")
        algorithm = algorithm_factory.worker(
            hub=create_autospec(BitfountHub, instance=True)
        )
        for type_ in [
            _BaseAlgorithm,
            _BaseWorkerAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    def test_worker_init_datasource(self, datasource: DataFrameSource) -> None:
        """Test worker method."""
        algorithm_factory = SqlQuery(query="SELECT * from df")
        algorithm_factory.worker().initialise(datasource=datasource)

    def test_modeller_init(self) -> None:
        """Test worker method."""
        algorithm_factory = SqlQuery(query="SELECT * from df")
        algorithm_factory.modeller().initialise()

    def test_bad_sql_no_table(
        self, caplog: LogCaptureFixture, datasource: DataFrameSource
    ) -> None:
        """Test that having no data raises an error."""
        algorithm_factory = SqlQuery(query="SELECT MAX(G) AS MAX_OF_G")
        worker = algorithm_factory.worker()
        worker.datasource = datasource
        worker.datasource.load_data()
        worker.run()
        err_msg = (
            "(\"The default table is called 'df'.\", "
            "'Please ensure your SQL query operates on that table.')"
        )
        assert err_msg in caplog.text

    def test_bad_sql_query_statement(
        self, caplog: LogCaptureFixture, datasource: DataFrameSource
    ) -> None:
        """Test that a bad operator in SQL query errors out."""
        algorithm_factory = SqlQuery(query="SELECTOR MAX(G) AS MAX_OF_G FROM df")
        worker = algorithm_factory.worker()
        worker.datasource = datasource
        worker.datasource.load_data()
        worker.run()
        assert "ERROR" in caplog.text

    def test_bad_sql_query_column(
        self, caplog: LogCaptureFixture, datasource: DataFrameSource
    ) -> None:
        """Test that an invalid column in SQL query errors out."""
        algorithm_factory = SqlQuery(
            query="SELECT MAX(BITFOUNT_TEST) AS MAX_OF_BITFOUNT_TEST FROM df"
        )
        worker = algorithm_factory.worker()
        worker.datasource = datasource
        worker.run()
        assert "ERROR" in caplog.text

    def test_bad_sql_no_from_df(
        self, caplog: LogCaptureFixture, datasource: DataFrameSource
    ) -> None:
        """Test that an invalid query errors out."""
        algorithm_factory = SqlQuery(query="mock")
        worker = algorithm_factory.worker()
        worker.datasource = datasource
        worker.run()
        err_msg = (
            "(\"The default table is called 'df'.\", "
            "'Please ensure your SQL query operates on that table.')"
        )
        assert err_msg in caplog.text

    def test_worker_gets_sql_results(self, datasource: DataFrameSource) -> None:
        """Test that a SQL query returns correct result."""
        algorithm_factory = SqlQuery(query="SELECT MAX(G) AS MAX_OF_G FROM df")
        worker = algorithm_factory.worker()
        worker.datasource = datasource
        results = worker.run()
        assert np.isclose(results.MAX_OF_G[0], 0.9997870068530033, atol=1e-4)

    def test_modeller_gets_sql_results(self, datasource: DataFrameSource) -> None:
        """Test that a SQL query returns a result."""
        algorithm_factory = SqlQuery(query="SELECT MAX(G) AS MAX_OF_G FROM df")
        modeller = algorithm_factory.modeller()
        data = {"MAX_OF_G": [0.9997870068530033]}
        results = pd.DataFrame(data)
        returned_results = modeller.run(results=[results])
        assert np.isclose(
            returned_results[0].MAX_OF_G[0], results.MAX_OF_G[0], atol=1e-4
        )

    def test_sql_algorithm_db_connection_multitable(
        self,
        db_session: sqlalchemy.engine.base.Engine,
    ) -> None:
        """Test sql algorithm on mulitable db connection."""
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        algorithm_factory = SqlQuery(
            query='SELECT MAX("A") AS MAX_OF_A FROM dummy_data'
        )
        worker = algorithm_factory.worker()
        worker.datasource = ds
        res = worker.run()
        assert res["max_of_a"] is not None

    def test_sql_output_duplicate_cols_error(
        self,
        caplog: LogCaptureFixture,
        datasource: DataFrameSource,
        mocker: MockerFixture,
    ) -> None:
        """Test that an error is raised if query output has a duplicated column name."""
        algorithm_factory = SqlQuery(query="SELECT * FROM df")
        worker = algorithm_factory.worker()
        dataset = pd.DataFrame({"A": [1], "B": [2]})
        dataset.columns = ["A", "A"]
        worker.datasource = datasource
        mocker.patch("pandasql.sqldf", return_value=dataset)
        worker.run()
        err_msg = "The following column names are duplicated in the output"
        assert err_msg in caplog.text

    def test_sql_execute(
        self, mock_bitfount_session: Mock, mocker: MockerFixture
    ) -> None:
        """Test execute syntactic sugar."""
        query = SqlQuery(query="SELECT * FROM df")
        pod_identifiers = ["username/pod-id"]

        mock_modeller_run_method = mocker.patch.object(_Modeller, "run")
        query.execute(pod_identifiers=pod_identifiers)
        mock_modeller_run_method.assert_called_once_with(
            pod_identifiers=pod_identifiers
        )

    def test_sql_algorithm_intermine(self, mocker: MockerFixture) -> None:
        """Test sql algorithm on Intermine data source."""
        service_url = "https://fake_url"

        mock_service = mocker.patch(
            "bitfount.data.datasources.intermine_source.Service"
        )
        ds = IntermineSource(service_url, token=None)
        mocker.patch.object(ds, "get_data", return_value=create_dataset())
        algorithm_factory = SqlQuery(query="SELECT * FROM df", table="Gene_Protein")
        worker = algorithm_factory.worker()
        worker.datasource = ds
        res = worker.run()

        mock_service.assert_called_once_with(service_url, token=None)
        assert not res.empty


@backend_test
@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for sql query algorithm."""

    def test_serialization(self) -> None:
        """Test Marshmallow Serialization for sql query algorithm."""
        algorithm_factory = SqlQuery(query="SELECT * FROM df")
        dumped = bf_dump(algorithm_factory)
        loaded = bf_load(dumped, _ALGORITHMS)
        assert isinstance(loaded, SqlQuery)
        assert algorithm_factory.__dict__ == loaded.__dict__


# Static tests for algorithm-protocol compatibility
if TYPE_CHECKING:
    from typing import cast

    from bitfount.federated.protocols.results_only import (
        _ResultsOnlyCompatibleAlgoFactory_,
        _ResultsOnlyCompatibleModeller,
        _ResultsOnlyDataIncompatibleWorker,
    )

    # Check compatible with ResultsOnly
    _algo_factory: _ResultsOnlyCompatibleAlgoFactory_ = SqlQuery(
        query=cast(str, object()), pretrained_file=cast(str, object())
    )
    _modeller_side: _ResultsOnlyCompatibleModeller = _ModellerSide()
    _worker_side: _ResultsOnlyDataIncompatibleWorker = _WorkerSide(
        query=cast(str, object()), table=cast(str, object())
    )
