"""Tests SecureAggregator."""
from typing import Any, Dict, List, Mapping, cast
from unittest.mock import Mock, create_autospec

import numpy as np
from pytest import fixture

from bitfount.federated.aggregators.aggregator import _ModellerSide, _WorkerSide
from bitfount.federated.aggregators.base import _BaseAggregator
from bitfount.federated.aggregators.base import _registry as aggregator_registry
from bitfount.federated.aggregators.secure import SecureAggregator
from bitfount.federated.aggregators.secure import _ModellerSide as SecModellerSide
from bitfount.federated.aggregators.secure import _WorkerSide as SecWorkerSide
from bitfount.federated.secure import SecureShare
from bitfount.federated.shim import BackendTensorShim
from bitfount.federated.transport.worker_transport import _WorkerMailbox
from bitfount.schemas.utils import bf_dump, bf_load
from bitfount.types import _SerializedWeights, _TensorLike
from tests.bitfount.federated.aggregators.util import assert_equal_weight_dicts
from tests.utils.helper import get_arg_from_args_or_kwargs, unit_test


def asert_vars_equal(agg: Any, dumped: Any) -> None:
    """Helper function for comparing aggregators."""
    for item in vars(agg).keys():
        if item != "_secure_share" and item != "_tensor_shim":
            assert vars(agg)[item] == vars(dumped)[item]


@fixture
def tensor_shim() -> Mock:
    """Returns mock tensor_shim."""
    mock_tensor_shim: Mock = create_autospec(BackendTensorShim)
    mock_tensor_shim.to_list.side_effect = lambda x: x.tolist()
    mock_tensor_shim.to_numpy.side_effect = lambda x: np.asarray(x)
    mock_tensor_shim.to_tensor.side_effect = lambda x, dtype: np.asarray(x, dtype)
    return mock_tensor_shim


@fixture
def secure_share() -> Mock:
    """Returns mock secure share."""
    mock_secure_share: Mock = create_autospec(SecureShare, instance=True)
    return mock_secure_share


@fixture
def mock_mailbox() -> Mock:
    """Mock WorkerMailbox."""
    mailbox: Mock = create_autospec(_WorkerMailbox, instance=True)
    return mailbox


@unit_test
class TestModellerSide:
    """Test Aggregator ModellerSide."""

    @fixture
    def modeller_side(self, secure_share: Mock, tensor_shim: Mock) -> SecModellerSide:
        """Create ModellerSide for tests."""
        return SecModellerSide(secure_share=secure_share, tensor_shim=tensor_shim)

    def test_run(self, modeller_side: SecModellerSide, secure_share: Mock) -> None:
        """Test run method."""
        parameter_updates: Dict[str, _SerializedWeights] = {
            "user1/pod1": {"hello": [1.0, 1.0, 1.0], "world": [2.0, 2.0, 2.0]},
            "user2/pod2": {"hello": [2.0, 2.0, 2.0], "world": [3.0, 3.0, 3.0]},
        }
        average = modeller_side.run(parameter_updates=parameter_updates)

        # Check returned value is the return of average_and_decode_state_dicts
        mock_decoder = secure_share.average_and_decode_state_dicts
        assert average == mock_decoder.return_value

        # Need to manually check call args due to equality checking numpy arrays
        mock_decoder.assert_called_once()

        expected_state_dicts = [
            {k: np.asarray(v) for k, v in i.items()} for i in parameter_updates.values()
        ]
        actual_state_dicts: List[Dict[str, np.ndarray]] = get_arg_from_args_or_kwargs(
            mock_decoder.call_args, 0, "state_dicts"
        )

        assert len(actual_state_dicts) == len(expected_state_dicts)
        for actual, expected in zip(actual_state_dicts, expected_state_dicts):
            assert_equal_weight_dicts(actual, expected)


@unit_test
class TestWorkerSide:
    """Test Aggregator WorkerSide."""

    @fixture
    def worker_side(
        self, mock_mailbox: Mock, secure_share: Mock, tensor_shim: Mock
    ) -> SecWorkerSide:
        """Create WorkerSide for tests."""
        return SecWorkerSide(
            secure_share=secure_share, mailbox=mock_mailbox, tensor_shim=tensor_shim
        )

    async def test_run(self, secure_share: Mock, worker_side: SecWorkerSide) -> None:
        """Test run method."""
        expected_output = {"hello": [1.0, 1.0, 1.0], "world": [2.0, 2.0, 2.0]}
        array_parameter_update: Mapping[str, _TensorLike] = {
            k: cast(_TensorLike, np.asarray(v)) for k, v in expected_output.items()
        }

        # Mock out the secure aggregation
        secure_share.do_secure_aggregation.return_value = array_parameter_update

        output = await worker_side.run(array_parameter_update)
        assert output == expected_output


@unit_test
class TestSecureAggregator:
    """Test Secure Aggregator."""

    def test_modeller(self, secure_share: Mock, tensor_shim: Mock) -> None:
        """Test modeller method."""
        aggregator_factory = SecureAggregator(
            tensor_shim=tensor_shim, secure_share=secure_share
        )
        aggregator = aggregator_factory.modeller()
        for type_ in [
            _BaseAggregator,
            SecModellerSide,
            _ModellerSide,
        ]:
            assert isinstance(aggregator, type_)

    def test_worker(
        self, mock_mailbox: Mock, secure_share: Mock, tensor_shim: Mock
    ) -> None:
        """Test worker method."""
        aggregator_factory = SecureAggregator(
            tensor_shim=tensor_shim, secure_share=secure_share
        )
        aggregator = aggregator_factory.worker(mailbox=mock_mailbox)
        for type_ in [
            _BaseAggregator,
            SecWorkerSide,
            _WorkerSide,
        ]:
            assert isinstance(aggregator, type_)


@unit_test
class TestMarshmallowSerialization:
    """Test Marshmallow Serialization for secure aggregator."""

    def test_dump_load(self) -> None:
        """Test Marshmallow Serialization for secure aggregator."""
        aggregator_factory = SecureAggregator()
        serialized_agg = bf_dump(aggregator_factory)
        deserialized_agg = bf_load(serialized_agg, aggregator_registry)
        asert_vars_equal(deserialized_agg, aggregator_factory)
        asert_vars_equal(
            deserialized_agg._secure_share, aggregator_factory._secure_share
        )
