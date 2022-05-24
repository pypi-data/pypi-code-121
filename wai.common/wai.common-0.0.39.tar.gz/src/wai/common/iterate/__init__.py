"""
Utility functions for working with iterables and iterators.
"""
from ._ConstantIterator import ConstantIterator
from ._functions import (
    safe_iter,
    flatten,
    invert_indices,
    extract_by_index,
    is_iterable,
    first,
    random,
    all_meet_predicate,
    any_meets_predicate,
    count
)
from ._metadata import with_metadata, zip_metadata, get_metadata, unzip_metadata
