from core.missing.Context import Context
from coreutility.collection.dictionary_utility import as_data

from missingrepo.Missing import Missing


def deserialize_missing(missing) -> Missing:
    if missing is not None:
        missing_info = as_data(missing, 'missing')
        context = Context.parse(as_data(missing, 'context'))
        market = as_data(missing, 'market')
        description = as_data(missing, 'description')
        return Missing(missing_info, context, market, description)
