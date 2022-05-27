"""Tests types.py."""
import string

import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest

from bitfount.data.types import _ExtendableLabelEncoder
from tests.utils.helper import unit_test


@unit_test
class TestExtendableLabelEncoder:
    """Tests the extendable label encoder."""

    DATA = np.array(list(string.ascii_lowercase))
    DATA2 = np.array(list(str(x) for x in range(0, 10)))

    def test_add_values(self) -> None:
        """Checks we can successfully add values.

        Also checks we don't get extras if doing it twice.
        """
        len1 = len(self.DATA)
        len2 = len(self.DATA2)
        encoder = _ExtendableLabelEncoder()
        encoder.add_values(self.DATA)
        assert encoder.size == len1
        encoder.add_values(self.DATA)
        assert encoder.size == len1
        encoder.add_values(self.DATA2)
        assert encoder.size == len1 + len2

    def test_transform_str(self) -> None:
        """Checks we can encode a column that is strings."""
        encoder = _ExtendableLabelEncoder()
        encoder.add_values(self.DATA)
        encoder.add_values(self.DATA2)
        input_arr = pd.Series(["a", "0", "2", "b"])
        encoded = encoder.transform(input_arr)
        assert_array_equal(encoded, np.array([0, 26, 28, 1]))

    def test_transform_error(self) -> None:
        """Tests transform error."""
        encoder = _ExtendableLabelEncoder()
        encoder.add_values(self.DATA)
        encoder.add_values(self.DATA2)
        with pytest.raises(ValueError):
            encoder.transform(pd.Series(["a", "a", "0", "2", "unseen"]))

    def test_size(self) -> None:
        """Tests size property explicitly."""
        encoder = _ExtendableLabelEncoder()
        encoder.classes = dict(zip(["a", "b", "c"], [1, 2, 3]))
        assert encoder.size == 3

    def test_eq_magic_method(self) -> None:
        """Tests that __eq__ works as expected."""
        encoder1 = _ExtendableLabelEncoder()
        encoder1.add_values(self.DATA)
        encoder2 = _ExtendableLabelEncoder()
        encoder2.add_values(self.DATA2)
        encoder3 = _ExtendableLabelEncoder()
        encoder3.add_values(self.DATA)
        assert not (encoder1 == encoder2)
        assert encoder1 == encoder3
