"""Tests Aggregator."""
import re
from typing import Dict, Union, cast
from unittest.mock import Mock, create_autospec

import numpy as np
import pytest
from pytest import fixture

from bitfount.federated.aggregators.aggregator import (
    Aggregator,
    _ModellerSide,
    _WorkerSide,
)
from bitfount.federated.aggregators.base import _BaseAggregator
from bitfount.federated.exceptions import AggregatorError
from bitfount.federated.shim import BackendTensorShim
from bitfount.types import _SerializedWeights, _TensorLike
from tests.bitfount.federated.aggregators.util import assert_equal_weight_dicts
from tests.utils.helper import unit_test


@fixture
def tensor_shim() -> Mock:
    """Returns mock tensor_shim."""
    mock_tensor_shim: Mock = create_autospec(BackendTensorShim)
    mock_tensor_shim.to_list.side_effect = lambda x: x.tolist()
    mock_tensor_shim.to_tensor.side_effect = lambda x, dtype: np.asarray(x, dtype)
    return mock_tensor_shim


@unit_test
class TestModellerSide:
    """Test Aggregator ModellerSide."""

    @fixture
    def modeller_side(self, tensor_shim: Mock) -> _ModellerSide:
        """Create ModellerSide for tests."""
        return _ModellerSide(tensor_shim=tensor_shim)

    @fixture
    def weights(self) -> Dict[str, Union[int, float]]:
        """A mapping of pod identifiers to aggregation weights."""
        return {
            "user1/pod1": 1.0,
            "user2/pod2": 2,
        }

    @fixture
    def normalised_weights(self) -> Dict[str, float]:
        """The expected normalised weights of the weights fixture."""
        return {
            "user1/pod1": 1 / 3,
            "user2/pod2": 2 / 3,
        }

    @fixture
    def modeller_side_with_weights(
        self, tensor_shim: Mock, weights: Dict[str, Union[int, float]]
    ) -> _ModellerSide:
        """Modeller-side of vanilla aggregation with weighting."""
        return _ModellerSide(tensor_shim=tensor_shim, weights=weights)

    def test_weights_returns_none_if_none_supplied(
        self,
        modeller_side: _ModellerSide,
    ) -> None:
        """Test `weights` property returns None if no weights set."""
        # No weights supplied in this fixture so should be None
        assert modeller_side.weights is None

    def test_weights_returns_normalised_weights_if_supplied(
        self,
        modeller_side_with_weights: _ModellerSide,
        normalised_weights: Dict[str, float],
        weights: Dict[str, Union[int, float]],
    ) -> None:
        """Test `weights` property returns normalised weights if weights set.

        Also ensures that this returned mapping is NOT the underlying mapping instance.
        """
        assert modeller_side_with_weights.weights == normalised_weights
        # Check this is a _copy_ of the underlying weights
        assert modeller_side_with_weights.weights == modeller_side_with_weights._weights
        assert (
            modeller_side_with_weights.weights
            is not modeller_side_with_weights._weights
        )

    def test_run(self, modeller_side: _ModellerSide) -> None:
        """Test run method."""
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user1/pod1": {"hello": [1.0, 1.0, 1.0], "world": [2.0, 2.0, 2.0]},
            "user2/pod2": {"hello": [2.0, 2.0, 2.0], "world": [3.0, 3.0, 3.0]},
        }
        average = modeller_side.run(parameter_updates=parameter_updates)

        expected_result = {
            "hello": np.asarray([1.5, 1.5, 1.5]),
            "world": np.asarray([2.5, 2.5, 2.5]),
        }
        assert_equal_weight_dicts(average, expected_result)

    def test_run_with_weights(self, modeller_side_with_weights: _ModellerSide) -> None:
        """Test run method with unequal weighting."""
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user1/pod1": {"hello": [1.5, 1.5, 1.5], "world": [3.0, 3.0, 3.0]},
            "user2/pod2": {"hello": [1.5, 1.5, 1.5], "world": [2.25, 2.25, 2.25]},
        }
        average = modeller_side_with_weights.run(parameter_updates=parameter_updates)

        expected_result = {
            "hello": np.asarray([1.5, 1.5, 1.5]),
            "world": np.asarray([2.5, 2.5, 2.5]),
        }
        assert_equal_weight_dicts(average, expected_result)

    def test_run_with_weights_throws_exception_extra_updates(
        self, modeller_side_with_weights: _ModellerSide
    ) -> None:
        """Test run throws an exception if unequal weights and extra pod.

        That is, the parameter updates contain an update from a pod that has
        no weighting.
        """
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user1/pod1": {"hello": [1.5, 1.5, 1.5], "world": [3.0, 3.0, 3.0]},
            "user2/pod2": {"hello": [1.5, 1.5, 1.5], "world": [2.25, 2.25, 2.25]},
            "user3/pod3": {"hello": [1.5, 1.5, 1.5], "world": [2.25, 2.25, 2.25]},
        }

        with pytest.raises(
            AggregatorError,
            match=re.escape(
                "Aggregation weightings provided but found updates from unweighted "
                "pods in received parameter updates: user3/pod3"
            ),
        ):
            modeller_side_with_weights.run(parameter_updates=parameter_updates)

    def test_run_with_weights_throws_exception_missing_updates(
        self, modeller_side_with_weights: _ModellerSide
    ) -> None:
        """Test run throws an exception if unequal weights and missing pod.

        That is, the parameter updates are missing an expected pod which has a
        weighting associated with it.
        """
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user2/pod2": {"hello": [1.5, 1.5, 1.5], "world": [2.25, 2.25, 2.25]},
        }

        with pytest.raises(
            AggregatorError,
            match=re.escape(
                "Aggregation weightings provided but missing updates from expected "
                "pods in received parameter updates: user1/pod1"
            ),
        ):
            modeller_side_with_weights.run(parameter_updates=parameter_updates)

    def test_run_throws_exception_different_params_in_updates(
        self, modeller_side_with_weights: _ModellerSide
    ) -> None:
        """Test run throws an exception if inconsistent updates are provided.

        In particular, that it throws an exception if the parameter names in each
        update are not the same.
        """
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user1/pod1": {"hello": [1.5, 1.5, 1.5], "world": [3.0, 3.0, 3.0]},
            "user2/pod2": {"hello": [1.5, 1.5, 1.5], "not_world": [2.25, 2.25, 2.25]},
        }

        with pytest.raises(
            AggregatorError,
            match=re.escape(
                f"Parameter names are not consistent between updates: "
                f"all updates should match { {'hello', 'world'} }"
            ),
        ):
            modeller_side_with_weights.run(parameter_updates=parameter_updates)


