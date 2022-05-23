from ewokscore import missing_data


# This value is used by
#  1. orange widgets to clear all downstream widgets
#  2. orange widget settings to indicate an unspecified ewoks default input value.
#
# `Settings` needs python builtins as values.
# This means we cannot use `None` as a value
INVALIDATION_DATA = None


def is_invalid_data(value):
    """Invalid means either missing data or invalidation value"""
    return value is INVALIDATION_DATA or missing_data.is_missing_data(value)


def as_missing(value):
    """Convert INVALIDATION_DATA to MISSING_DATA"""
    if is_invalid_data(value):
        return missing_data.MISSING_DATA
    return value


def as_invalidation(value):
    """Convert MISSING_DATA to INVALIDATION_DATA"""
    if is_invalid_data(value):
        return INVALIDATION_DATA
    return value
