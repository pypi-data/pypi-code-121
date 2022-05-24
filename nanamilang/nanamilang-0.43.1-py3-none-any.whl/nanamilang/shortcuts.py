"""NanamiLang Shortcuts"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import functools
import random
import string
from typing import Any, Generator

# Functions to call within any context (actually some useful utilities) ##############################################


def get(coll: tuple or list, idx: int, default_value):
    """
    Safely get value by index, otherwise None or default

    :param coll: Python3 collection, can be tuple or list
    :param idx: an index to get a value from a collection
    :param default_value: default value (instead of None)
    :return: in the worst case you'll get None or default
    """

    try:
        return coll[idx]
    except IndexError:
        return None or default_value

    # Thus, we catch Python3 IndexError and return default


def plain2partitioned(coll: tuple or list,
                      n: int = 2) -> Generator:
    """Allows iterating collection partitioned (by 'n')"""

    return (coll[i:i + n] for i in range(0, len(coll), n))


def demangle(name: str) -> str:
    """
    Return demangled name (LISP -> Python3)

    :param name: a LISP name to demangle it
    :return: returns demangled Python3 name
    """

    return name.replace('-', '_')

    # Maybe extend demangle rules if needed


def truncated(source: str, n: int) -> str:
    """
    Return possibly truncated strings

    :param source: maybe \n joined strings
    :param n: a maximum string length allowed
    :return: truncated string like foobar...baz
    """

    def handle(_: str) -> str:
        """Actual handling is implemented here"""

        length = len(_)
        if length <= n:
            return _  # if it already fits length
        mid = int(n / 2)
        #      left      dots :) right
        return _[:mid] + '...' + _[length-mid+2:]

    if '\n' not in source:
        return handle(source)
    return '\n'.join(map(handle, source.split('\n')))


def partitioned2plain(collection: tuple or list) -> tuple:
    """Return a flatted collection based on partitioned"""

    return functools.reduce(lambda e, n: e + n, collection)


def randstr(length: int = 10) -> str:
    """Return randomly generated string using predefined alphabet"""

    characters = string.ascii_lowercase

    return ''.join(random.choice(characters) for _ in range(length))


def aligned(start: str, source: str, n: int, dots: str = ' ') -> str:
    """
    Return right aligned string

    :param start: to add at the start
    :param source: string to align right
    :param n: maximum length of the string
    :param dots: is space or something else
    :return: returns aligned to right string
    """

    maybe_truncated = truncated(source, n - 3)

    return start + dots * (n - len(start) - len(maybe_truncated)) + maybe_truncated


def dashcase2capitalcase(source: str) -> str:
    """
    Converts dash case string into capital case

    :param source: dash-cased-source-string-here
    :return: ConvertedCapitalCaseResultingString
    """

    return ''.join(map(lambda partition: partition.capitalize(), source.split('-')))

# A set of internal assertion functions ##############################################################################


def __ASSERT_DICTIONARY(coll: dict, message: str) -> None:
    """For internal use only, coll is a dictionary inst"""
    assert isinstance(coll, dict), message


def __ASSERT_COLLECTION(
        coll: (tuple
               or list or set or str), message: str) -> None:
    """For internal use only, 'coll' is a valid collection"""
    assert isinstance(coll, (list, tuple, set, str)), message

# A set of external assertion functions ##############################################################################


def ASSERT_COLL_CONTAINS_ITEM(coll: (tuple or
                                     list or set), item: Any, message: str) -> None:
    """Asserts that collection contains required item"""
    __ASSERT_COLLECTION(coll, 'ASSERT_COLL_CONTAINS_ITEM: collection was expected!')
    assert item in coll, message

# Sample usage: ASSERT_COLL_CONTAINS_ITEM([1], 10, 'sorry, I want 10 to be present')


def ASSERT_COLL_LENGTH_IS_EVEN(coll: (tuple
                                      or list or set or str), message: str) -> None:
    """Asserts that assertable collection has even len"""
    __ASSERT_COLLECTION(coll, 'ASSERT_COLL_LENGTH_IS_EVEN: collection was expected')
    assert len(coll) % 2 == 0, message

# Sample usage: ASSERT_COLL_LENGTH_IS_EVEN([1, 2, 3, 4], 'even items count wanted!')


def ASSERT_DICT_CONTAINS_KEYS(coll: dict, keys: set, message: str) -> None:
    """Asserts that assertable dictionary has keys set"""
    __ASSERT_DICTIONARY(coll, 'ASSERT_DICT_CONTAINS_KEYS: dictionary was expected!')
    assert keys <= coll.keys(), message

# Sample usage: ASSERT_DICT_CONTAINS_KEYS({...}. {'foo', 'bar'}, 'where is foobar?')


def ASSERT_COLL_LENGTH_VARIANTS(coll: (tuple or list or set
                                       or str), _len_v: list, message: str) -> None:
    """Asserts that assertable collection has even len"""
    __ASSERT_COLLECTION(coll, 'ASSERT_COLL_LENGTH_IS_EVEN: collection was expected')
    assert len(coll) in _len_v, message

# Sample usage: ASSERT_COLL_LENGTH_VARIANTS([], [1, 2, 3], 'only 1 .. 3 items here')


def ASSERT_COLLECTION_NOT_EMPTY(coll: (tuple
                                       or list or set or str), message: str) -> None:
    """Asserts that assertable collection has elements"""
    __ASSERT_COLLECTION(coll, 'ASSERT_COLLECTION_NOT_EMPTY: collection was expected')
    assert coll, message

# Sample usage: ASSERT_COLLECTION_NOT_EMPTY([], 'list collection could not be empty')


def ASSERT_COLL_LENGTH_EQUALS_TO(coll: (tuple or list or set
                                        or str), _length: int, message: str) -> None:
    """Asserts that assertable collection length eq to"""
    __ASSERT_COLLECTION(coll, 'ASSERT_COLL_LENGTH_IS: valid collection was expected')
    assert len(coll) == _length, message

# Sample usage: ASSERT_COLL_LENGTH_EQUALS_TO([1], 1, 'list must be a length of one!')


def ASSERT_IS_CHILD_OF(instance: Any,
                       cls: Any, message) -> None:
    """Asserts that instance class is a subclass of cls"""
    assert issubclass(instance.__class__, (cls,)), message

# Sample usage: ASSERT_IS_CHILD_OF('some-string', str, 'some-string: must be a <str>')


def ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(
        coll: (tuple or list or set), cls: Any, message: str) -> None:
    """Asserts that every collection item instance class is a subclass of cls"""
    __ASSERT_COLLECTION(coll, 'ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF: collection was expected!')
    assert len(list(filter(lambda x: issubclass(x.__class__, (cls,)), coll))) == len(coll), message

# Sample usage: ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(['some-string], str, 'must be a <list> of <str>)


# Functions to call within a tokenizer context #######################################################################


def UNTERMINATED_STR():
    """Return error message for unterminated string"""
    return 'Encountered an unterminated string literal'


def UNTERMINATED_SYMBOL(sym: str):
    """Return error message for an unterminated symbol"""
    return f'Encountered an unterminated \'{sym}\' symbol'


def UNTERMINATED_SYMBOL_AT_EOF(sym: str):
    """Return error message for an unterminated symbol at the end of file"""
    return f'Encountered an unterminated \'{sym}\' symbol at the end of file'

# Functions to call within a macro context ###########################################################################


def NML_M_FORM_IS_A_VECTOR(form: list) -> bool:
    """Whether given 'form' is a Vector coll?"""
    return form[0].dt().origin() == 'make-vector'


def NML_M_FORM_IS_A_HASHMAP(form: list) -> bool:
    """Whether given 'form' is a HashMap coll?"""
    return form[0].dt().origin() == 'make-hashmap'


def NML_M_FORM_IS_A_HASHSET(form: list) -> bool:
    """Whether given 'form' is a HashSet coll?"""
    return form[0].dt().origin() == 'make-hashset'


def NML_FORM_IS_A_COLLECTION(form: list) -> bool:
    """Whether the given 'form' is a collection?"""
    return isinstance(form, list) and len(form) >= 1


def NML_M_ASSERT_FORM_IS_A_VECTOR(form: list, message: str) -> None:
    """Should be called within a macro. Asserts that the 'form' is a Vector"""
    assert NML_FORM_IS_A_COLLECTION(form) and NML_M_FORM_IS_A_VECTOR(form), message


def NML_M_ASSERT_FORM_IS_A_HASHSET(form: list, message: str) -> None:
    """Should be called within a macro. Asserts that the 'form' is a HashSet"""
    assert NML_FORM_IS_A_COLLECTION(form) and NML_M_FORM_IS_A_HASHSET(form), message


def NML_M_ASSERT_FORM_IS_A_HASHMAP(form: list, message: str) -> None:
    """Should be called within a macro. Asserts that the 'form' is a HashMap"""
    assert NML_FORM_IS_A_COLLECTION(form) and NML_M_FORM_IS_A_HASHMAP(form), message


def NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS_EVEN(form: list, message: str) -> None:
    """Should be called within a macro. Asserts that collection items count is even"""
    ASSERT_COLL_LENGTH_IS_EVEN(form[1:], message)

    # Note, as you can see, it just wraps the call to the ASSERT_COLL_LENGTH_IS_EVEN(...)


def NML_M_ASSERT_COLL_FORM_ITEMS_COUNT_IS(form: list, n: int, message: str) -> None:
    """Should be called within a macro. Asserts that collections items count equals to n"""
    ASSERT_COLL_LENGTH_EQUALS_TO(form[1:], n, message)

    # Note, as you can see, it just wraps the call to the ASSERT_COLL_LENGTH_IS(...) function


def NML_M_ITERATE_AS_PAIRS(form: list, n: int = 0) -> Generator:
    """Should be called within macro. Allows iterating through the NanamiLang collection form"""
    if n == 0:
        return (_ for _ in form[1:])
    assert n % 2 == 0, 'NML_M_ITERATE_AS_PAIRS: n could not be odd, provide even n value please'
    return plain2partitioned(form[1:])

    # if n equals to 0, just return lazy collection as is, otherwise, if even, iterate using plain2partitioned function.

########################################################################################################################
