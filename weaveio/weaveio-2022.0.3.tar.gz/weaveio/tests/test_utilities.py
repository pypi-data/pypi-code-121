from weaveio.readquery.utilities import remove_successive_duplicate_lines
import pytest
from string import printable
from hypothesis import given, strategies as st, example


@given(st.lists(st.text(printable, min_size=1, max_size=2)))
@example(['a', 'b', 'b'])
@example(['a', 'b', 'c'])
def test_remove_successive_duplicate_lines(x):
    removed = remove_successive_duplicate_lines(x)
    for a, b in zip(removed[:-1], removed[1:]):
        assert a != b
    pairs = list(zip(x[:-1], x[1:]))
    for a, b in pairs:
        if a != b:
            assert (a, b) in pairs
