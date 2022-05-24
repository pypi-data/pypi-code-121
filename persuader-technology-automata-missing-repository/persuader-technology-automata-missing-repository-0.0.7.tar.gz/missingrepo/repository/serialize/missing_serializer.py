from coreutility.string.string_utility import is_empty

from missingrepo.Missing import Missing


def serialize_missing(missing: Missing) -> dict:
    serialized = {
        'missing': missing.missing,
        'context': missing.context.value,
        'market': missing.market
    }
    if not is_empty(missing.description):
        serialized['description'] = missing.description
    return serialized
