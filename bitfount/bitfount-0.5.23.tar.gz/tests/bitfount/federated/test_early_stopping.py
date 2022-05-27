"""Tests early_stopping.py module."""
from typing import Callable, Dict, Generator, List

from _pytest.logging import LogCaptureFixture
import pytest
from pytest import fixture

from bitfount.federated.early_stopping import FederatedEarlyStopping
from tests.utils.helper import unit_test

ValidationMetrics = List[Dict[str, float]]
ValidationMetricsGenerator = Generator[ValidationMetrics, None, None]
ValidationMetricsCreator = Callable[..., Generator[List[Dict[str, float]], None, None]]


@unit_test
class TestFederatedEarlyStopping:
    """Tests FederatedEarlyStopping class."""

    @fixture
    def decreasing_validation_metrics(self) -> ValidationMetricsCreator:
        """Validation metrics that should trigger early stopping when iterated."""

        def validation_metrics_generator() -> ValidationMetricsGenerator:
            validation_metrics = [{"AUC": 0.8}]
            for _ in range(10):
                validation_metrics.append({"AUC": validation_metrics[-1]["AUC"] - 0.01})
                yield validation_metrics

        return validation_metrics_generator

    @fixture
    def increasing_validation_metrics(self) -> ValidationMetricsCreator:
        """Validation metrics that should not trigger early stopping when iterated."""

        def validation_metrics_generator() -> ValidationMetricsGenerator:
            validation_metrics = [{"AUC": 0.8}]
            for _ in range(10):
                validation_metrics.append({"AUC": validation_metrics[-1]["AUC"] + 0.01})
                yield validation_metrics

        return validation_metrics_generator

    @fixture
    def rollercoaster_validation_metrics(self) -> ValidationMetricsCreator:
        """Validation metrics that first go down and then go up."""

        def validation_metrics_generator() -> ValidationMetricsGenerator:
            validation_metrics = [{"AUC": 0.8}]
            for _ in range(5):
                validation_metrics.append({"AUC": validation_metrics[-1]["AUC"] - 0.01})
                yield validation_metrics

            for _ in range(5):
                validation_metrics.append({"AUC": validation_metrics[-1]["AUC"] + 0.01})
                yield validation_metrics

        return validation_metrics_generator

    @pytest.mark.parametrize("patience", [1, 3, 7])
    def test_early_stopping_patience(
        self, decreasing_validation_metrics: ValidationMetricsCreator, patience: int
    ) -> None:
        """Tests that early stopping is triggered at the right time."""
        early_stopping = FederatedEarlyStopping(
            metric="AUC", patience=patience, delta=0.01
        )

        for epoch, metrics in enumerate(decreasing_validation_metrics(), start=1):
            stop = early_stopping.check(metrics)
            if epoch > patience:
                assert stop
            else:
                assert not stop

    @pytest.mark.parametrize("delta", [0.001, 0.00999, 0.01, 0.02])
    def test_early_stopping_delta(
        self, delta: float, increasing_validation_metrics: ValidationMetricsCreator
    ) -> None:
        """Tests that early stopping is triggered at the right time."""
        patience = 5
        early_stopping = FederatedEarlyStopping(
            metric="AUC", patience=patience, delta=delta
        )

        for epoch, metrics in enumerate(increasing_validation_metrics(), start=1):
            stop = early_stopping.check(metrics)
            if epoch > patience and delta > 0.01:  # fixture increments AUC by 0.01
                assert stop
            else:
                assert not stop

    @pytest.mark.parametrize("patience", [1, 3, 7])
    def test_early_stopping_not_triggered(
        self, increasing_validation_metrics: ValidationMetricsCreator, patience: int
    ) -> None:
        """Tests that early stopping is not triggered at the right time."""
        early_stopping = FederatedEarlyStopping(
            metric="AUC", patience=patience, delta=0.01
        )

        for _, metrics in enumerate(increasing_validation_metrics(), start=1):
            stop = early_stopping.check(metrics)
            assert not stop

    @pytest.mark.parametrize("patience", [1, 3, 7])
    def test_early_stopping_with_variable_metrics(
        self, patience: int, rollercoaster_validation_metrics: ValidationMetricsCreator
    ) -> None:
        """Tests early stopping with metrics that go down and then up."""
        delta = 0.01
        metric = "AUC"
        halfway_point_index = 5
        early_stopping = FederatedEarlyStopping(
            metric=metric, patience=patience, delta=delta
        )
        for epoch, metrics in enumerate(rollercoaster_validation_metrics(), start=1):
            stop = early_stopping.check(metrics)

            # Make assertions about counter
            if epoch <= halfway_point_index:
                assert early_stopping.counter == epoch
            elif epoch < patience:
                assert early_stopping.counter == halfway_point_index
            elif metrics[-1][metric] - metrics[-1 - patience][metric] >= delta:
                assert early_stopping.counter == 0
            else:
                assert early_stopping.counter == halfway_point_index

            # Make assertions about stop
            if early_stopping.counter > patience:
                assert stop
            else:
                assert not stop

    @pytest.mark.parametrize("patience", [1, 3, 7])
    def test_early_stopping_metric_missing(
        self,
        caplog: LogCaptureFixture,
        decreasing_validation_metrics: ValidationMetricsCreator,
        patience: int,
    ) -> None:
        """Checks early stopping ignored and warning issued if missing metric."""
        early_stopping = FederatedEarlyStopping(
            metric="missing_metric", patience=patience, delta=0.01
        )

        for _, metrics in enumerate(decreasing_validation_metrics(), start=1):
            stop = early_stopping.check(metrics)
            assert not stop
            assert (
                caplog.records[-1].msg
                == "Early stopping ignored. "
                + "Metric missing_metric not reported by model."
            )
            assert caplog.records[-1].levelname == "WARNING"
