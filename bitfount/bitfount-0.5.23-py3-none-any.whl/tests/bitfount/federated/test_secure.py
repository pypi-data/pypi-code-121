"""Tests federated secure module."""
from bitfount import SecureShare
from bitfount.federated.secure import (
    FLOAT_32_BIT_PRECISION,
    LARGE_PRIME_NUMBER,
    _secure_share_registry,
)
from bitfount.schemas.utils import bf_dump, bf_load
from tests.utils.helper import unit_test


def asert_vars_equal(agg: object, dumped: object) -> None:
    """Helper function for comparing aggregators."""
    for item in vars(agg).keys():
        if item != "_tensor_shim":
            assert vars(agg)[item] == vars(dumped)[item]


@unit_test
class TestMarshmallowSerialization:
    """Tests serialization of SecureShare."""

    def test_dump_load(self) -> None:
        """Tests serialization of SecureShare."""
        aggregator_factory = SecureShare(
            prime_q=LARGE_PRIME_NUMBER,
            precision=FLOAT_32_BIT_PRECISION,
        )
        serialized_agg = bf_dump(aggregator_factory)
        deserialized_agg = bf_load(serialized_agg, _secure_share_registry)
        asert_vars_equal(deserialized_agg, deserialized_agg)
