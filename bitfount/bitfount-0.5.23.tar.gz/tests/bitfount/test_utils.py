"""Testcases for all classes in bitfount/utils.py."""
from typing import List, Tuple, Union

import numpy as np
import pytest
from pytest import fixture

from bitfount.utils import (
    _add_this_to_list,
    _get_mb_from_bytes,
    _is_notebook,
    one_hot_encode_list,
)
from tests.utils import PytestRequest
from tests.utils.helper import unit_test


@unit_test
class TestIsNotebook:
    """Tests is_notebook()."""

    def test_notebook(self) -> None:
        """Tests fit_all_datasets()."""
        return_val = _is_notebook()
        assert not return_val


@unit_test
class TestAddThisToList:
    """Tests add_this_to_list()."""

    def test_add_duplicate(self) -> None:
        """Tests adding duplicate."""
        this = 1
        lst = [1, 2, 3]
        lst = _add_this_to_list(this, lst)
        assert lst == [1, 2, 3]

    def test_add_none(self) -> None:
        """Tests adding none."""
        this = None
        lst = [1, 2, 3]
        lst = _add_this_to_list(this, lst)
        assert lst == [1, 2, 3]

    def test_add_new_value(self) -> None:
        """Tests adding new value."""
        this = 4
        lst = [1, 2, 3]
        lst = _add_this_to_list(this, lst)
        assert lst == [1, 2, 3, 4]

    def test_add_list(self) -> None:
        """Tests adding list."""
        this = [4]
        lst = [1, 2, 3]
        lst = _add_this_to_list(this, lst)
        assert lst == [1, 2, 3, 4]


@unit_test
class TestOneHotEncodeList:
    """Tests one_hot_encode_list."""

    @staticmethod
    def data(dims: int) -> Union[List[int], List[List[int]]]:
        """Fixture of input list (or 2D list) of integers."""
        if dims == 1:
            return [0, 1, 2, 1]
        elif dims == 2:
            return [[0, 1], [1, 2], [2, 1], [1, 0]]
        else:
            raise ValueError(f"Unsupported dimension: {dims}")

    @staticmethod
    def expected(dims: int) -> np.ndarray:
        """Fixture of expected OHE output array."""
        if dims == 1:
            return np.array(
                [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 0]], dtype=np.uint8
            )
        elif dims == 2:
            return np.array(
                [
                    [1, 0, 0, 0, 1, 0],
                    [0, 1, 0, 0, 0, 1],
                    [0, 0, 1, 0, 1, 0],
                    [0, 1, 0, 1, 0, 0],
                ],
                dtype=np.uint8,
            )
        else:
            raise ValueError(f"Unsupported dimension: {dims}")

    @fixture(params=[1, 2], ids=["1D", "2D"])
    def data_and_expected(
        self, request: PytestRequest
    ) -> Tuple[Union[List[int], List[List[int]]], np.ndarray]:
        """Fixture combining data and expected for different dimensions."""
        return self.data(request.param), self.expected(request.param)

    def test_one_hot_encode_int_list(
        self, data_and_expected: Tuple[Union[List[int], List[List[int]]], np.ndarray]
    ) -> None:
        """Tests one_hot_encode_list for int list."""
        data, expected = data_and_expected
        ohe = one_hot_encode_list(data)
        assert np.array_equal(ohe, expected)

    def test_one_hot_encode_array_list(
        self, data_and_expected: Tuple[Union[List[int], List[List[int]]], np.ndarray]
    ) -> None:
        """Tests one_hot_encode_list for array list."""
        data, expected = data_and_expected
        data_arrays = [np.array(i) for i in data]
        assert isinstance(data_arrays, list)
        assert isinstance(data_arrays[0], np.ndarray)
        ohe = one_hot_encode_list(data_arrays)
        assert np.array_equal(ohe, expected)

    def test_one_hot_encode_array(
        self, data_and_expected: Tuple[Union[List[int], List[List[int]]], np.ndarray]
    ) -> None:
        """Tests one_hot_encode_list for array."""
        data, expected = data_and_expected
        data_array = np.asarray(data)
        assert isinstance(data_array, np.ndarray)
        ohe = one_hot_encode_list(data_array)
        assert np.array_equal(ohe, expected)

    def test_one_hot_encode_fails_3D(self) -> None:
        """Tests one hot encoding fails for 3D data."""
        data = [[[1], [2], [3]]]
        with pytest.raises(
            ValueError,
            match="Incorrect number of dimensions for one-hot encoding; "
            "expected 1 or 2, got 3",
        ):
            one_hot_encode_list(data)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950

    def test_one_hot_encode_fails_0D(self) -> None:
        """Tests one hot encoding fails for scalar data."""
        data = 1
        with pytest.raises(
            ValueError,
            match="Incorrect number of dimensions for one-hot encoding; "
            "expected 1 or 2, got 0",
        ):
            one_hot_encode_list(data)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950


@unit_test
def test_get_mb_from_bytes() -> None:
    """Tests get_mb_from_bytes works correctly."""
    # Test with whole number of MB bytes
    whole_mb = 2 * 1024 * 1024  # 2MB
    mb = _get_mb_from_bytes(whole_mb)
    assert mb.whole == 2
    assert mb.fractional == 2.0

    # Test with non-whole number of MB bytes
    non_whole_mb = whole_mb + 1
    mb = _get_mb_from_bytes(non_whole_mb)
    assert mb.whole == 2
    assert mb.fractional == non_whole_mb / (1024 * 1024)
