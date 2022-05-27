"""Tests for data utils classes and methods."""
import hashlib
import json
from typing import Dict, Generator, Union
from unittest.mock import MagicMock, Mock

import numpy as np
import pandas as pd
from pandas._typing import Dtype
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
import sqlalchemy

from bitfount.data.exceptions import (
    DatabaseMissingTableError,
    DatabaseSchemaNotFoundError,
    DatabaseUnsupportedQueryError,
)
from bitfount.data.helper import convert_epochs_to_steps
from bitfount.data.utils import (
    DatabaseConnection,
    _convert_python_dtypes_to_pandas_dtypes,
    _generate_dtypes_hash,
    _hash_str,
)
from bitfount.types import _Dtypes
from tests.utils.helper import unit_test


@unit_test
def test_convert_epochs_to_steps() -> None:
    """Test converting of epochs to steps is correct."""
    dataloader = MagicMock()
    dataloader.__len__.return_value = 100
    steps = convert_epochs_to_steps(5, dataloader)
    assert steps == 100 * 5


@unit_test
class TestDatabaseConnection:
    """Tests DatabaseConnection class."""

    @fixture
    def mock_engine(self) -> Mock:
        """Returns mock sqlalchemy engine."""
        return Mock(spec=sqlalchemy.engine.base.Engine)

    @fixture(autouse=True)
    def mock_inspector(self, mocker: MockerFixture) -> Generator[Mock, None, None]:
        """Automatically mocks sqlalchemy inspector and yields mocked object."""
        mock_inspector = Mock(
            default_schema_name="public", spec=sqlalchemy.engine.Inspector
        )
        mock_inspector.get_schema_names.return_value = ["public"]
        mock_inspector.get_table_names.return_value = ["test_data"]
        mocker.patch("bitfount.data.utils.inspect", return_value=mock_inspector)
        yield mock_inspector

    def test_create_engine_from_connection_string(self, mocker: MockerFixture) -> None:
        """Tests that a sqlalchemy object can be created from a database URI."""
        mock_create_engine = mocker.patch(
            "bitfount.data.utils.create_engine", autospec=True
        )
        DatabaseConnection(
            "postgresql://localhost:5432/test", query="SELECT * FROM test_data"
        )
        mock_create_engine.assert_called_once_with("postgresql://localhost:5432/test")

    def test_schema_not_found_in_database_raises_value_error(
        self, mock_engine: Mock, mock_inspector: Mock
    ) -> None:
        """Tests that DatabaseSchemaNotFoundError raised if schema not in database."""
        with pytest.raises(DatabaseSchemaNotFoundError):
            DatabaseConnection(mock_engine, db_schema="nonexistent_schema")

        mock_inspector.get_schema_names.assert_called_once()

    def test_query_and_table_names_raises_value_error(self, mock_engine: Mock) -> None:
        """Tests that query and table names can't both be specified."""
        with pytest.raises(ValueError):
            DatabaseConnection(
                mock_engine, query="SELECT * FROM test_data", table_names=["test_data"]
            )

    def test_specified_table_not_found_in_schema_raises_value_error(
        self,
        mock_engine: Mock,
    ) -> None:
        """Tests that DatabaseMissingTableError raised if table not in schema."""
        with pytest.raises(DatabaseMissingTableError):
            DatabaseConnection(mock_engine, table_names=["nonexistent_table"])

    def test_no_tables_found_in_schema_raises_value_error(
        self, mock_engine: Mock, mock_inspector: Mock
    ) -> None:
        """Tests that DatabaseMissingTableError raised if no tables in schema."""
        mock_inspector.get_table_names.return_value = []
        with pytest.raises(DatabaseMissingTableError):
            DatabaseConnection(mock_engine)

    def test_get_default_schema(self, mock_engine: Mock, mock_inspector: Mock) -> None:
        """Tests that default schema is used if none specified."""
        DatabaseConnection(mock_engine)
        mock_inspector.get_table_names.assert_called_once_with(schema="public")

    def test_single_table_name(self, mock_engine: Mock) -> None:
        """Tests that a single table name can be specified."""
        db_conn = DatabaseConnection(mock_engine, table_names=["test_data"])
        assert not db_conn.multi_table

    def test_multiple_table_names(
        self, mock_engine: Mock, mock_inspector: Mock
    ) -> None:
        """Tests that multiple table names can be specified."""
        mock_inspector.get_table_names.return_value = ["test_data", "test_data_2"]
        db_conn = DatabaseConnection(
            mock_engine, table_names=["test_data", "test_data_2"]
        )
        assert db_conn.multi_table

    def test_all_tables_in_schema(
        self, mock_engine: Mock, mock_inspector: Mock
    ) -> None:
        """Tests that connection will default to all tables if none provided."""
        mock_inspector.get_table_names.return_value = [
            "test_data",
            "test_data_2",
            "test_data_3",
        ]
        db_conn = DatabaseConnection(mock_engine)
        assert db_conn.multi_table
        assert db_conn.table_names == ["test_data", "test_data_2", "test_data_3"]

    def test_query(self, mock_engine: Mock) -> None:
        """Tests that query can be specified."""
        db_conn = DatabaseConnection(mock_engine, query="SELECT * FROM test_data")
        assert not db_conn.multi_table
        assert db_conn.query

    def test_into_query_error(self, mock_engine: Mock) -> None:
        """Tests that a query containing into raises error."""
        with pytest.raises(DatabaseUnsupportedQueryError):
            DatabaseConnection(mock_engine, query="SELECT * INTO df")


