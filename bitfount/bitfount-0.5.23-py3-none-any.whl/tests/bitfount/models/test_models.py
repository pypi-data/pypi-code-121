"""Testcases for all classes in bitfount/models.py."""
import os
from pathlib import Path
from typing import cast
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
from pytest import fixture
from pytest_mock import MockerFixture
from sklearn.linear_model import LinearRegression as sklearnLinearRegression
from sklearn.neighbors import KNeighborsClassifier

from bitfount.data.dataloaders import _BitfountDataLoader
from bitfount.data.datasources.base_source import _BaseSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.metrics import MetricCollection
from bitfount.models.base_models import (
    MAIN_MODEL_REGISTRY,
    CNNModelStructure,
    NeuralNetworkModelStructure,
    _model_structure_registry,
)
from bitfount.models.models import LogisticRegressionClassifier, RegBoostRegressor
from bitfount.schemas.utils import bf_dump, bf_load
from bitfount.types import _StrAnyDict
from tests.utils.helper import (
    TABLE_NAME,
    assert_results,
    create_dataset,
    create_datasource,
    create_datastructure,
    create_schema,
    integration_test,
    unit_test,
)

SERIALIZED_MODEL_NAME = "test_model.pickle"


def assert_vars_equal(vars_original: _StrAnyDict, vars_copy: _StrAnyDict) -> None:
    """Asserts both vars() are equal; handles FunctionalForm as well."""
    for variable, value in vars_original.items():
        if isinstance(value, DataStructure):
            assert value.target == vars_copy[variable].target
        elif isinstance(value, BitfountSchema):
            assert isinstance(vars_copy[variable], BitfountSchema)
        else:
            assert value == vars_copy[variable]


@pytest.fixture
def datastructure() -> DataStructure:
    """Fixture for datastructure."""
    return create_datastructure()


@pytest.fixture
def datasource() -> _BaseSource:
    """Fixture for datasource."""
    return create_datasource(classification=True)


@pytest.fixture
def schema() -> BitfountSchema:
    """Fixture for schema."""
    return create_schema(classification=True)


@unit_test
class TestNeuralNetworkModelStructure:
    """Test NeuralNetworkModelStructure classes."""

    def test_nn_model_structure_dropout_layer_mismatch(self) -> None:
        """Test ValueError is raised if dropout layers don't match linear layers."""
        with pytest.raises(ValueError):
            NeuralNetworkModelStructure(layers=[100, 50], dropout_probs=[0.1, 0.3, 0.5])

    def test_cnn_model_structure_invalid_pooling_function(self) -> None:
        """Test ValueError is raised if an invalid pooling function is used."""
        with pytest.raises(ValueError):
            CNNModelStructure(pooling_function="notarealpoolingfunction")

    def test_cnn_model_structure_dropout_layer_mismatch(self) -> None:
        """Test ValueError is raised if dropout layers don't match conv layers."""
        with pytest.raises(ValueError):
            CNNModelStructure(layers=[100, 50], dropout_probs=[0.1, 0.3, 0.5])

    def test_cnn_model_structure_serialization(self) -> None:
        """Test CNN Model is serialized correctly."""
        model_structure = CNNModelStructure(pooling_function="avg", padding=5, stride=1)
        dumped_model_structure = bf_dump(model_structure)
        reloaded = bf_load(dumped_model_structure, _model_structure_registry)
        assert reloaded.pooling_function == model_structure.pooling_function
        assert reloaded.padding == model_structure.padding
        assert reloaded.stride == model_structure.stride


