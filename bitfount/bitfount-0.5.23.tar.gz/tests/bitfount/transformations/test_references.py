"""Tests for the transformations reference extractions."""
from typing import Optional

import pytest
from pytest import fixture

from bitfount.transformations.exceptions import (
    IncorrectReferenceError,
    NotColumnReferenceError,
    NotTransformationReferenceError,
)
from bitfount.transformations.references import (
    _extract_col_ref,
    _extract_ref,
    _extract_transformation_ref,
)
from tests.utils.helper import unit_test

ref_name: str = "coltran"  # value allows testing we don't catch non-prefix part


def base_ref(prefix: Optional[str] = None) -> str:
    """Returns a base reference to build from."""
    if prefix:
        return f"{prefix}:{ref_name}"
    else:
        return ref_name


@fixture(scope="session")
def good_t_ref_short() -> str:
    """Returns a short-form transformation reference."""
    return base_ref("t")


@fixture(scope="session")
def good_t_ref_mid() -> str:
    """Returns a mid-form transformation reference."""
    return base_ref("tran")


@fixture(scope="session")
def good_t_ref_long() -> str:
    """Returns a long-form transformation reference."""
    return base_ref("transformation")


@fixture(scope="session")
def good_c_ref_short() -> str:
    """Returns a short-form column reference."""
    return base_ref("c")


@fixture(scope="session")
def good_c_ref_mid() -> str:
    """Returns a mid-form column reference."""
    return base_ref("col")


@fixture(scope="session")
def good_c_ref_long() -> str:
    """Returns a long-form column reference."""
    return base_ref("column")


@fixture(scope="session")
def bad_ref() -> str:
    """Returns a bad (i.e. unprefixed) reference."""
    return base_ref()


@unit_test
class TestExtractTransformationRef:
    """Tests for extract_transformation_ref()."""

    def test_extract_transformation_ref(
        self, good_t_ref_long: str, good_t_ref_mid: str, good_t_ref_short: str
    ) -> None:
        """Tests that extract_transformation_ref() works correctly."""
        assert ref_name == _extract_transformation_ref(good_t_ref_short)
        assert ref_name == _extract_transformation_ref(good_t_ref_mid)
        assert ref_name == _extract_transformation_ref(good_t_ref_long)

    def test_extract_transformation_ref_fails_no_prefix(self, bad_ref: str) -> None:
        """Tests that extract_transformation_ref() fails when there is no prefix."""
        with pytest.raises(
            NotTransformationReferenceError,
            match="Incorrect format for transformation reference",
        ):
            _extract_transformation_ref(bad_ref)

    def test_extract_transformation_ref_fails_wrong_type(self) -> None:
        """Tests that extract_transformation_ref() fails when ref non-string."""
        with pytest.raises(
            NotTransformationReferenceError,
            match="Incorrect type for transformation reference",
        ):
            _extract_transformation_ref(0)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950


@unit_test
class TestExtractColRef:
    """Tests for extract_col_ref()."""

    def test_extract_col_ref(
        self, good_c_ref_long: str, good_c_ref_mid: str, good_c_ref_short: str
    ) -> None:
        """Tests that extract_col_ref() works correctly."""
        assert ref_name == _extract_col_ref(good_c_ref_short)
        assert ref_name == _extract_col_ref(good_c_ref_mid)
        assert ref_name == _extract_col_ref(good_c_ref_long)

    def test_extract_col_ref_fails_no_prefix(self, bad_ref: str) -> None:
        """Tests that extract_col_ref() fails when there is no prefix."""
        with pytest.raises(
            NotColumnReferenceError, match="Incorrect format for column reference"
        ):
            _extract_col_ref(bad_ref)

    def test_extract_col_ref_fails_wrong_type(self) -> None:
        """Tests that extract_col_ref() fails when ref non-string."""
        with pytest.raises(
            NotColumnReferenceError, match="Incorrect type for column reference"
        ):
            _extract_col_ref(0)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950


@unit_test
class TestExtractRef:
    """Tests for _extract_ref()."""

    def test__extract_ref_transformation_ref(
        self, good_t_ref_long: str, good_t_ref_mid: str, good_t_ref_short: str
    ) -> None:
        """Tests that _extract_ref() works with transformations references."""
        assert ref_name == _extract_ref(good_t_ref_short)
        assert ref_name == _extract_ref(good_t_ref_mid)
        assert ref_name == _extract_ref(good_t_ref_long)

    def test__extract_ref_col_ref(
        self, good_c_ref_long: str, good_c_ref_mid: str, good_c_ref_short: str
    ) -> None:
        """Tests that _extract_ref() works with column references."""
        assert ref_name == _extract_ref(good_c_ref_short)
        assert ref_name == _extract_ref(good_c_ref_mid)
        assert ref_name == _extract_ref(good_c_ref_long)

    def test__extract_ref_fails_no_prefix(self, bad_ref: str) -> None:
        """Tests that _extract_ref() fails when there is no prefix."""
        with pytest.raises(
            IncorrectReferenceError,
            match="Argument is not a transformation or column reference.",
        ):
            _extract_ref(bad_ref)

    def test_extract_col_ref_fails_wrong_type(self) -> None:
        """Tests that _extract_ref() fails when ref non-string."""
        with pytest.raises(
            IncorrectReferenceError,
            match="Argument is not a transformation or column reference.",
        ):
            _extract_ref(0)  # type: ignore[arg-type] # Reason: purpose of test # noqa: B950
