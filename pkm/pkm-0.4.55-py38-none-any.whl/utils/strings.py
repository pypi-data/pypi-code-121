from typing import Iterable, Optional


def without_suffix(s: str, suffix: str) -> str:
    """
    :param s: the base string
    :param suffix: the suffix to remove
    :return: the value of `s` without `suffix` if `s` ends with `suffix` otherwise unchanged `s`
    """
    if s.endswith(suffix):
        return s[:-len(suffix)]

    return s


def without_prefix(s: str, prefix: str) -> str:
    """
    :param s: the base string
    :param prefix: the prefix to remove
    :return: the value of `s` without `prefix` if `s` starts with `prefix` otherwise unchanged `s`
    """
    if s.startswith(prefix):
        return s[len(prefix):]

    return s


def endswith_any(s: str, suffixes: Iterable[str]) -> Optional[str]:
    """
    :param s: the string to check
    :param suffixes: iterable of suffixes to search
    :return: the first suffix of `s` in `suffixes` or `None` if no such suffix found
    """
    return next((sf for sf in suffixes if s.endswith(sf)), None)


def startswith_any(s: str, prefixes: Iterable[str]) -> Optional[str]:
    """
    :param s: the string to check
    :param prefixes: iterable of prefixes to search
    :return: the first prefix of `s` in `prefixes` or `None` if no such prefix found
    """
    return next((pf for pf in prefixes if s.startswith(pf)), None)
