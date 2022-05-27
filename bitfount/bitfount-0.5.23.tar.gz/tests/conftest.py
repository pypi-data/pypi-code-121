# +
"""Pytest config and hooks for tests."""
# Import fixtures
import logging
import multiprocessing
import platform
import sys
from typing import Any, Generator, List, Set
from unittest.mock import Mock

# noinspection PyUnresolvedReferences
from _pytest.monkeypatch import MonkeyPatch
import pandas as pd
import psycopg
import pytest

# noinspection PyUnresolvedReferences
from pytest import fixture
from pytest_mock import MockerFixture
import sqlalchemy

from tests.utils.fixtures import *  # noqa: F401, F403
from tests.utils.helper import (
    backend_test,
    create_dataset,
    create_dataset_pii,
    end_to_end_mocks_test,
    end_to_end_test,
    integration_test,
    tutorial_test,
    unit_test,
)

logger = logging.getLogger(__name__)

_REQUIRED_MARKERS: Set[str] = {
    tutorial_test.name,
    end_to_end_mocks_test.name,
    end_to_end_test.name,
    integration_test.name,
    unit_test.name,
}

_BACKEND_PACKAGE_NAME: str = "backends"
_BACKEND_MARKER: str = backend_test.name

_BACKEND_MARK_EXCLUSIONS: Set[str] = set(
    [
        # Add node IDs that should be excluded from requiring the backend_test marker
    ]
)


@fixture(autouse=True, scope="session")
def multiprocessing_start_method() -> None:
    """Sets multiprocessing start method to 'fork' rather than 'spawn'.

    This can only be set once and it has to be before the library is used anywhere which
    is why it must be an autouse session scope fixture.

    Required for Python 3.8 on Macs when using Flask but ensures consistency between
    Unix platforms ("fork" is the default on non-macOS Unix).

    See: https://github.com/pytest-dev/pytest-flask/issues/104
    """
    if sys.platform in ["win32", "win64"]:
        multiprocessing.set_start_method("spawn")
    else:
        multiprocessing.set_start_method("fork")


@fixture(autouse=True, scope="session")
def mac_m1_env_fix(monkeypatch_session_scope: MonkeyPatch) -> None:
    """This empirically fixes errors on this test for Macs with M1 chip.

    Setting the `no_proxy` environment variable disables network proxy lookups. The
    solution was taken from a much older python bug which also fixes this for some
    reason: https://bugs.python.org/issue28342
    """
    if sys.platform == "darwin" and "ARM64" in platform.version():
        logger.info("M1 Mac detected, setting envvar 'no_proxy' to '*'")
        # Checking for 'ARM64'in `platform.version()` appears to be the only way
        # to ensure we find Macs with the M1 chip even when the python interpreter
        # is using Rosetta
        monkeypatch_session_scope.setenv("no_proxy", "*")


@fixture
def mock_pandas_read_sql_query(monkeypatch: MonkeyPatch) -> None:
    """Pandas `read_sql_query()` mocked."""
    data = create_dataset()

    def get_df(**_kwargs: Any) -> pd.DataFrame:
        return data

    monkeypatch.setattr(pd, "read_sql_query", get_df)


@fixture
def mock_inspector(mocker: MockerFixture) -> Generator[Mock, None, None]:
    """Automatically mocks sqlalchemy inspector and yields mocked object."""
    mock_inspector = Mock(
        default_schema_name="public", spec=sqlalchemy.engine.Inspector
    )
    mock_inspector.get_schema_names.return_value = ["public"]
    mock_inspector.get_table_names.return_value = ["dummy_data", "dummy_data_2"]
    mocker.patch("bitfount.data.utils.inspect", return_value=mock_inspector)
    yield mock_inspector


@fixture
def mock_engine(mock_inspector: Mock) -> Generator[Mock, None, None]:
    """Returns mock sqlalchemy engine."""
    yield Mock(spec=sqlalchemy.engine.base.Engine)


@fixture
def db_session(
    postgresql: psycopg.Connection,
) -> Generator[sqlalchemy.engine.base.Engine, None, None]:
    """Creates a dummy postgres database connection.

    This fixture should only be used for integration or end-to-end tests.
    """
    connection = (
        f"postgresql+psycopg2://{postgresql.info.user}:"
        f"@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    )
    engine = sqlalchemy.create_engine(connection)

    df = create_dataset()
    df2 = create_dataset()
    # The tables should never already exist in the database so we set it to fail
    # if it does to catch any potential setup errors.
    df.to_sql("dummy_data", engine, if_exists="fail", index=False)
    df2.to_sql("dummy_data_2", engine, if_exists="fail", index=False)

    yield engine


@fixture
def db_session_pii(
    postgresql: psycopg.Connection,
) -> Generator[sqlalchemy.engine.base.Engine, None, None]:
    """Creates a dummy postgres database connection."""
    connection = (
        f"postgresql+psycopg2://{postgresql.info.user}:"
        f"@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    )
    engine = sqlalchemy.create_engine(connection)

    # Create first table, drop height
    df = create_dataset_pii()
    df.drop("height", inplace=True, axis=1)
    # Create second, different table including height
    df2 = create_dataset_pii()
    df2.drop("age", inplace=True, axis=1)
    df2.drop("weight", inplace=True, axis=1)
    df2.drop("exercise", inplace=True, axis=1)

    # The tables should never already exist in the database so we set it to fail
    # if it does to catch any potential setup errors.
    df.to_sql("dummy_data", index=False, con=engine, if_exists="fail")
    df2.to_sql("dummy_data_2", index=False, con=engine, if_exists="fail")

    yield engine


@pytest.fixture(scope="module")
def monkeypatch_module_scope() -> Generator[MonkeyPatch, None, None]:
    """Module-scoped monkeypatch."""
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def monkeypatch_session_scope() -> Generator[MonkeyPatch, None, None]:
    """Session-scoped monkeypatch."""
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


# Create hook to ensure that all tests are correctly marked
def pytest_collection_modifyitems(items: List[pytest.Item]) -> None:
    """Hooks into the pytest test collection to ensure marker criteria met."""
    no_marks: List[str] = []
    missing_backend_marks: List[str] = []

    for item in items:
        item_id = item.nodeid
        item_markers = set(m.name for m in item.iter_markers())

        # Check each found test has a required mark
        if _REQUIRED_MARKERS.isdisjoint(item_markers):
            no_marks.append(item_id)

        # Check backend tests have backend mark
        if _BACKEND_PACKAGE_NAME in item_id:
            if (
                _BACKEND_MARKER not in item_markers
                and item_id not in _BACKEND_MARK_EXCLUSIONS
            ):
                missing_backend_marks.append(item_id)

        # Add pytest-asyncio marker to all tests;
        # this marker works for both `def` and `async def` defined functions
        # (so has no detrimental effect) but just ensures we have
        # an event loop for things like `asyncio.Lock()`
        # which may appear deep down in the code.
        item.add_marker("asyncio")

    # Error out if any tests were found without marks
    if no_marks:
        no_marks_str = "    " + "\n    ".join(no_marks)
        raise ValueError(
            f"All tests require one of tutorial_test, end_to_end_test, "
            f"end_to_end_mocks_test, integration_test or unit_test as markers; "
            f"some tests have none:\n{no_marks_str}"
        )

    # Error out if any backend tests missing mark
    if missing_backend_marks:
        missing_backend_marks_str = "    " + "\n    ".join(missing_backend_marks)
        raise ValueError(
            f"The following tests may require the backend_test marker; "
            f"add this or mark them as excluded in tests/conftest.py:"
            f"\n{missing_backend_marks_str}"
        )
