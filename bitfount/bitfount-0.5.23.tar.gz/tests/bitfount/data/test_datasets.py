"""Test dataset classes in data/datasets.py."""
import logging
from typing import Iterator, Optional, Tuple
from unittest.mock import Mock

from PIL import Image
from _pytest.logging import LogCaptureFixture
import numpy as np
import pandas as pd
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
import sqlalchemy

from bitfount.data.datasets import _BitfountDataset, _IterableBitfountDataset
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datasplitters import (
    DatasetSplitter,
    PercentageSplitter,
    SplitterDefinedInData,
)
from bitfount.data.datastructure import DataStructure
from bitfount.data.exceptions import DataNotLoadedError
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import DataSplit, SemanticType
from bitfount.data.utils import DatabaseConnection, _generate_dtypes_hash
from tests.utils.helper import (
    DATASET_ROW_COUNT,
    TABLE_NAME,
    create_dataset,
    integration_test,
    unit_test,
)


@fixture
def tabular_dataframe() -> pd.DataFrame:
    """Underlying dataframe for tabular datasets."""
    return create_dataset()


class FakeSplitter(DatasetSplitter):
    """Fake Splitter that just returns predefined indices."""

    def __init__(
        self,
        train_indices: np.ndarray,
        validation_indices: np.ndarray,
        test_indices: np.ndarray,
    ):
        self.train_indices = train_indices
        self.validation_indices = validation_indices
        self.test_indices = test_indices

    @classmethod
    def splitter_name(cls) -> str:
        """Splitter name for config."""
        return "FakeSplitter"

    def create_dataset_splits(
        self, data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns predefined indices and provided data."""
        return self.train_indices, self.validation_indices, self.test_indices

    def get_split_query(self, datasource: DatabaseSource, split: DataSplit) -> str:
        """Returns query for given split."""
        ...


class TestBaseBitfountDataset:
    """Tests BaseBitfountDataset class."""

    @fixture
    def test_percentage(self) -> int:
        """Test percentage value."""
        return 25

    @fixture
    def validation_percentage(self) -> int:
        """Validation percentage value."""
        return 55

    @fixture
    def train_percentage(self, test_percentage: int, validation_percentage: int) -> int:
        """Train percentage value."""
        return (100 - test_percentage) - validation_percentage

    @fixture
    def target(self) -> str:
        """Target value."""
        return "TARGET"

    @fixture
    def fake_splitter(
        self, test_percentage: int, train_percentage: int, validation_percentage: int
    ) -> FakeSplitter:
        """Fake splitter defined using train/validation/test values."""
        return FakeSplitter(
            np.array(range(int(DATASET_ROW_COUNT * (train_percentage / 100)))),
            np.array(range(int(DATASET_ROW_COUNT * (validation_percentage / 100)))),
            np.array(range(int(DATASET_ROW_COUNT * (test_percentage / 100)))),
        )

    @fixture
    def datastructure(self, target: str) -> DataStructure:
        """Datastructure fixture."""
        return DataStructure(target=target, ignore_cols=["image"], table=TABLE_NAME)

    @unit_test
    def test_transform_image_with_custom_batch_transformation(
        self, image_dataset: _BitfountDataset
    ) -> None:
        """Test transform_image method."""
        assert image_dataset.batch_transforms is not None
        img_array = np.array(Image.new("RGB", size=(224, 224), color=(55, 100, 2)))
        transformed_image = image_dataset._transform_image(img_array.copy(), 0)
        assert isinstance(transformed_image, np.ndarray)
        assert transformed_image.shape == (224, 224, 3)

        # Assert that the transformed image is not the same as the original
        with pytest.raises(AssertionError):
            np.testing.assert_array_equal(img_array, transformed_image)

    @unit_test
    def test_load_image(self, image_dataset: _BitfountDataset) -> None:
        """Test transform_image method."""
        loaded_transformed_image = image_dataset._load_images(0)
        assert isinstance(loaded_transformed_image, np.ndarray)
        assert loaded_transformed_image.shape == (224, 224, 3)

    @unit_test
    def test_apply_schema(
        self, caplog: LogCaptureFixture, tabular_dataset: pd.DataFrame
    ) -> None:
        """Tests data is loaded according to `selected_cols` and schema."""
        assert set(tabular_dataset.data.columns).issubset(
            set(tabular_dataset.selected_cols)
        )
        assert set(tabular_dataset.data.columns).issubset(
            set(tabular_dataset.schema.get_feature_names())
        )

        for record in caplog.records:
            if record.levelname == "WARNING":
                assert (
                    record.message
                    == "Selected columns `I,J,K,L` were not found in the data, continuing without them."  # noqa: B950
                )

    @unit_test
    def test_apply_schema_with_extra_columns(
        self,
        caplog: LogCaptureFixture,
        datastructure: DataStructure,
        tabular_dataframe: pd.DataFrame,
    ) -> None:
        """Tests data is loaded according to `selected_cols` and schema.

        Checks that even if extra columns are provided in the `selected_cols` from the
        DataStructure, they are not used when loading the datasource.
        """
        datasource = DataFrameSource(tabular_dataframe, ignore_cols=["image"])
        datasource.load_data()

        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        datasource.data = datasource.data.drop(
            columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
        )
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        tabular_dataset = _BitfountDataset(
            datasource=datasource,
            selected_cols=datastructure.selected_cols,
            data_split=DataSplit.TRAIN,
            schema=schema.get_table_schema(TABLE_NAME),
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
        )
        assert tabular_dataset.datasource.data is not None

        assert set(tabular_dataset.datasource.data.columns).issubset(
            set(tabular_dataset.selected_cols)
        )
        assert set(tabular_dataset.datasource.data.columns).issubset(
            set(tabular_dataset.schema.get_feature_names())
        )
        assert (
            "Selected columns `I,J,K,L` were not found in the data, continuing without them."  # noqa: B950
            in caplog.text
        )

    @unit_test
    def test_datasource_data_split_called_twice(
        self, caplog: LogCaptureFixture, iter_tabular_dataset: _IterableBitfountDataset
    ) -> None:
        """Tests that the log is printed if split_data called twice."""
        caplog.set_level(logging.DEBUG)

        assert iter_tabular_dataset.datasource._data_is_split is False

        iter_tabular_dataset._split_data()

        assert iter_tabular_dataset.datasource._data_is_split is True
        # split data in DataBunch into training, validation, test sets
        iter_tabular_dataset._split_data()
        assert "Data is already split, keeping the current split." in caplog.text

    @pytest.mark.parametrize(
        "datasplit_type", [DataSplit.TEST, DataSplit.TRAIN, DataSplit.VALIDATION]
    )
    @unit_test
    def test_X_set(
        self,
        dataframe: pd.DataFrame,
        datasplit_type: DataSplit,
        datastructure: DataStructure,
        fake_splitter: FakeSplitter,
        target: str,
        test_percentage: int,
        train_percentage: int,
        validation_percentage: int,
    ) -> None:
        """Checks test/train/validation sets behave correctly."""
        if datasplit_type == DataSplit.TEST:
            datasplit_val = test_percentage
        elif datasplit_type == DataSplit.TRAIN:
            datasplit_val = train_percentage
        elif datasplit_type == DataSplit.VALIDATION:
            datasplit_val = validation_percentage

        datasource = DataFrameSource(dataframe, data_splitter=fake_splitter)
        datasource.load_data()

        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        datasource.data = datasource.data.drop(
            columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
        )

        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _BitfountDataset(
            datasource=datasource,
            target=target,
            selected_cols=datastructure.selected_cols,
            data_split=DataSplit.TRAIN,
            schema=schema.get_table_schema(TABLE_NAME),
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
        )

        dataset._split_data()
        assert dataset.datasource.data is not None
        # assert columns match the original data
        assert (
            dataset.datasource.data.shape[1]
            == dataset.get_dataset_split(datasplit_type).shape[1]
        )
        # assert there are the expected number of rows
        assert (
            int(datasplit_val * dataset.datasource.data.shape[0] / 100)
            == dataset.get_dataset_split(datasplit_type).shape[0]
        )

    @unit_test
    @pytest.mark.parametrize(
        "datasource_splitter, datastructure_splitter",
        [
            (PercentageSplitter(), PercentageSplitter()),
            (PercentageSplitter(), None),
            (None, PercentageSplitter()),
            (None, None),
        ],
    )
    def test_resolve_data_splitter(
        self,
        dataframe: pd.DataFrame,
        datasource_splitter: Optional[DatasetSplitter],
        datastructure_splitter: Optional[DatasetSplitter],
    ) -> None:
        """Checks data splitter is resolved correctly.

        If datasource has a data_splitter, use it to split the data.
        Else if the datastructure has a data_splitter use that splitter.
        Else use the PercentageSplitter.
        """
        datasource = DataFrameSource(dataframe, data_splitter=datasource_splitter)
        datasource.load_data()
        target = "TARGET"

        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        datasource.data = datasource.data.drop(
            columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
        )
        datastructure = DataStructure(
            target=target, ignore_cols=["image"], table=TABLE_NAME
        )
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _IterableBitfountDataset(
            datasource=datasource,
            target=target,
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
            selected_cols=datastructure.selected_cols,
            data_split=DataSplit.TRAIN,
            schema=schema.get_table_schema(TABLE_NAME),
        )
        resolved_splitter = dataset._resolve_data_splitter(datastructure_splitter)
        assert isinstance(resolved_splitter, PercentageSplitter)

        if datasource_splitter:
            assert datasource.data_splitter is not None
            assert resolved_splitter is datasource.data_splitter
            assert resolved_splitter is not datastructure_splitter
        elif datastructure_splitter:
            assert datasource.data_splitter is None
            assert resolved_splitter is datastructure_splitter
        else:
            assert resolved_splitter is not datastructure_splitter
            assert resolved_splitter is not datasource_splitter

    @unit_test
    def test_zero_validation_test_size(
        self, dataframe: pd.DataFrame, target: str
    ) -> None:
        """Checks Dataset object behaves properly when if valid and test pct are 0."""
        datasource = DataFrameSource(
            dataframe,
            data_splitter=FakeSplitter(
                train_indices=np.array(range(DATASET_ROW_COUNT)),
                validation_indices=np.array([]),
                test_indices=np.array([]),
            ),
        )
        datasource.load_data()
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=TABLE_NAME)
        datasource.data = datasource.data.drop(
            columns=schema.get_feature_names(TABLE_NAME, SemanticType.TEXT)
        )
        datastructure = DataStructure(
            target=target, ignore_cols=["image"], table=TABLE_NAME
        )
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _BitfountDataset(
            datasource=datasource,
            target=target,
            selected_cols=datastructure.selected_cols,
            data_split=DataSplit.TRAIN,
            schema=schema.get_table_schema(TABLE_NAME),
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
        )
        assert len(datasource.data) == len(dataset.get_dataset_split(DataSplit.TRAIN))
        assert datasource._test_idxs is not None
        assert datasource._validation_idxs is not None
        assert len(datasource._test_idxs) == 0
        assert len(datasource._validation_idxs) == 0

    @unit_test
    def test_mock_database_query_input(
        self, db_session: Mock, mocker: MockerFixture
    ) -> None:
        """Checks DatabaseSource initialises correctly with `DatabaseConnection`.

        Mock query database connection.
        """
        db_conn = DatabaseConnection(
            db_session,
            query="""
            SELECT 'd1.Date', 'A'
            FROM dummy_data d1
            LEFT JOIN dummy_data_2 d2
            ON 'd1.Date' = 'd2.Date'
            """,
        )
        datasource = DatabaseSource(db_conn, seed=420)
        datasource.load_data()

        mocker.patch.object(_BitfountDataset, "_set_column_name_attributes")
        mocker.patch.object(_BitfountDataset, "_reformat_data")

        db_dataset = _BitfountDataset(
            datasource=datasource,
            data_split=Mock(value="train"),
            schema=Mock(),
            selected_cols=Mock(),
            selected_cols_semantic_types=Mock(),
        )
        db_dataset._split_data()
        assert not datasource.multi_table
        assert datasource.data is not None
        assert datasource._train_idxs is not None
        assert datasource._validation_idxs is not None
        assert datasource._test_idxs is not None
        assert len(datasource._train_idxs) + len(datasource._validation_idxs) + len(
            datasource._test_idxs
        ) == len(datasource.data)

    @unit_test
    def test_training_set_unloaded_raises_error(
        self, mock_engine: Mock, mocker: MockerFixture
    ) -> None:
        """Tests that calling the `training_set` property raises an error.

        The error should be a `DataNotLoadedError` when the data is multi-table because
        it is never loaded.
        """
        target = "TARGET"
        table_name = "dummy_data"
        datastructure = DataStructure(
            target=target, ignore_cols=["image"], table=table_name
        )

        db_conn = DatabaseConnection(
            mock_engine, table_names=["dummy_data", "dummy_data_2"]
        )
        datasource = DatabaseSource(db_conn, seed=420)
        mock_dtypes = {"col": np.dtype(int)}
        mocker.patch.object(datasource, "get_dtypes", return_value=mock_dtypes)
        datasource._table_hashes.add(_generate_dtypes_hash(mock_dtypes))
        datasource.load_data()
        schema = BitfountSchema()
        schema.add_datasource_tables(datasource, table_name=table_name)
        # Using IterableBitfountDataset but get_dataset_split is a
        # concrete method of _BaseBitfountDataset
        db_dataset = _IterableBitfountDataset(
            datasource=datasource,
            target=target,
            selected_cols=datastructure.selected_cols,
            data_split=DataSplit.TRAIN,
            schema=schema.get_table_schema(table_name),
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
        )
        with pytest.raises(DataNotLoadedError):
            db_dataset.get_dataset_split(DataSplit.TRAIN)

    @unit_test
    def test_datasource_data_split_flag_updated(self, dataframe: pd.DataFrame) -> None:
        """Tests that the data_is_split flag is updated."""
        target = "TARGET"
        ds = DataFrameSource(dataframe, selected_cols=["M", "F"])
        ds.load_data()
        assert ds._data_is_split is False

        schema = BitfountSchema()
        schema.add_datasource_tables(ds, table_name=TABLE_NAME)
        datastructure = DataStructure(
            target=target, ignore_cols=["image"], table=TABLE_NAME
        )
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _IterableBitfountDataset(
            datasource=ds,
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
            selected_cols=datastructure.selected_cols,
            data_split=DataSplit.TRAIN,
            schema=schema.get_table_schema(TABLE_NAME),
        )
        dataset._split_data()
        assert ds._data_is_split is True

    @unit_test
    def test_get_dataset_split_length_returns_length_correctly(
        self, dataframe: pd.DataFrame, target: str
    ) -> None:
        """Tests that `get_dataset_split_length` returns the correct length.

        This is done with the `SplitterDefinedInData` splitter.
        """
        dataframe["BITFOUNT_SPLIT_CATEGORY"] = np.random.choice(
            ["TRAIN", "VALIDATE", "TEST"], size=dataframe.shape[0]
        )

        ds = DataFrameSource(dataframe, data_splitter=SplitterDefinedInData())
        ds.load_data()
        schema = BitfountSchema()
        schema.add_datasource_tables(ds, table_name=TABLE_NAME)
        datastructure = DataStructure(
            target=target, ignore_cols=["image"], table=TABLE_NAME
        )
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])
        dataset = _BitfountDataset(
            datasource=ds,
            target=target,
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
            selected_cols=datastructure.selected_cols,
            data_split=DataSplit.TRAIN,
            schema=schema.get_table_schema(TABLE_NAME),
        )
        train_length = dataset.get_dataset_split_length(DataSplit.TRAIN)
        assert train_length == len(
            dataframe.loc[dataframe["BITFOUNT_SPLIT_CATEGORY"] == "TRAIN"]
        )

    @unit_test
    def test_get_dataset_split_length_executes_query(
        self,
        mock_engine: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Tests that `get_dataset_split_length` executes query with database."""
        db_conn = DatabaseConnection(
            mock_engine, table_names=["dummy_data", "dummy_data_2"]
        )
        datasource = DatabaseSource(
            db_conn,
            data_splitter=SplitterDefinedInData(
                column_name='q."M"', training_set_label="True"
            ),
        )
        datasource.load_data(sql_query="SELECT * FROM dummy_data")
        mock_connect = mocker.patch.object(datasource.con, "connect")
        mock_connect.__enter__.return_value = Mock()
        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(datasource, Mock(), Mock(), Mock(), Mock())
        dataset.get_dataset_split_length(DataSplit.TRAIN)

        mock_connect.assert_called_once()

    @integration_test
    def test_get_dataset_split_length_with_multitable_database_connection(
        self,
        dataframe: pd.DataFrame,
        db_session: sqlalchemy.engine.base.Engine,
        mocker: MockerFixture,
    ) -> None:
        """Tests that `get_dataset_split_length` returns the correct length."""
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )
        datasource = DatabaseSource(
            db_conn,
            data_splitter=SplitterDefinedInData(
                column_name='q."M"', training_set_label="True"
            ),
        )
        datasource.load_data(sql_query="SELECT * FROM dummy_data")
        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(datasource, Mock(), Mock(), Mock(), Mock())
        train_length = dataset.get_dataset_split_length(DataSplit.TRAIN)
        assert train_length == len(dataframe.loc[dataframe["M"] == True])  # noqa: E712

    @unit_test
    def test_unable_get_dataset_split_length(
        self, dataframe: pd.DataFrame, fake_splitter: FakeSplitter, target: str
    ) -> None:
        """Test error raise when unable to split dataset."""
        ds = DataFrameSource(dataframe, data_splitter=fake_splitter)
        ds.load_data()

        schema = BitfountSchema()
        schema.add_datasource_tables(ds, table_name=TABLE_NAME)
        datastructure = DataStructure(
            target=target, ignore_cols=["image"], table=TABLE_NAME
        )
        datastructure.set_training_column_split_by_semantic_type(schema.tables[0])

        dataset = _BitfountDataset(
            datasource=ds,
            target=target,
            selected_cols_semantic_types=datastructure.selected_cols_w_types,
            selected_cols=datastructure.selected_cols,
            data_split=DataSplit.TRAIN,
            schema=schema.get_table_schema(TABLE_NAME),
        )
        dataset.datasource._data_is_loaded = False
        with pytest.raises(
            DataNotLoadedError,
            match="Unable to get length of dataset split",
        ):
            dataset.get_dataset_split_length(DataSplit.TRAIN)


