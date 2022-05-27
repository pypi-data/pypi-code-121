"""Tests for the federated transport utils."""
from bitfount.federated.transport.utils import _average_training_metrics
from tests.utils.helper import unit_test


@unit_test
def test_metrics_averaging() -> None:
    """Tests validation metrics are averaged and returned when provided."""
    validation_metrics = [{"AUC": "0.7", "F1": "0.8"}, {"AUC": "0.9", "F1": "0.6"}]

    metrics = _average_training_metrics(validation_metrics)
    assert metrics == {"AUC": 0.8, "F1": 0.7}


@unit_test
def test_metrics_averaging_no_metrics() -> None:
    """Tests aggregator returns no validation metrics when not provided."""
    metrics = _average_training_metrics([{}])
    assert metrics == {}
