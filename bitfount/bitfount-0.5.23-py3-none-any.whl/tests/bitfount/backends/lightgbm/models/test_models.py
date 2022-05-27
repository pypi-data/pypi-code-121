"""Tests for LightGBM models."""
import os
from pathlib import Path

import lightgbm
import pytest
from pytest_mock import MockerFixture
import sqlalchemy

from bitfount.backends.lightgbm.models.models import (
    LGBMRandomForestClassifier,
    LGBMRandomForestRegressor,
)
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datasources.database_source import DatabaseSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.utils import DatabaseConnection
from bitfount.models.base_models import MAIN_MODEL_REGISTRY
from bitfount.schemas.utils import bf_dump, bf_load
from tests.bitfount.models.test_models import SERIALIZED_MODEL_NAME, assert_vars_equal
from tests.utils.helper import (
    assert_results,
    backend_test,
    create_datasource,
    create_datastructure,
    create_query_datastructure,
    create_schema,
    integration_test,
    unit_test,
)


@pytest.fixture
def datastructure() -> DataStructure:
    """Fixture for datastructure."""
    return create_datastructure()


@pytest.fixture
def query_datastructure() -> DataStructure:
    """Fixture for datastructure containing query."""
    return create_query_datastructure()


@pytest.fixture
def datasource() -> _BaseSource:
    """Fixture for datasource."""
    return create_datasource(classification=True)


@pytest.fixture
def schema() -> BitfountSchema:
    """Fixture for datastructure with schema."""
    return create_schema(classification=True)


@backend_test
class TestLGBMRandomForest:
    """Test LGBMRandomForest model classes."""

    @integration_test
    def test_classification(
        self,
        datasource: _BaseSource,
        datastructure: DataStructure,
        schema: BitfountSchema,
    ) -> None:
        """Tests LGBMRandomForestClassifier training."""
        random_forest = LGBMRandomForestClassifier(
            datastructure=datastructure,
            schema=schema,
            n_estimators=10,
            early_stopping_rounds=2,
            verbose=-1,
        )
        random_forest.fit(datasource)
        assert_results(model=random_forest)

    @integration_test
    def test_regression(
        self, datasource: _BaseSource, datastructure: DataStructure
    ) -> None:
        """Tests LGBMRandomForestRegressor training."""
        random_forest = LGBMRandomForestRegressor(
            datastructure=datastructure,
            schema=create_schema(classification=False),
            verbose=-1,
        )
        random_forest.fit(datasource)
        assert_results(model=random_forest)

    @integration_test
    def test_serialization(
        self,
        datasource: _BaseSource,
        datastructure: DataStructure,
        schema: BitfountSchema,
        tmp_path: Path,
    ) -> None:
        """Tests serialize() and deserialize() methods."""
        random_forest = LGBMRandomForestClassifier(
            datastructure=datastructure,
            schema=schema,
            n_estimators=10,
            early_stopping_rounds=10,
            verbose=-1,
        )

        random_forest.fit(datasource)
        random_forest.serialize(str(tmp_path / SERIALIZED_MODEL_NAME))
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME)
        rf_model = LGBMRandomForestClassifier(
            datastructure=datastructure,
            schema=schema,
            n_estimators=10,
            early_stopping_rounds=10,
            verbose=-1,
        )
        rf_model.fit(datasource)
        rf_model.deserialize(str(tmp_path / SERIALIZED_MODEL_NAME))
        rf_model.evaluate(random_forest.test_set)

    @integration_test
    def test_fit_called_with_db_query(
        self,
        db_session: sqlalchemy.engine.base.Engine,
        mocker: MockerFixture,
    ) -> None:
        """Tests model is fit with a query datastructure."""
        datastructure = DataStructure(target="TARGET", table="dummy_data")
        db_datasource = DatabaseSource(
            DatabaseConnection(db_session, table_names=["dummy_data"])
        )
        schema = BitfountSchema(
            db_datasource,
            table_name="dummy_data",
            force_stypes={"dummy_data": {"categorical": ["TARGET"]}},
        )
        random_forest = LGBMRandomForestClassifier(
            datastructure=datastructure,
            schema=schema,
            verbose=-1,
        )

        mocker.patch.object(lightgbm, "train", return_value=None)
        random_forest.fit(db_datasource)
        assert random_forest._databunch is not None
        assert random_forest.n_classes == 2

    @unit_test
    def test_fit_called_with_table_datastructure(
        self,
        datasource: _BaseSource,
        datastructure: DataStructure,
        schema: BitfountSchema,
    ) -> None:
        """Tests model is fit with a table datastructure."""
        random_forest = LGBMRandomForestClassifier(
            datastructure=datastructure,
            schema=schema,
            n_estimators=10,
            early_stopping_rounds=2,
            verbose=-1,
        )
        table_name = datastructure.get_table_name()
        expected_schema = schema.get_table_schema(table_name)
        random_forest.fit(datasource)
        assert random_forest._databunch is not None
        assert random_forest.n_classes == 2
        assert random_forest._databunch.schema == expected_schema

    @unit_test
    def test_evaluate_no_test_dl_error(self, datastructure: DataStructure) -> None:
        """Tests that evaluate raises error with no test_dl."""
        random_forest = LGBMRandomForestRegressor(
            datastructure=datastructure, schema=BitfountSchema(), verbose=-1
        )
        with pytest.raises(ValueError):
            random_forest.evaluate()

    @unit_test
    def test_fit_no_validation_dl(
        self,
        datasource: _BaseSource,
        datastructure: DataStructure,
        schema: BitfountSchema,
    ) -> None:
        """Tests that evaluate called without test data raises error."""
        random_forest = LGBMRandomForestClassifier(
            datastructure=datastructure,
            schema=schema,
            n_estimators=10,
            early_stopping_rounds=2,
            verbose=-1,
        )
        datasource.load_data()
        random_forest._add_datasource_to_schema(datasource)
        random_forest._set_dataloaders()
        random_forest.validation_dl = None
        train_df, val_df = random_forest._create_dataset()
        assert val_df is None


@backend_test
@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for LightGBM models."""

    def test_rf_classifier_serialization(
        self, datastructure: DataStructure, schema: BitfountSchema
    ) -> None:
        """Tests serialization with LGBMRandomForestClassifier."""
        model = LGBMRandomForestClassifier(datastructure=datastructure, schema=schema)
        serialized_model = bf_dump(model)
        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        assert_vars_equal(vars(model), vars(deserialized_model))

    def test_rf_regressor_serialization(self, datastructure: DataStructure) -> None:
        """Tests serialization with LGBMRandomForestRegressor."""
        model = LGBMRandomForestRegressor(
            datastructure=datastructure, schema=BitfountSchema()
        )
        serialized_model = bf_dump(model)
        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        assert_vars_equal(vars(model), vars(deserialized_model))