@unit_test
class TestDataFrameHashing:
    """Tests for generate_dataframe_hash()."""

    @fixture
    def dtypes(self) -> _Dtypes:
        """A test dataframe with data."""
        return {
            "np_test": np.dtype(int),
            "pd_test": pd.core.arrays.integer.Int64Dtype(),
        }

    @fixture
    def dtypes_hash(self) -> str:
        """The expected hash for the dataframe fixture."""
        # The hash is on the DataFrame.dtypes (which returns a Series), so we
        # manually construct the expected matching one.
        dtypes = {
            "np_test": str(np.dtype(int)),
            "pd_test": str(pd.core.arrays.integer.Int64Dtype()),
        }
        str_rep = json.dumps(dtypes, sort_keys=True)
        return hashlib.sha256(str_rep.encode("utf8")).hexdigest()

    @fixture
    def empty_dtypes(self) -> _Dtypes:
        """A test dtype mapping with no data."""
        return {}

    @fixture
    def empty_dtypes_hash(self) -> str:
        """The expected hash of an empty dataframe."""
        # The hash is on the DataFrame.dtypes (which returns a Series), so we
        # manually construct the expected matching one.
        empty_series: Dict = {}
        str_rep: str = str(empty_series)
        return hashlib.sha256(str_rep.encode("utf8")).hexdigest()

    def test_generate_dtypes_hash(self, dtypes: _Dtypes, dtypes_hash: str) -> None:
        """Tests generated hash is expected one for non-empty dataframe."""
        assert _generate_dtypes_hash(dtypes) == dtypes_hash

    def test_generate_dtypes_hash_empty_dataframe(
        self, empty_dtypes: _Dtypes, empty_dtypes_hash: str
    ) -> None:
        """Tests generated hash is expected one for empty dataframe."""
        assert _generate_dtypes_hash(empty_dtypes) == empty_dtypes_hash

    def test_generate_dtypes_hash_same_for_same_dtypes(
        self, dtypes: Dict[str, Union[Dtype, np.dtype]], dtypes_hash: str
    ) -> None:
        """Tests generated hash is consistent for two dataframes with same cols."""
        dtypes_2 = dtypes.copy()

        # Check they are different instances
        assert dtypes is not dtypes_2
        # Check hashes match
        assert (
            _generate_dtypes_hash(dtypes)
            == _generate_dtypes_hash(dtypes_2)
            == dtypes_hash
        )

    def test_generate_dtypes_hash_different_for_different_dtype_dataframes(
        self, dtypes: _Dtypes, dtypes_hash: str
    ) -> None:
        """Tests hash is different for two dataframes with diff col dtypes."""
        # Change the column dtype from int64 to string
        dtypes_2 = {k: np.dtype(str) for k in dtypes.keys()}

        # Check they are different instances
        assert dtypes is not dtypes_2
        # Check hashes differ
        assert (
            _generate_dtypes_hash(dtypes)
            != _generate_dtypes_hash(dtypes_2)
            != dtypes_hash
        )


@unit_test
def test_hash_str() -> None:
    """Tests that hash_str() works."""
    test_string = "Hello, world!"
    expected_hash = "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3"
    assert _hash_str(test_string) == expected_hash


@unit_test
def test_convert_python_dtypes_to_panda_dtypes_error_unsupported_type() -> None:
    """Tests error is raised with unsupported type."""
    with pytest.raises(ValueError):
        _convert_python_dtypes_to_pandas_dtypes(set, "col_name")
