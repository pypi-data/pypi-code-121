"""Test metrics from bitfount.metrics."""
from dataclasses import dataclass
from typing import Optional, Union, cast

import matplotlib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import recall_score

from bitfount.metrics import (
    BINARY_CLASSIFICATION_METRICS,
    MULTICLASS_CLASSIFICATION_METRICS,
    MULTILABEL_CLASSIFICATION_METRICS,
    REGRESSION_METRICS,
    ClassificationMetric,
    MetricCollection,
    MetricsProblem,
    sum_fpr_curve,
)
from bitfount.models.base_models import ClassifierMixIn
from tests.utils.helper import integration_test, unit_test


class TestMetricCollection:
    """Tests Metrics class explicitly where necessitated.

    Currently already being partially tested in `test_models.py`
    """

    @unit_test
    @pytest.mark.parametrize(
        "classification, multilabel, classes, problem",
        [
            (True, False, 2, MetricsProblem.BINARY_CLASSIFICATION),
            (True, False, 3, MetricsProblem.MULTICLASS_CLASSIFICATION),
            (True, True, 2, MetricsProblem.MULTILABEL_CLASSIFICATION),
            (False, None, None, MetricsProblem.REGRESSION),
        ],
    )
    def test_create_instance_from_model(
        self,
        classes: Optional[int],
        classification: bool,
        multilabel: bool,
        problem: MetricsProblem,
    ) -> None:
        """Test Metric Collection created from Model.

        Tests that MetricCollection creates the right problem from the Model.
        """
        if isinstance(classes, int):
            n_classes = classes

        @dataclass
        class ClassifierModel(ClassifierMixIn):
            multilabel: bool
            n_classes: int

        class RegressorModel:
            pass

        model: Union[ClassifierModel, RegressorModel]
        if classification:
            model = ClassifierModel(multilabel, n_classes)
        else:
            model = RegressorModel()

        m = MetricCollection.create_from_model(model)  # type: ignore[arg-type] # reason: used only for testing # noqa: B950
        assert m.problem == problem

    @integration_test
    def test_binary_classification(self) -> None:
        """Test metrics in the binary class setting."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob)

        assert isinstance(m.results, dict)
        assert len(m.results) == len(BINARY_CLASSIFICATION_METRICS)
        assert cast(float, m.optimal_threshold) <= 1.0
        assert cast(float, m.optimal_threshold) >= 0.0
        for _, v in m.results.items():
            # assert 1 number before the decimal place and a maximum of 4 after
            assert len(str(v)) <= 6
            assert v >= 0.0
            assert v <= 1.0

    @integration_test
    def test_binary_classification_not_enough_data(self) -> None:
        """Test metrics in the binary class setting with not enough data."""
        y_true = np.array([0, 0])
        y_prob = np.array([0.1, 0.3])

        m = MetricCollection(MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob)

        assert isinstance(m.results, dict)
        assert len(m.results) == len(BINARY_CLASSIFICATION_METRICS)
        assert m.results["AUC"] == np.inf

    @integration_test
    def test_multiclass_classification(self) -> None:
        """Test metrics in the multiclass setting (>2 classes)."""
        y_true = np.array([0, 1, 2, 0, 1])
        y_prob = np.array(
            [
                [0.5, 0.4, 0.1],
                [0.9, 0.1, 0.0],
                [0.0, 0.5, 0.5],
                [0.3, 0.3, 0.4],
                [0.2, 0.6, 0.2],
            ]
        )

        m = MetricCollection(MetricsProblem.MULTICLASS_CLASSIFICATION)
        m.compute(y_true, y_prob)
        assert isinstance(m.results, dict)
        assert len(m.results) == len(MULTICLASS_CLASSIFICATION_METRICS)
        for _, v in m.results.items():
            # assert 1 number before the decimal place and a maximum of 4 after
            assert len(str(v)) <= 6
            assert v >= 0.0
            assert v <= 1.0

    @integration_test
    def test_multilabel_classification(self) -> None:
        """Test metrics in the multilabel setting."""
        y_true = np.array([[1, 1, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0]])
        y_prob = np.array(
            [
                [0.5, 0.4, 0.1],
                [0.9, 0.1, 0.0],
                [0.0, 0.5, 0.5],
                [0.3, 0.3, 0.4],
                [0.2, 0.6, 0.2],
            ]
        )

        m = MetricCollection(MetricsProblem.MULTILABEL_CLASSIFICATION)
        m.compute(y_true, y_prob)
        assert isinstance(m.results, dict)
        assert len(m.results) == len(MULTILABEL_CLASSIFICATION_METRICS)
        assert cast(float, m.optimal_threshold) <= 1.0
        assert cast(float, m.optimal_threshold) >= 0.0
        for _, v in m.results.items():
            # assert 1 number before the decimal place and a maximum of 4 after
            assert len(str(v)) <= 6
            assert v >= 0.0
            assert v <= 1.0

    @integration_test
    def test_regression(self) -> None:
        """Test metrics in the regression setting."""
        y_true = np.array([0.2, 1, 0.5, 0, 1, 0.55])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(MetricsProblem.REGRESSION)
        m.compute(y_true, y_prob)

        assert isinstance(m.results, dict)
        assert len(m.results) == len(REGRESSION_METRICS)
        assert m.optimal_threshold is None

    @integration_test
    def test_optimise_chosen_metric(self) -> None:
        """Optimise chosen metric in binary classification."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob, "Recall")
        assert m.optimal_threshold == 0.0

    @unit_test
    def test_optimise_chosen_metric_does_not_exist(self) -> None:
        """Test optimisation for classification.

        Chosen metric doesn not exist raises ValueError.
        """
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(MetricsProblem.BINARY_CLASSIFICATION)
        with pytest.raises(ValueError):
            m.compute(y_true, y_prob, "Blah")

    @unit_test
    def test_get_results_df(self) -> None:
        """Tests get_results_df method."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob)
        results_df = m.get_results_df()

        assert isinstance(results_df, pd.DataFrame)
        for index, row in results_df.iterrows():
            assert row["value"] == m.results[cast(str, index)]

    @integration_test
    def test_threshold(self) -> None:
        """Supply the threshold rather than optimising it."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob, threshold=0.5)
        assert m.results["Recall"] == 0.75
        assert m.optimal_threshold is None

    @unit_test
    def test_view_thresholds(self) -> None:
        """Tests that chart displaying thresholds can be created properly.

        Including the underlying data.
        """
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])

        m = MetricCollection(MetricsProblem.BINARY_CLASSIFICATION)
        m.compute(y_true, y_prob)

        assert len(m.thresholds) == 201  # num of thresholds (0-100 at 0.5 increments)
        assert isinstance(m.threshold_metrics, dict)
        for k, v in m.threshold_metrics.items():
            assert k in m.metrics
            assert len(v) == len(m.thresholds)

        fig = m.view_thresholds()
        assert isinstance(fig, matplotlib.figure.Figure)

    @integration_test
    def test_custom_metric(self) -> None:
        """Test custom metric can be supplied."""
        y_true = np.array([0, 1, 1, 0, 1, 1])
        y_prob = np.array([0.1, 0.9, 0.8, 0.3, 0.2, 0.5])
        custom_metric = ClassificationMetric(recall_score, False)
        m = MetricCollection(
            MetricsProblem.BINARY_CLASSIFICATION, {"custom_metric": custom_metric}
        )
        m.compute(y_true, y_prob, metric_to_optimise="custom_metric")
        assert isinstance(m.results, dict)
        assert len(m.results) == 1
        assert m.optimal_threshold is not None


@unit_test
class TestSumFPRCurve:
    """Tests sum_fpr_curve() function."""

    def test_one_entry(self) -> None:
        """Tests functionality when only one entry.

        Check that when we have one entry correct, one wrong it gets placed in
        the right places.
        """
        test_target = [1.0, 0.0]
        test_pred = [0.89, 0.32]
        test_var_to_sum = [1.0, -2.0]
        fpr, totals = sum_fpr_curve(
            test_target, test_pred, test_var_to_sum, granularity=10
        )
        # At threshold of 0.3 we start accepting the bad one
        assert fpr == [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
        # At threshold of 0.8 we start accepting the good one
        assert totals == [-1, -1, -1, -1, 1, 1, 1, 1, 1, 0, 0]