class TestLogisticRegression:
    """Test LogisticRegression class from bitfount.models."""

    @integration_test
    def test_fit_and_results(
        self, datasource: _BaseSource, datastructure: DataStructure
    ) -> None:
        """Test LogisticRegression fit() and get_results() methods."""
        log_reg = LogisticRegressionClassifier(
            datastructure=datastructure,
            schema=create_schema(classification=True),
            verbose=0,
        )
        log_reg.fit(datasource)
        assert_results(model=log_reg)

    @unit_test
    def test_missing_image_col_raises_error(self) -> None:
        """Tests that a value error when images are not in the datasource."""  # noqa: B950
        datasource = create_datasource(classification=True, image=True)
        datastructure = DataStructure(
            target=["TARGET"], image_cols=["img"], table=TABLE_NAME
        )
        model = LogisticRegressionClassifier(
            datastructure=datastructure,
            schema=create_schema(classification=True),
            verbose=0,
        )
        with pytest.raises(ValueError):
            model.fit(datasource)

    @unit_test
    def test_evaluate_no_test_dl_error(self, datastructure: DataStructure) -> None:
        """Tests that evaluate raises error with no test_dl."""
        model = LogisticRegressionClassifier(
            datastructure=datastructure,
            schema=create_schema(classification=True),
            verbose=-1,
        )
        with pytest.raises(ValueError):
            model.evaluate()

    @unit_test
    def test_serialization(
        self, datasource: _BaseSource, datastructure: DataStructure, tmp_path: Path
    ) -> None:
        """Test serialize() and deserialize() methods."""
        log_reg = LogisticRegressionClassifier(
            datastructure=datastructure,
            schema=create_schema(classification=True),
            verbose=0,
        )
        log_reg.fit(datasource)
        log_reg.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME)

        log_reg = LogisticRegressionClassifier(
            datastructure=datastructure, schema=create_schema(classification=True)
        )
        log_reg.fit(datasource)
        log_reg.deserialize(tmp_path / SERIALIZED_MODEL_NAME)

        assert log_reg.test_dl is not None
        log_reg.evaluate(log_reg.test_dl)


