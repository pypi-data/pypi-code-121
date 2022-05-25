from typing import Tuple, Any

from . import misc
from .logger import get_logger

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

logger = get_logger(__name__)

# Cache for storing standardized names
standardized_name_cache = {}


def get_auto_generated_indexing_set_name(session_name: str):
    return "auto-generated extraction set {} for {}".format(
        misc.get_truncated_uid(), session_name)


def get_auto_generated_enrichment_set_name(
        session_uid: str, enrichment_provider: str, unique: bool = True):
    if unique:
        return "auto-generated enrichment set {} for {} from provider {}"\
            .format(misc.get_truncated_uid(), session_uid, enrichment_provider)
    else:
        return "auto-generated enrichment set for {} from provider {}"\
            .format(session_uid, enrichment_provider)


def standardize_name(
        name: str,
        replace_symbol: str = '_') -> str:
    if not name:
        raise ValueError(
            'Session name must be provided, got: `{}`'.format(name))

    if name in standardized_name_cache:
        return standardized_name_cache[name]
    else:
        original_name = name
        for symbol in [",", "*", "\\", "<", "|", ">", "/", "?",
                       ' ', '{', '}', '$', '^', '%', '(', ')', ':', '+', '-']:
            name = name.replace(symbol, replace_symbol)

        name = name.lower()
        standardized_name_cache[original_name] = name
        return name


def assert_standardized(name: str):
    assert name == standardize_name(name), f'{name} is not standardized'


def convert_booleans_to_string(x: Any):
    """
    Parses the input (mainly for dictionaries) and finds the boolean values and converts them to strings.
    Parameters
    ----------
    x:
        Input can be any type.

    Returns
    -------
    Any:
        The output will be the stringified version of the input
    """
    out_dict = {}
    if isinstance(x, bool) or x is None:
        return str(x).lower()
    elif isinstance(x, dict):
        for k, v in x.items():
            if isinstance(k, str):
                k = standardize_name(str(k))
            out_dict.update({k: convert_booleans_to_string(v)})
        return out_dict
    elif isinstance(x, list):
        return [convert_booleans_to_string(i) for i in x]
    return x


def replace_all_symbols(s: str, replace_symbol: str = '_') -> str:
    for symbol in [
        ",", "*", "\\", "<", "|", ">", "/", "?",
        ' ', '{', '}', '$', '^', '%', '(', ')', ':', '+',
        '@', '!', '#', '&', '\'', '\"', '^', '`', '~', '.'
    ]:
        s = s.replace(symbol, replace_symbol)
    return s


def session_status_key(session_uid: str):
    if not session_uid:
        raise ValueError(
            'Session uid must be provided, got: `{}`'.format(session_uid))
    return "status_{}".format(session_uid)


def get_similarity_index_name(media_type: str,
                              model: str,
                              version: str) -> str:
    return standardize_name("similarity_{}_{}_{}".format(media_type, model, version)).replace(".", "_")

class UriParser(object):

    def __init__(self, uri: str):
        self._parsed = urlparse(uri, allow_fragments=False)

    @property
    def bucket(self):
        return self._parsed.netloc

    @property
    def key(self) -> str:
        if self._parsed.query:
            return self._parsed.path.lstrip('/') + '?' + self._parsed.query
        else:
            return self._parsed.path.lstrip('/')

    @property
    def url(self) -> str:
        return self._parsed.geturl()

    @property
    def cloud_provider(self) -> str:
        return self._parsed.scheme
