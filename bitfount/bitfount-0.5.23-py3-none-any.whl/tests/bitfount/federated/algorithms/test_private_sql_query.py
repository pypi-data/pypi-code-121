"""Tests for the sql query algorithm."""
from copy import deepcopy
import logging
from typing import TYPE_CHECKING
from unittest.mock import Mock, create_autospec

from _pytest.logging import LogCaptureFixture
import numpy as np
import pandas as pd
from pandas.core.dtypes.common import pandas_dtype
from pytest import fixture
from pytest_mock import MockerFixture
import sqlalchemy

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseConnection, DatabaseSource
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import ContinuousRecord
from bitfount.federated.algorithms.base import (
    _BaseAlgorithm,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.algorithms.private_sql_query import (
    PrivateSqlQuery,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.modeller import _Modeller
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.utils import _ALGORITHMS
from bitfount.hub import BitfountHub
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import (
    TABLE_NAME,
    backend_test,
    create_datasource,
    create_schema,
    create_schema_pii,
    unit_test,
)


@fixture
def column_ranges() -> dict:
    """Fixture for the column ranges."""
    return {
        "A": {"lower": 1, "upper": 1000},  # will be int (A-D)
        "B": {"lower": 1, "upper": 1000},
        "C": {"lower": 1, "upper": 1000},
        "D": {"lower": 1, "upper": 1000},
        "E": {"lower": 0, "upper": 1},  # will be float (E-H)
        "F": {"lower": 0, "upper": 1},
        "G": {"lower": 0, "upper": 1},
        "H": {"lower": 0, "upper": 1},
        "I": {},  # will be string (I-L)
        "J": {},
        "K": {},
        "L": {},
        "TARGET": {"lower": 0, "upper": 1},  # will be int
    }


class TestPrivateSqlQuery:
    """Test PrivateSqlQuery algorithm."""

    @fixture
    def datasource(self) -> _BaseSource:
        """Fixture for datasource."""
        return create_datasource(classification=True)

    @fixture
    def column_ranges_multi(self) -> dict:
        """Fixture for the column ranges."""
        return {
            "dummy_data": {
                "name": {"lower": 1, "upper": 5000, "private_id": True},
                "age": {"lower": 1, "upper": 100},
                "weight": {"lower": 1.8, "upper": 230},
                "exercise": {},
            },
            "dummy_data_2": {
                "name": {"lower": 1, "upper": 5000, "private_id": True},
                "height": {"lower": 25, "upper": 230},
            },
        }

    @fixture
    def pod_schema(self) -> BitfountSchema:
        """Fixture for schema."""
        return create_schema(classification=True)

    @fixture
    def pod_schema_pii(self) -> BitfountSchema:
        """Fixture for PII data schema."""
        return create_schema_pii()

    @unit_test
    def test_modeller_types(self, column_ranges: dict) -> None:
        """Test modeller method."""
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        algorithm = algorithm_factory.modeller()
        for type_ in [
            _BaseAlgorithm,
            _BaseModellerAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    @unit_test
    def test_worker_types(self, column_ranges: dict) -> None:
        """Test worker method."""
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        algorithm = algorithm_factory.worker(
            hub=create_autospec(BitfountHub, instance=True)
        )
        for type_ in [
            _BaseAlgorithm,
            _BaseWorkerAlgorithm,
        ]:
            assert isinstance(algorithm, type_)

    @unit_test
    def test_worker_init_datasource(
        self, column_ranges: dict, datasource: _BaseSource
    ) -> None:
        """Test worker init with datasource."""
        kwargs = {"hub": Mock(spec=BitfountHub)}
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
            **kwargs
        )
        algorithm_factory.worker(**kwargs).initialise(
            datasource=datasource,
            pod_identifier="test-pod",
            pod_dp=DPPodConfig(max_epsilon=1, max_target_delta=0.0001),
        )

    @unit_test
    def test_worker_init_missingargs(
        self, column_ranges: dict, datasource: _BaseSource
    ) -> None:
        """Test worker init without all arguments."""
        kwargs = {"hub": Mock(spec=BitfountHub)}
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
            **kwargs
        )
        algorithm_factory.worker(**kwargs).initialise(datasource=datasource)

    @unit_test
    def test_modeller_init(self, column_ranges: dict) -> None:
        """Test modeller init method."""
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        algorithm_factory.modeller().initialise()

    @unit_test
    def test_bad_sql_no_table(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: _BaseSource,
        mocker: MockerFixture,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test that having bad SQL query raises an error."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        algorithm_factory = PrivateSqlQuery(
            query="SELECT MAX(G) AS MAX_OF_G",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()
        assert "Error executing PrivateSQL query" in caplog.text

    @unit_test
    def test_no_pod_identifier(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: _BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test that having no pod identifier raises error."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = None
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()
        assert "No pod identifier - cannot get schema" in caplog.text

    @unit_test
    def test_bad_sql_query_statement(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: _BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test that a bad operator in SQL query errors out."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        algorithm_factory = PrivateSqlQuery(
            query="SELECTOR MAX(G) AS MAX_OF_G from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()
        assert "Error executing PrivateSQL query" in caplog.text

    @unit_test
    def test_bad_sql_query_column(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: _BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test that an invalid column in SQL query errors out."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        algorithm_factory = PrivateSqlQuery(
            query="SELECT MAX(BITFOUNT_TEST) AS MAX_OF_BITFOUNT_TEST from df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()
        assert "Error executing PrivateSQL query:" in caplog.text

    @unit_test
    def test_worker_gets_sql_results(
        self, column_ranges: dict, datasource: _BaseSource, pod_schema: BitfountSchema
    ) -> None:
        """Test that a SQL query returns correct result."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        results = worker.run()

        assert results is not None
        assert len(results) > 0
        # The result should not be the same as the true value
        assert float(results[1][0]) != 0.500129

    @unit_test
    def test_sql_algorithm_db_connection_multitable_onetable(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
    ) -> None:
        """Test sql algorithm on mulitable db connection, check ranges."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}

        db_src = DatabaseSource(
            DatabaseConnection(
                db_session_pii, table_names=["dummy_data", "dummy_data_2"]
            )
        )
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(age) as avg_adult FROM public.dummy_data where age > 17;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = db_src
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        results = worker.run()

        # Check output has the currect form
        assert results is not None
        assert len(results) > 0
        assert len(results) == 2

        # Check the results are as expected (name and within range)
        assert results[0][0] == "avg_adult"
        assert float(results[1][0]) <= 100
        assert float(results[1][0]) >= 1

    @unit_test
    def test_sql_algorithm_db_connection_test_float(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
    ) -> None:
        """Test sql algorithm on mulitable db connection, check float result."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        # Create column metadata without ranges to test defaults
        column_ranges_multi_nobounds = column_ranges_multi
        column_ranges_multi_nobounds["dummy_data_2"]["height"] = {}

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi_nobounds,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        results = worker.run()

        # Check output has the currect form
        assert results is not None
        assert len(results) > 0
        assert len(results) == 2

        # Check the results are as expected (name and within range)
        assert results[0][0] == "avg_height"
        # There is a very small proabibility these tests will fail
        assert float(results[1][0]) <= 4
        assert float(results[1][0]) >= -4

    @unit_test
    def test_sql_algorithm_db_connection_test_colnotthere(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test fallback for column not in data schema."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        # Create column metadata without ranges to test defaults
        column_ranges_multi_nobounds = column_ranges_multi
        column_ranges_multi_nobounds["dummy_data_2"]["dynamic"] = {}

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi_nobounds,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()
        assert "proceed assuming it is a string" in caplog.text

    @unit_test
    def test_sql_algorithm_db_connection_test_tabnotthere(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test query fails if table in metadata not in pod data."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        # Create column metadata without ranges to test defaults
        column_ranges_multi_nobounds = column_ranges_multi
        column_ranges_multi_nobounds["dummy_data_3"] = {"dynamic": {}}

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi_nobounds,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()
        assert "SQL query will probably fail" in caplog.text

    @unit_test
    def test_sql_algorithm_db_connection_test_incompletemeta(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test the code which auto-completes the metadata if not complete."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        # Create column metadata without ranges to test defaults
        column_ranges_missing_feature = column_ranges_multi
        del column_ranges_missing_feature["dummy_data"]["weight"]

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        ds.load_data()
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_missing_feature,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()
        assert "lower and upper bound of (0,1) for field [weight]" in caplog.text

    @unit_test
    def test_sql_algorithm_db_connection_test_othertypes(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test metadata auto-complete.

        If a column/feature is missing, test that defaults ranges
        are correctly applied.
        """
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        # Create column metadata without ranges to test defaults
        column_ranges_missing_feature = column_ranges_multi
        del column_ranges_missing_feature["dummy_data"]["weight"]

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT avg(height) as avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_missing_feature,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()
        assert "lower and upper bound of (0,1) for field [weight]" in caplog.text

    @unit_test
    def test_sql_algorithm_db_connection_multitable_groupby(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
    ) -> None:
        """Test Group By statement in SQL query ."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        algorithm_factory = PrivateSqlQuery(
            query=(
                "SELECT avg(age) as avg_adult, exercise as e "
                "FROM public.dummy_data where age > 17 "
                "GROUP BY exercise "
                "ORDER BY avg_adult ASC;"
            ),
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        results = worker.run()
        # Check output has the currect form
        assert results is not None
        assert len(results) > 0
        assert len(results) == 12

        # Check the results are as expected (name and within range)
        assert results[0][0] == "avg_adult"
        assert results[0][1] == "e"
        assert float(results[1][0]) <= 100
        for i in range(1, 12):
            assert float(results[i][0]) >= 1
            assert float(results[i][0]) <= 100

    @unit_test
    def test_sql_algorithm_db_connection_multitable_anothertable(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
    ) -> None:
        """Test result of SQL algorithm in different table."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(height) AS avg_height FROM public.dummy_data_2;",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        results = worker.run()

        # Check output has the currect form
        assert results is not None
        assert len(results) > 0
        assert len(results) == 2

        # Check the results are as expected (name and within range)
        assert results[0][0] == "avg_height"
        assert float(results[1][0]) <= 230
        assert float(results[1][0]) >= 25

    @unit_test
    def test_join_sql_query_statement(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test that a JOIN yields an appropriate error."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        algorithm_factory = PrivateSqlQuery(
            query="""
            SELECT 'd1.Date', 'A'
            FROM dummy_data d1
            LEFT JOIN dummy_data_2 d2
            ON 'd1.Date' = 'd2.Date'
            """,
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()

        assert "JOIN clauses are not supported" in caplog.text

    @unit_test
    def test_sql_algorithm_db_connection_multitable_epsilonspent(
        self,
        column_ranges_multi: dict,
        pod_schema_pii: BitfountSchema,
        db_session_pii: sqlalchemy.engine.base.Engine,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test that epsilon is respected with SQL query."""
        # Mock out hub creation
        pod_schema_pii.tables.append(deepcopy(pod_schema_pii.tables[0]))
        pod_schema_pii.tables[0].name = "dummy_data"
        pod_schema_pii.tables[1].name = "dummy_data_2"

        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema_pii
        kwargs = {"hub": mock_hub}
        db_conn = DatabaseConnection(
            db_session_pii, table_names=["dummy_data", "dummy_data_2"]
        )
        ds = DatabaseSource(db_conn, seed=420)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(height) AS avg_height FROM public.dummy_data_2;",
            epsilon=0.4,
            delta=0.00001,
            column_ranges=column_ranges_multi,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = ds
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()

        # Check that we surface an error for exceeding budget
        assert "which is more than the allowed" in caplog.text

    @unit_test
    def test_schema_mapping_unknown_column(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: _BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test failure if feature specified not in pod data."""
        caplog.set_level(logging.INFO)
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Update column ranges to have a column not in the schema
        column_ranges_bad = column_ranges
        column_ranges_bad["Z"] = {"lower": 0, "upper": 1}

        # Run the query
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_bad,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)

        worker.run()

        # Check that both the mapping check, and SQL reader raise errors
        assert "No field named 'Z' present in the schema" in caplog.text
        assert "got error ['Z']" in caplog.text

    @unit_test
    def test_schema_mapping_no_bounds(
        self,
        datasource: _BaseSource,
        column_ranges: dict,
        pod_schema: BitfountSchema,
        caplog: LogCaptureFixture,
    ) -> None:
        """Test backing off to default bound values."""
        caplog.set_level(logging.INFO)
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Update column ranges to have a column not in the schema
        column_ranges_bad = column_ranges
        column_ranges_bad["A"] = {}

        # Run the query
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges_bad,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)
        worker.run()

        assert "Using default lower and upper bound" in caplog.text

    @unit_test
    def test_schema_mapping_unknown_type(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: _BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test schema with unsupported type raises error."""
        caplog.set_level(logging.INFO)

        # Unsupported schema
        pod_schema.get_table_schema(TABLE_NAME).features["continuous"][
            "G"
        ] = ContinuousRecord("G", pandas_dtype("datetime64"))

        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Run the query
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)

        worker.run()

        # Check that both the mapping check, and SQL reader raise errors
        assert "Type datetime64 for column 'G' is not supported" in caplog.text
        assert "must be over numeric or boolean, got string in AVG" in caplog.text

    @unit_test
    def test_modeller_gets_sql_results(
        self, column_ranges: dict, pod_schema: BitfountSchema
    ) -> None:
        """Test SQL query returns a result to modeller."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema

        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        modeller = algorithm_factory.modeller()
        data = {"AVG_OF_G": [0.500129]}
        results = pd.DataFrame(data)
        returned_results = modeller.run(results=[results])
        assert np.isclose(
            returned_results[0].AVG_OF_G[0], results.AVG_OF_G[0], atol=1e-4
        )

    @unit_test
    def test_different_privacy_different_results(
        self, column_ranges: dict, datasource: _BaseSource, pod_schema: BitfountSchema
    ) -> None:
        """Test different DP levels provide different results."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Run query with good privacy (i.e. low epsilon and delta)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=2, max_target_delta=0.001)

        # Run query 10 times, aggregate deviations from truth value
        all_deviations = []
        ground_truth = 0.500129
        for _ in range(10):
            results_good_privacy = worker.run()
            all_deviations.append(
                np.abs(ground_truth - float(results_good_privacy[1][0]))
            )
        mean_deviation_good = np.mean(np.array(all_deviations))

        # Run query with bad privacy (i.e. high epsilon and delta)
        algorithm_factory_bad = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM df.df",
            epsilon=20.0,
            delta=1.0,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory_bad.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=40, max_target_delta=2.0)

        # Run query 10 times, aggregate deviations from truth value
        all_deviations_bad = []
        for _ in range(10):
            results_bad_privacy = worker.run()
            all_deviations_bad.append(
                np.abs(ground_truth - float(results_bad_privacy[1][0]))
            )
        mean_deviation_bad = np.mean(np.array(all_deviations_bad))

        # Check that deviation is higher with more DP noise
        assert mean_deviation_good > mean_deviation_bad

    @unit_test
    def test_different_privacy_applied(
        self, column_ranges: dict, datasource: _BaseSource, pod_schema: BitfountSchema
    ) -> None:
        """Test that DP yields different results over multiple queries."""
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Run query with good privacy (i.e. low epsilon and delta)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT AVG(G) AS AVG_OF_G FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=1, max_target_delta=0.0001)

        # Run query 10 times, ensure results are unique
        all_results = {}
        for _ in range(10):
            results = worker.run()
            result_value = float(results[1][0])
            assert result_value not in all_results
            all_results[result_value] = 1

    @unit_test
    def test_pod_dp_prevails(
        self,
        caplog: LogCaptureFixture,
        column_ranges: dict,
        datasource: _BaseSource,
        pod_schema: BitfountSchema,
    ) -> None:
        """Test Pod DP is preferred over modeller DP."""
        caplog.set_level(logging.INFO)
        # Mock out hub creation
        mock_hub = create_autospec(BitfountHub, instance=True)
        mock_hub.get_pod_schema.return_value = pod_schema
        kwargs = {"hub": mock_hub}

        # Run query with good privacy (i.e. low epsilon and delta)
        algorithm_factory = PrivateSqlQuery(
            query="SELECT SUM(G) AS SUM_OF_G FROM df.df",
            epsilon=3.0,
            delta=0.1,
            column_ranges=column_ranges,
        )
        worker = algorithm_factory.worker(**kwargs)
        worker.datasource = datasource
        worker.pod_identifier = "test-pod"
        worker.pod_dp = DPPodConfig(max_epsilon=2.0, max_target_delta=0.001)

        worker.run()

        assert "Requested DP max epsilon (3.0) exceeds maximum" in caplog.text
        assert "Requested DP target delta (0.1) exceeds maximum" in caplog.text
        assert "The query will cost 4.0 epsilon" in caplog.text
        assert "more than the allowed pod values of 2.0 epsilon" in caplog.text

    @unit_test
    def test_private_sql_execute(
        self, column_ranges: dict, mock_bitfount_session: Mock, mocker: MockerFixture
    ) -> None:
        """Test execute syntactic sugar."""
        query = PrivateSqlQuery(
            query="SELECT * FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        pod_identifiers = ["username/pod-id"]

        mock_modeller_run_method = mocker.patch.object(_Modeller, "run")
        query.execute(pod_identifiers=pod_identifiers)
        mock_modeller_run_method.assert_called_once_with(
            pod_identifiers=pod_identifiers
        )


@backend_test
@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for private sql algorithm."""

    def test_serialization(self, column_ranges: dict) -> None:
        """Test Marshmallow Serialization for private sql algorithm."""
        algorithm_factory = PrivateSqlQuery(
            query="SELECT * FROM df.df",
            epsilon=0.1,
            delta=0.00001,
            column_ranges=column_ranges,
        )
        dumped = bf_dump(algorithm_factory)
        loaded = bf_load(dumped, _ALGORITHMS)
        assert isinstance(loaded, PrivateSqlQuery)
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
    _algo_factory: _ResultsOnlyCompatibleAlgoFactory_ = PrivateSqlQuery(
        query=cast(str, object()),
        epsilon=cast(float, object()),
        delta=cast(float, object()),
        column_ranges=cast(dict, object()),
    )
    _modeller_side: _ResultsOnlyCompatibleModeller = _ModellerSide()
    _worker_side: _ResultsOnlyDataIncompatibleWorker = _WorkerSide(
        query=cast(str, object()),
        epsilon=cast(float, object()),
        delta=cast(float, object()),
        column_ranges=cast(dict, object()),
        hub=cast(BitfountHub, object()),
        table=cast(str, object()),
    )
