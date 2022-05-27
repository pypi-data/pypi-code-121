"""Tests for the column averaging algorithm."""
from typing import TYPE_CHECKING
from unittest.mock import Mock

import numpy as np
from pytest_mock import MockerFixture

from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.utils import DatabaseConnection
from bitfount.federated.algorithms.base import (
    _BaseAlgorithm,
    _BaseModellerAlgorithm,
    _BaseWorkerAlgorithm,
)
from bitfount.federated.algorithms.column_avg import (
    ColumnAverage,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.utils import _ALGORITHMS
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import create_dataset, unit_test


class TestColumnAverage:
    """Tests ColumnAverage algorithm."""

    @unit_test
    def test_modeller(self) -> None:
        """Tests modeller method."""
        algorithm_factory = ColumnAverage(field="TARGET", table_name="fake")
        algorithm = algorithm_factory.modeller()
        for type_ in [_BaseAlgorithm, _BaseModellerAlgorithm]:
            assert isinstance(algorithm, type_)

    @unit_test
    def test_worker(self) -> None:
        """Tests worker method."""
        algorithm_factory = ColumnAverage(field="TARGET", table_name="fake")
        algorithm = algorithm_factory.worker()
        for type_ in [_BaseAlgorithm, _BaseWorkerAlgorithm]:
            assert isinstance(algorithm, type_)

    @unit_test
    def test_worker_run_single_table_dataframe_datasource(self) -> None:
        """Tests worker run method with a single table datasource."""
        datasource = DataFrameSource(create_dataset())
        algorithm_factory = ColumnAverage(field="TARGET", table_name="doesnt_matter")
        worker = algorithm_factory.worker()
        worker.initialise(datasource=datasource)
        result = worker.run()
        assert isinstance(result, dict)
        assert isinstance(result["mean"], float)

    @unit_test
    def test_worker_run_single_table_database_datasource(
        self, mock_engine: Mock, mocker: MockerFixture
    ) -> None:
        """Tests worker run method with a single table datasource."""
        data = create_dataset()
        db_conn = DatabaseConnection(mock_engine, table_names=["dummy_data"])
        algorithm_factory = ColumnAverage(field="TARGET", table_name="doesnt_matter")
        # Mocks `Session` and resulting context manager
        mock_session = Mock()
        mock_result = Mock()
        mock_session.execute.return_value = mock_result
        mock_result.columns.return_value = [
            (i,) for i in data[algorithm_factory.field].to_list()
        ]
        mocker.patch(
            "bitfount.data.datasources.database_source.Session"
        ).return_value.__enter__.return_value = mock_session

        datasource = DatabaseSource(db_conn)
        worker = algorithm_factory.worker()
        worker.initialise(datasource=datasource)
        result = worker.run()
        assert isinstance(result, dict)
        assert isinstance(result["mean"], float)
        assert result["mean"] == np.mean(data[algorithm_factory.field])


@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for column average algorithm."""

    def test_serialization(self) -> None:
        """Test Marshmallow Serialization for column average algorithm."""
        algorithm_factory = ColumnAverage(field="TARGET", table_name="fake")
        dumped = bf_dump(algorithm_factory)
        loaded = bf_load(dumped, _ALGORITHMS)
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
    _algo_factory: _ResultsOnlyCompatibleAlgoFactory_ = ColumnAverage(
        field=cast(str, object()), table_name=cast(str, object())
    )
    _modeller_side: _ResultsOnlyCompatibleModeller = _ModellerSide()
    _worker_side: _ResultsOnlyDataIncompatibleWorker = _WorkerSide(
        field=cast(str, object()), table_name=cast(str, object())
    )
