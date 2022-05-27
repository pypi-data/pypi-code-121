"""Tests for utils.py."""
from unittest.mock import Mock

import pytest

from bitfount.schemas.exceptions import SchemaClassError
from bitfount.schemas.utils import (
    _combine_dict_helper,
    _dict_to_schema,
    _obj_to_schema,
    bf_dump,
)
from tests.utils.helper import unit_test


@unit_test
def test_dump_with_empty_object_error() -> None:
    """Tests that empty object dump raises error."""
    with pytest.raises(SchemaClassError):
        bf_dump(None)


@unit_test
def test_optional_nested_set() -> None:
    """Test that `optional_nested` is set on the class."""
    obj1 = Mock()
    obj1.optional_nested = None
    obj2 = Mock()
    obj2.fields_dict = {}
    obj2.nested_fields = {}
    obj2.optional_nested = ["blah"]
    _combine_dict_helper(obj1, obj2, {}, {})
    assert obj1.optional_nested == ["blah"]


@unit_test
def test_depth_greater_than5_raises_error_dict_to_schema() -> None:
    """Tests that depth greater than 5 raises error."""
    with pytest.raises(SchemaClassError):
        _dict_to_schema(Mock(), Mock(), depth=6)


@unit_test
def test_depth_greater_than5_raises_error_obj_to_schema() -> None:
    """Tests that depth greater than 5 raises error."""
    with pytest.raises(SchemaClassError):
        _obj_to_schema(Mock(), depth=6)