class TestRegBoostRegressor:
    """Test RegBoost model."""

    @fixture
    def mock_ols(self, mocker: MockerFixture) -> Mock:
        """Mock OLS import."""
        mock_ols: Mock = mocker.patch("statsmodels.api.OLS", autospec=True)
        return mock_ols

    @unit_test
    def test_model_tree_structure(self) -> None:
        """Test basic Model tree structure."""
        data = create_dataset(classification=True)
        modeltree = RegBoostRegressor._ModelTree(data.index.to_numpy(), 0)
        assert modeltree.negatives is None
        assert modeltree.positives is None
        assert isinstance(modeltree.model, sklearnLinearRegression)
        assert modeltree.depth == 0
        assert len(modeltree.data_indices) == len(data)

    @unit_test
    def test_model_tree_structure_add_children(self) -> None:
        """Test Model tree structure adding children."""
        data = create_dataset(classification=True)
        modeltree = RegBoostRegressor._ModelTree(data.index.to_numpy(), 0)
        child = modeltree.add_child(
            RegBoostRegressor._ModelTreeSide.NEGATIVE, np.array([1, 2, 3, 4, 5])
        )
        assert modeltree.negatives is not None
        assert modeltree.negatives.depth == 1
        assert child == modeltree.negatives
        assert isinstance(modeltree.negatives.model, sklearnLinearRegression)
        assert len(modeltree.negatives.data_indices) == 5
        assert modeltree.positives is None

        child2 = modeltree.add_child(
            RegBoostRegressor._ModelTreeSide.POSITIVE, np.array([1, 2, 3, 4])
        )

        assert modeltree.positives is not None
        assert modeltree.positives.depth == 1
        assert child2 == modeltree.positives
        assert child != child2
        assert isinstance(modeltree.positives.model, sklearnLinearRegression)
        assert len(modeltree.positives.data_indices) == 4
        assert modeltree.negatives is not None

    @unit_test
    @pytest.mark.parametrize("max_depth", [1, 5, 10])
    def test_model_tree_building(
        self, datasource: _BaseSource, datastructure: DataStructure, max_depth: int
    ) -> None:
        """Test building of Model tree."""
        reg = RegBoostRegressor(
            datastructure=datastructure, schema=BitfountSchema(), max_depth=max_depth
        )
        reg.fit(datasource)

        assert isinstance(reg._model, RegBoostRegressor._ModelTree)

        def find_tree_max_depth(model: RegBoostRegressor._ModelTree) -> int:
            depths = []
            for model_ in [model.positives, model.negatives]:
                if model_ is not None:
                    # Assert data indices are a subset of parent and >= minimum required
                    assert len(model_.data_indices) >= reg.min_data_points_per_node
                    assert set(model_.data_indices).issubset(set(model.data_indices))
                    # Assert features are a subset of parent
                    assert len(model_.features) <= len(model.features)
                    assert set(model_.features).issubset(set(model.features))
                    depths.append(find_tree_max_depth(model_))
                else:
                    depths.append(model.depth)
            return max(depths)

        depth = find_tree_max_depth(reg._model)
        assert depth <= reg.max_depth

    @unit_test
    def test_fit_and_evaluate_model_tree(
        self,
        datasource: _BaseSource,
        datastructure: DataStructure,
        mocker: MockerFixture,
        schema: BitfountSchema,
    ) -> None:
        """Test fitting and evaluating of model tree with very basic dummy data.

        Dummy data consists of 6 data points which can be separated into two exactly
        linear relationships of 3 data points each such that our predictions should be
        precisely accurate after one splitting of the decision tree.
        """
        model = RegBoostRegressor(
            datastructure=datastructure,
            schema=schema,
            max_depth=1,
            learning_rate=0.1,
            min_data_points_per_node=2,
        )

        # Patch out train dataloader
        model.train_dl = Mock()
        X = pd.DataFrame({"x": [3, 5, 7, 2, 4, 6]})
        y = pd.DataFrame({"TARGET": [2, 3, 4, 5, 6, 7]})
        positive_indices = [3, 4, 5]
        negative_indices = [0, 1, 2]
        model.train_dl.get_x_dataframe = Mock(return_value=X)
        model.train_dl.get_y_dataframe = Mock(return_value=y)

        mock_fit = mocker.patch.object(
            RegBoostRegressor._ModelTree,
            "fit",
            autospec=True,
            side_effect=lambda self_, X, y: self_.model.fit(X, y),
        )
        mock_predict = mocker.patch.object(
            RegBoostRegressor._ModelTree,
            "predict",
            autospec=True,
            side_effect=lambda self_, X: self_.model.predict(X),
        )

        modeltree = RegBoostRegressor._ModelTree(np.array(range(6)), 0)
        model._fit_model_tree(modeltree)

        assert modeltree.positives is not None
        assert modeltree.negatives is not None
        assert modeltree.positives.data_indices.tolist() == positive_indices
        assert modeltree.negatives.data_indices.tolist() == negative_indices
        assert modeltree.negatives.is_leaf
        assert modeltree.positives.is_leaf
        mock_predict.assert_called_once()
        pd.testing.assert_frame_equal(mock_predict.call_args[0][1], X)

        # One for each of root node, positive child and negative child
        assert mock_fit.call_count == 3

        # ROOT NODE
        # First call, second positional arg (positional args include 'self')
        pd.testing.assert_frame_equal(mock_fit.call_args_list[0][0][1], X)
        # First call, third positional arg
        np.testing.assert_array_equal(
            mock_fit.call_args_list[0][0][2], y.TARGET.to_numpy()
        )
        # POSITIVE CHILD
        # Second call, second positional arg
        pd.testing.assert_frame_equal(
            mock_fit.call_args_list[1][0][1], X.loc[positive_indices]
        )
        # Second call, third positional arg
        np.testing.assert_array_equal(
            mock_fit.call_args_list[1][0][2],
            # new y values (target - (learning rate * parent predictions))
            np.array([4.6, 5.56, 6.52], dtype=np.float32),
        )
        # NEGATIVE CHILD
        # Third call, second positional arg
        pd.testing.assert_frame_equal(
            mock_fit.call_args_list[2][0][1], X.loc[negative_indices]
        )
        # Third call, third positional arg
        np.testing.assert_array_equal(
            mock_fit.call_args_list[2][0][2],
            # new y values (target - (learning rate * parent predictions))
            np.array([1.58, 2.54, 3.5], dtype=np.float32),
        )

        preds = model._evaluate_model_tree(modeltree, X, 1)
        predictions: np.ndarray = model._aggregate_model_predictions(preds)
        # Assert that our model predictions are precisely accurate
        np.testing.assert_almost_equal(
            predictions, y.TARGET.to_numpy(dtype=np.float32), decimal=4
        )

    @unit_test
    def test_serialization(
        self, datasource: _BaseSource, datastructure: DataStructure, tmp_path: Path
    ) -> None:
        """Test serialize() and deserialize() methods."""
        model = RegBoostRegressor(datastructure=datastructure, schema=BitfountSchema())
        model.fit(datasource)
        model.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME)
        model = RegBoostRegressor(datastructure=datastructure, schema=BitfountSchema())
        model.fit(datasource)
        model.deserialize(tmp_path / SERIALIZED_MODEL_NAME)
        model.evaluate(k=5)

    @unit_test
    def test_append_model_predictions(self) -> None:
        """Test appending of model predictions is in correct order."""
        parent_preds = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]
        child_preds = [
            [0.7],
            [0.8],
        ]
        indices = [True, False]
        parent_preds = RegBoostRegressor._append_model_predictions(
            parent_preds, child_preds, indices
        )
        assert parent_preds == [
            [0.1, 0.2, 0.3, 0.7],
            [0.4, 0.5, 0.6],
        ]

    @unit_test
    def test_aggregate_model_predictions(
        self, datasource: _BaseSource, datastructure: DataStructure
    ) -> None:
        """Test models predictions are aggregated correctly."""
        model = RegBoostRegressor(
            datastructure=datastructure, schema=BitfountSchema(), learning_rate=0.1
        )
        preds = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]
        agg_preds = model._aggregate_model_predictions(preds)
        # All bar last element in array are multiplied by learning rate and then summed
        np.testing.assert_array_equal(agg_preds, np.array([0.33, 0.69]))

    @unit_test
    def test_model_classifier(
        self, datasource: _BaseSource, datastructure: DataStructure
    ) -> None:
        """Test fitting and evaluating of model classifier."""
        model = RegBoostRegressor(datastructure=datastructure, schema=BitfountSchema())
        model.fit(datasource)
        assert isinstance(model._model, RegBoostRegressor._ModelTree)
        assert model._model.classifier is None
        model._fit_model_tree_classifier(model._model, k=5)
        assert isinstance(model._model.classifier, KNeighborsClassifier)
        test_df = cast(_BitfountDataLoader, model.validation_dl).get_x_dataframe()
        assert not isinstance(test_df, tuple)
        preds = model._eval_model_tree_classifier(
            model._model, test_df[model._model.features]
        )
        assert len(preds) == len(test_df)

        # Set negatives to None and assert we get positive classes only
        temp_model = model._model.negatives
        model._model.negatives = None
        model._model.classifier = None
        preds = model._eval_model_tree_classifier(
            model._model, test_df[model._model.features]
        )
        np.testing.assert_array_equal(preds, np.ones(len(test_df), dtype=int))

        # Set positives to None and assert we get negative classes only
        model._model.negatives = temp_model
        model._model.positives = None
        model._model.classifier = None
        preds = model._eval_model_tree_classifier(
            model._model, test_df[model._model.features]
        )
        np.testing.assert_array_equal(preds, np.zeros(len(test_df), dtype=int))

    @unit_test
    def test_missing_image_col_raises_error(self) -> None:
        """Tests that a value error when images are not in the datasource."""  # noqa: B950
        datasource = create_datasource(classification=True, image=True)
        datastructure = DataStructure(
            target=["TARGET"], image_cols=["img"], table=TABLE_NAME
        )
        model = RegBoostRegressor(
            datastructure=datastructure, schema=BitfountSchema(), verbose=0
        )
        with pytest.raises(ValueError):
            model.fit(datasource)

    @unit_test
    def test_perform_stepwise_regression(
        self,
        datasource: _BaseSource,
        datastructure: DataStructure,
        mocker: MockerFixture,
    ) -> None:
        """Test stepwise regression function."""
        model = RegBoostRegressor(
            datastructure=datastructure,
            schema=BitfountSchema(),
            stepwise_regression="forward",
        )

        fwd = mocker.patch.object(
            RegBoostRegressor,
            "_forward_stepwise_regression",
            autospec=True,
            side_effect=lambda x, y, z: ["test"],
        )
        bwd = mocker.patch.object(
            RegBoostRegressor,
            "_backward_stepwise_regression",
            autospec=True,
            side_effect=lambda x, y, z: ["test"],
        )

        X = pd.DataFrame({"x": [3, 5, 7, 2, 4, 6]})
        y = np.array([2, 3, 4, 5, 6, 7])

        # Test forward stepwise regression
        features = model._perform_stepwise_regression(X, y)
        fwd.assert_called_once()
        bwd.assert_not_called()
        assert features == ["test"]

        # Test backward stepwise regression
        model.stepwise_regression = "backward"
        fwd.reset_mock()
        features = model._perform_stepwise_regression(X, y)
        bwd.assert_called_once()
        fwd.assert_not_called()
        assert features == ["test"]

        # Test stepwise regression not recognised
        with pytest.raises(ValueError):
            model.stepwise_regression = "blah"  # type: ignore[assignment] # Reason: purpose of test # noqa: B950
            model._perform_stepwise_regression(X, y)

    @unit_test
    def test_forward_stepwise_regression(self, mock_ols: Mock) -> None:
        """Test forward stepwise regression."""
        ols_model = Mock()
        mock_ols.return_value = ols_model
        # Cycles through features, adds one and then cycles through remaining features
        ols_model.fit.side_effect = [
            Mock(pvalues={"b": 0.02}),
            Mock(pvalues={"a": 0.11}),
            Mock(pvalues={"b": 0.09, "a": 0.11}),
        ]

        X = pd.DataFrame({"b": [3, 5, 7, 2, 4, 6], "a": [3, 5, 7, 2, 4, 6]})
        y = np.array([2, 3, 4, 5, 6, 7])
        features = RegBoostRegressor._forward_stepwise_regression(X, y, 0.1)
        assert features == ["b"]
        assert mock_ols.call_count == 3

    @unit_test
    def test_backward_stepwise_regression(self, mock_ols: Mock) -> None:
        """Test backward stepwise regression."""
        ols_model = Mock()
        mock_ols.return_value = ols_model
        # Cycles through features, adds one and then cycles through remaining features
        ols_model.fit.side_effect = [
            Mock(pvalues=pd.Series([0, 0.09, 0.11], index=["ignore-me", "b", "a"])),
        ]

        X = pd.DataFrame({"b": [3, 5, 7, 2, 4, 6], "a": [3, 5, 7, 2, 4, 6]})
        y = np.array([2, 3, 4, 5, 6, 7])
        features = RegBoostRegressor._backward_stepwise_regression(X, y, 0.1)
        assert features == ["b"]
        assert mock_ols.call_count == 1

    @pytest.mark.parametrize("max_depth", [1, 3])
    @unit_test
    def test_model_visualisation(
        self, datasource: _BaseSource, datastructure: DataStructure, max_depth: int
    ) -> None:
        """Test model visualisation works."""
        model = RegBoostRegressor(
            datastructure=datastructure,
            schema=BitfountSchema(),
            max_depth=max_depth,
        )
        model.fit(datasource)
        string_display = str(model._model)
        num_nodes = sum([2**i for i in range(1, max_depth + 1)]) + 1
        num_tabs = sum([i * (2**i) for i in range(1, max_depth + 1)])
        assert string_display.count("\n") == num_nodes
        assert string_display.count("\t") == num_tabs
        assert string_display.count("Depth") == num_nodes
        assert string_display.count("Features") == num_nodes
        assert string_display.count("Data") == num_nodes

    @unit_test
    def test_regboost_evaluate_no_test_dl_error(
        self, datastructure: DataStructure
    ) -> None:
        """Tests that evaluate raises error with no test_dl."""
        model = RegBoostRegressor(
            datastructure=datastructure,
            schema=BitfountSchema(),
            min_data_points_per_node=5,
            learning_rate=0.5,
            stepwise_regression_threshold=0.01,
        )
        with pytest.raises(ValueError):
            model.evaluate()

    @integration_test
    def test_fit_and_results(
        self, datasource: _BaseSource, datastructure: DataStructure
    ) -> None:
        """Test fit() and evaluate() methods as classifier outputs."""
        model = RegBoostRegressor(
            datastructure=datastructure,
            schema=BitfountSchema(),
            min_data_points_per_node=5,
            learning_rate=0.5,
            stepwise_regression_threshold=0.01,
        )
        model.fit(datasource)
        test_preds, test_target = model.evaluate(k=3)
        # normalize outputs to be between 0 and 1
        test_preds = (test_preds - np.min(test_preds)) / (
            np.max(test_preds) - np.min(test_preds)
        )
        metrics = MetricCollection.create_from_model(model)
        results = metrics.compute(test_target, test_preds)
        # This model does not perform very well, at least
        # check that the relevant metrics are computed
        assert "MAE" in results.keys()


@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for core Bitfount models."""

    def test_logistic_regression_serialization(
        self, datasource: _BaseSource, datastructure: DataStructure
    ) -> None:
        """Test Logistic Regression serialization."""
        model = LogisticRegressionClassifier(
            datastructure=datastructure, schema=BitfountSchema()
        )
        serialized_model = bf_dump(model)
        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        assert_vars_equal(vars(model), vars(deserialized_model))

    def test_regboost_regressor_serialization(
        self, datasource: _BaseSource, datastructure: DataStructure
    ) -> None:
        """Test RegBoost serialization."""
        model = RegBoostRegressor(datastructure=datastructure, schema=BitfountSchema())
        serialized_model = bf_dump(model)
        deserialized_model = bf_load(serialized_model, MAIN_MODEL_REGISTRY)
        assert_vars_equal(vars(model), vars(deserialized_model))