@unit_test
class TestWorkerSide:
    """Test Aggregator WorkerSide."""

    @fixture
    def worker_side(self) -> _WorkerSide:
        """Create WorkerSide for tests."""
        return _WorkerSide(tensor_shim=tensor_shim)  # type: ignore[arg-type] # Reason: tensor shim is mocked # noqa: B950

    async def test_run(self, worker_side: _WorkerSide) -> None:
        """Test run method."""
        parameter_update = {"hello": [1, 1, 1], "world": [2, 2, 2]}
        output = await worker_side.run(
            {
                key: cast(_TensorLike, np.asarray(value))
                for key, value in parameter_update.items()
            }
        )
        assert output == parameter_update


@unit_test
class TestAggregator:
    """Test Aggregator."""

    def test_modeller(self, tensor_shim: Mock) -> None:
        """Test modeller method."""
        aggregator_factory = Aggregator()
        aggregator = aggregator_factory.modeller()
        for type_ in [_BaseAggregator, _ModellerSide]:
            assert isinstance(aggregator, type_)

    def test_worker(self, tensor_shim: Mock) -> None:
        """Test worker method."""
        aggregator_factory = Aggregator()
        aggregator = aggregator_factory.worker()
        for type_ in [_BaseAggregator, _WorkerSide]:
            assert isinstance(aggregator, type_)