@unit_test
class TestBitfountDataset:
    """Tests BitfountDataset class."""

    def test_len_tab_data(self, tabular_dataset: _BitfountDataset) -> None:
        """Tests tabular dataset __len__ method."""
        assert tabular_dataset.datasource._train_idxs is not None
        assert len(tabular_dataset) == len(tabular_dataset.datasource._train_idxs)

    def test_len_img_data(self, image_tab_dataset: _BitfountDataset) -> None:
        """Tests image dataset __len__ method."""
        assert image_tab_dataset.datasource._train_idxs is not None
        assert len(image_tab_dataset) == len(image_tab_dataset.datasource._train_idxs)

    def test_len_img_tab_data(self, image_dataset: _BitfountDataset) -> None:
        """Tests dataset __len__ method."""
        assert image_dataset.datasource._train_idxs is not None
        assert len(image_dataset) == len(image_dataset.datasource._train_idxs)

    def test_len_multiimg_data(self, multiimage_dataset: _BitfountDataset) -> None:
        """Tests multi-image dataset __len__ method."""
        assert multiimage_dataset.datasource._train_idxs is not None
        assert len(multiimage_dataset) == len(multiimage_dataset.datasource._train_idxs)


class TestIterableBitfountDataset:
    """Tests IterableBitfountDataset class."""

    @pytest.mark.parametrize(
        "data_split", [DataSplit.TRAIN, DataSplit.VALIDATION, DataSplit.TEST]
    )
    @pytest.mark.parametrize(
        "validation_percentage,test_percentage", [(0, 0), (10, 10)]
    )
    @unit_test
    def test_len_magic_method(
        self,
        data_split: DataSplit,
        mock_engine: Mock,
        mocker: MockerFixture,
        tabular_dataframe: pd.DataFrame,
        test_percentage: int,
        validation_percentage: int,
    ) -> None:
        """Tests that __len__ magic method returns correct row count."""
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        splitter = PercentageSplitter(
            validation_percentage=validation_percentage,
            test_percentage=test_percentage,
        )
        ds = DatabaseSource(
            db_conn,
            seed=420,
            data_splitter=splitter,
        )
        mock_len = mocker.patch.object(
            DatabaseSource, "__len__", return_value=DATASET_ROW_COUNT
        )

        schema = BitfountSchema(
            datasource=DataFrameSource(tabular_dataframe), table_name="dummy_data"
        )
        dataset = _IterableBitfountDataset(
            datasource=ds,
            selected_cols_semantic_types={
                "continuous": ["columns", "dont", "matter", "here"]
            },
            selected_cols=[],
            schema=schema.tables[0],
            target="TARGET",
            data_split=data_split,
        )

        # Call __len__ method on dataset
        dataset_length = len(dataset)

        mock_len.assert_called_once()

        if data_split == DataSplit.TRAIN:
            assert dataset_length == int(
                DATASET_ROW_COUNT * splitter.train_percentage / 100
            )
        elif data_split == DataSplit.VALIDATION:
            assert dataset_length == int(
                DATASET_ROW_COUNT * splitter.validation_percentage / 100
            )
        elif data_split == DataSplit.TEST:
            assert dataset_length == int(
                DATASET_ROW_COUNT * splitter.test_percentage / 100
            )

    @unit_test
    def test_dataset_len_is_cached(
        self, mock_engine: Mock, mocker: MockerFixture, tabular_dataframe: pd.DataFrame
    ) -> None:
        """Tests that __len__ magic method uses cached length."""
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        splitter = PercentageSplitter()  # default is 80:10:10
        ds = DatabaseSource(
            db_conn,
            seed=420,
            data_splitter=splitter,
        )
        mock_len = mocker.patch.object(
            DatabaseSource, "__len__", return_value=DATASET_ROW_COUNT
        )

        schema = BitfountSchema(
            datasource=DataFrameSource(tabular_dataframe), table_name="dummy_data"
        )
        dataset = _IterableBitfountDataset(
            datasource=ds,
            selected_cols_semantic_types={
                "continuous": ["columns", "dont", "matter", "here"]
            },
            selected_cols=[],
            schema=schema.tables[0],
            target="TARGET",
            data_split=DataSplit.TRAIN,
        )

        # Call __len__ method on dataset TWICE
        dataset_length = len(dataset)
        dataset_length_2 = len(dataset)

        # Make assertion that mock only called ONCE
        mock_len.assert_called_once()

        # Makes assertion on final result
        assert (
            dataset_length
            == dataset_length_2
            == int(DATASET_ROW_COUNT * splitter.train_percentage / 100)
        )

    @unit_test
    def test_iter_magic_method(
        self, mock_engine: Mock, mocker: MockerFixture, tabular_dataframe: pd.DataFrame
    ) -> None:
        """Tests that __iter__ magic method works as expected."""
        ds = DataFrameSource(tabular_dataframe)
        schema = BitfountSchema(
            datasource=ds,
            table_name="dummy_data",
            force_stypes={"dummy_data": {"categorical": ["TARGET"]}},
        )

        class MockBaseSourceIterator:
            """Mock class to represent database result paritions."""

            def __iter__(self) -> Iterator[pd.DataFrame]:
                """Iterator just returns one set of dataframe values."""
                yield tabular_dataframe

        dataset = _IterableBitfountDataset(
            datasource=ds,
            selected_cols_semantic_types={
                "continuous": ["A", "B"],
                "categorical": ["TARGET"],
            },
            selected_cols=["TARGET", "A", "B"],
            schema=schema.tables[0],
            target="TARGET",
            data_split=DataSplit.TRAIN,
        )

        mock_datasource_iterator = MockBaseSourceIterator()
        mocker.patch.object(
            dataset, "yield_dataset_split", return_value=mock_datasource_iterator
        )

        # Call __iter__ method on dataset
        dataset_iterator = iter(dataset)
        row = next(dataset_iterator)  # First output of iterator
        assert isinstance(row, tuple)
        assert isinstance(row[0], tuple)  # x data
        assert isinstance(row[0][0], np.ndarray)  # tabular x data
        assert isinstance(row[0][1], np.ndarray)  # x support columns
        assert isinstance(row[1], np.integer)  # y data

        dataset.yield_dataset_split.assert_called_once()

    @unit_test
    def test_yield_dataset_split_raises_value_error_if_not_database_loader(
        self, iter_tabular_dataset: _IterableBitfountDataset
    ) -> None:
        """Tests that ValueError is raised if loader is not a DatabaseSource."""
        with pytest.raises(
            ValueError,
            match="Iterating over in-memory data is currently not supported.",
        ):
            next(iter_tabular_dataset.yield_dataset_split(DataSplit.TRAIN))

    @unit_test
    def test_yield_dataset_split_raises_value_error_if_no_query_or_table_name_provided(
        self,
        iter_db_dataset: _IterableBitfountDataset,
    ) -> None:
        """Tests that ValueError is raised if no query or table name provided."""
        with pytest.raises(ValueError, match="No query or table name specified."):
            next(iter_db_dataset.yield_dataset_split(DataSplit.TRAIN))

    @integration_test
    def test_validation_set_unsplit_raises_error(
        self, iter_db_dataset: _IterableBitfountDataset
    ) -> None:
        """Tests that calling the `validation_set` property raises an error.

        The error should be a `DataNotLoadedError` when the data is multi-table because
        it is never loaded.
        """
        with pytest.raises(DataNotLoadedError):
            iter_db_dataset.get_dataset_split(DataSplit.VALIDATION)

    @unit_test
    def test_yield_dataset_split_works_correctly(
        self, dataframe: pd.DataFrame, mock_engine: Mock, mocker: MockerFixture
    ) -> None:
        """Tests that `yield_dataset_split` method works as expected."""
        mock_db_connection = Mock()
        mock_result = Mock()

        class MockPartition:
            """Mock class to represent database result paritions."""

            def __iter__(self) -> Iterator[np.ndarray]:
                """Iterator just returns one set of dataframe values."""
                yield dataframe.values

        mock_result.partitions.return_value = MockPartition()
        mock_result.keys.return_value = dataframe.columns
        mock_result.scalar_one.return_value = DATASET_ROW_COUNT
        mock_engine.execution_options.return_value = mock_engine
        mock_db_connection.execute.return_value = mock_result

        # Creates a multitable DatabaseConnection object
        db_conn = DatabaseConnection(
            mock_engine,
            table_names=["dummy_data", "dummy_data_2"],
        )
        # Mocks `connect` method and resulting context manager on SQLAlchemy Engine
        mocker.patch.object(
            db_conn.con, "connect"
        ).return_value.__enter__.return_value = mock_db_connection

        # Creates DatabaseSource
        ds = DatabaseSource(db_conn, seed=420)
        ds.load_data(table_name="dummy_data")
        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(ds, Mock(), Mock(), Mock(), Mock())

        # Iterates over datasource split
        df = next(
            dataset.yield_dataset_split(DataSplit.TRAIN)
        )  # First output of iterator
        assert isinstance(df, pd.DataFrame)

        # Makes assertions on call stack
        # Ignoring mypy errors because `connect` has been patched to return a Mock
        db_conn.con.connect.assert_called()  # type: ignore[attr-defined] # Reason: see above # noqa: B950
        db_conn.con.connect.return_value.__enter__.assert_called()  # type: ignore[attr-defined] # Reason: see above # noqa: B950
        db_conn.con.execution_options.assert_called_once()  # type: ignore[attr-defined] # Reason: see above # noqa: B950
        mock_db_connection.execute.assert_called()
        mock_result.partitions.assert_called_once()
        mock_result.keys.assert_called_once()
        mock_result.scalar_one.assert_called_once()

    @unit_test
    def test_database_multi_table_input_table_name(
        self, db_session: sqlalchemy.engine.base.Engine, mocker: MockerFixture
    ) -> None:
        """Checks DatabaseSource initialises correctly with `DatabaseConnection`.

        Multi-table database connection, load single table. Check that table is iterated
        instead of loaded.
        """
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )

        database_partition_size = 10
        datasource = DatabaseSource(
            db_conn, seed=420, database_partition_size=database_partition_size
        )

        # Test when load_data is called without query
        # DatabaseSource has no data attribute
        datasource.load_data()
        assert not datasource._data_is_loaded
        # Test when load_data is called WITH query
        # DatabaseSource has no data attribute
        table_name = "dummy_data"
        datasource.load_data(table_name=table_name)
        assert not datasource._data_is_loaded  # data is not set

        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(datasource, Mock(), Mock(), Mock(), Mock())

        iterator = dataset.yield_dataset_split(split=DataSplit.TRAIN)
        df = next(iterator)
        assert len(df) == database_partition_size

    @integration_test
    @pytest.mark.parametrize(
        "query",
        [
            'SELECT "Date", "TARGET" FROM blah',
            'SELECT "invalid", FROM blah',
            '"invalid" from blah',
        ],
    )
    def test_database_query_sql_error(
        self,
        db_session: sqlalchemy.engine.base.Engine,
        mocker: MockerFixture,
        query: str,
    ) -> None:
        """Checks DatabaseSource raises sqlalchemy error."""
        db_conn = DatabaseConnection(
            db_session,
            table_names=["dummy_data", "dummy_data_2"],
        )

        datasource = DatabaseSource(db_conn, seed=420)
        datasource.load_data(sql_query=query)

        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(datasource, Mock(), Mock(), Mock(), Mock())

        with pytest.raises(sqlalchemy.exc.ProgrammingError):
            next(dataset.yield_dataset_split(split=DataSplit.TRAIN))

    @integration_test
    def test_database_multi_table_input(
        self, db_session: sqlalchemy.engine.base.Engine, mocker: MockerFixture
    ) -> None:
        """Checks DatabaseSource initialises correctly with `DatabaseConnection`.

        Multi-table database connection.
        """
        db_conn = DatabaseConnection(
            db_session, table_names=["dummy_data", "dummy_data_2"]
        )

        datasource = DatabaseSource(
            db_conn, seed=420, data_splitter=PercentageSplitter(0, 0)
        )

        # Test when load_data is called without query
        # DatabaseSource has no data attribute
        datasource.load_data()
        assert datasource.multi_table
        assert not datasource._data_is_loaded
        # Test when load_data is called WITH query
        # DatabaseSource has no data attribute
        query = "SELECT 'Date', 'TARGET' FROM dummy_data"
        datasource.load_data(sql_query=query)
        assert not datasource._data_is_loaded
        assert isinstance(datasource, DatabaseSource)
        expected_output = pd.read_sql(
            f"{query} LIMIT {datasource.database_partition_size}",
            con=db_conn.con,
        )
        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(datasource, Mock(), Mock(), Mock(), Mock())

        pd.testing.assert_frame_equal(
            next(dataset.yield_dataset_split(split=DataSplit.TRAIN)), expected_output
        )

    @integration_test
    def test_database_single_table_input(
        self, db_session: sqlalchemy.engine.base.Engine, mocker: MockerFixture
    ) -> None:
        """Checks DatabaseSource initialises correctly with `DatabaseConnection`.

        Single table database connection.
        """
        db_conn = DatabaseConnection(db_session, table_names=["dummy_data"])
        datasource = DatabaseSource(db_conn, seed=420)
        datasource.load_data()
        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(datasource, Mock(), Mock(), Mock(), Mock())
        dataset._split_data()
        assert datasource.data is not None
        assert not datasource.multi_table
        assert datasource._train_idxs is not None
        assert datasource._validation_idxs is not None
        assert datasource._test_idxs is not None
        assert len(datasource._train_idxs) + len(datasource._validation_idxs) + len(
            datasource._test_idxs
        ) == len(datasource.data)

    @unit_test
    def test_mock_database_single_table_input(
        self, mock_engine: Mock, mock_pandas_read_sql_query: None, mocker: MockerFixture
    ) -> None:
        """Checks DatabaseSource initialises correctly with `DatabaseConnection`.

        Mock single table database connection.
        """
        db_conn = DatabaseConnection(mock_engine, table_names=["dummy_data"])
        datasource = DatabaseSource(db_conn, seed=420)
        datasource.load_data()
        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(datasource, Mock(), Mock(), Mock(), Mock())
        dataset._split_data()
        assert datasource.data is not None
        assert not datasource.multi_table
        assert datasource._train_idxs is not None
        assert datasource._validation_idxs is not None
        assert datasource._test_idxs is not None
        assert len(datasource._train_idxs) + len(datasource._validation_idxs) + len(
            datasource._test_idxs
        ) == len(datasource.data)

    @integration_test
    def test_database_query_input(
        self, db_session: sqlalchemy.engine.base.Engine, mocker: MockerFixture
    ) -> None:
        """Checks DatabaseSource initialises correctly with `DatabaseConnection`.

        Query database connection.
        """
        db_conn = DatabaseConnection(
            db_session,
            query="""
            SELECT *
            FROM dummy_data d1
            LEFT JOIN dummy_data_2 d2
            ON 'd1.Date' = 'd2.Date'
            """,
        )
        datasource = DatabaseSource(db_conn, seed=420)
        datasource.load_data()

        mocker.patch.object(_IterableBitfountDataset, "_set_column_name_attributes")
        dataset = _IterableBitfountDataset(datasource, Mock(), Mock(), Mock(), Mock())
        dataset._split_data()
        assert not datasource.multi_table
        assert datasource.data is not None
        assert datasource._train_idxs is not None
        assert datasource._validation_idxs is not None
        assert datasource._test_idxs is not None
        assert len(datasource._train_idxs) + len(datasource._validation_idxs) + len(
            datasource._test_idxs
        ) == len(datasource.data)
