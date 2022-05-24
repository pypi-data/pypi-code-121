import itertools
import unicodedata


def recase_as(s, r):
    if r.islower():
        return s.lower()
    if r.isupper():
        return s.upper()
    if r.istitle():
        return s.title()
    return s.capitalize()


# shamelessly copied from Python's documentation
# https://docs.python.org/3/library/itertools.html?highlight=itertools
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


# shamelessly copied from Python's documentation
# https://docs.python.org/3/library/itertools.html?highlight=itertools
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def normalize_unicode(s):
    """
    Ensure that strings that look the same to a human reader compare equal.

    This one-liner function exists to ensure that the same normalization standard
     is applied everywhere.

    Don't use NFKC because it will replace "ª" with "a".

    See https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize
    """
    return unicodedata.normalize("NFC", s)


def normalize_text(s):
    return normalize_unicode(s).replace("\xad", "-")


__all__ = ["recase_as", "pairwise", "grouper", "normalize_unicode"]
