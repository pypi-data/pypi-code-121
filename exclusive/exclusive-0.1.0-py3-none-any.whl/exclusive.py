"""
Data structure for representing secret shares of byte vectors based on
bitwise XOR, designed for use within secure multi-party computation
(MPC) protocol implementations.
"""
from __future__ import annotations
from typing import Optional, Union, Sequence
import doctest
import base64
import secrets

class share(bytes):
    """
    Data structure for representing a XOR-based secret share of a bytes-like
    object.

    Normally, the :obj:`shares` function should be used to construct a list
    of :obj:`share` objects.

    >>> (a, b) = shares(bytes([1, 2, 3]))
    >>> (c, d) = shares(bytes([4, 5, 6]))
    >>> xor([xor([a, c]), xor([b, d])]) == xor([bytes([1, 2, 3]), bytes([4, 5, 6])])
    True
    """
    @staticmethod
    def from_base64(s: str) -> share:
        """
        Convert a secret share represented as a Base64 encoding of
        a bytes-like object into a :obj:`share` object.

        >>> share.from_base64('AQID')
        share([1, 2, 3])
        """
        return share(base64.standard_b64decode(s))

    def __xor__(self: share, other: share) -> share:
        """
        Return the bitwise exclusive disjunction (XOR) of this share and
        another share.

        >>> share(bytes([1, 2, 3])) ^ share(bytes([4, 5, 6]))
        share([5, 7, 5])

        If the two share arguments do not have equal lengths, an exception
        is raised.

        >>> share(bytes([1, 2, 3])) ^ share(bytes([4, 5]))
        Traceback (most recent call last):
          ...
        ValueError: shares must have equal lengths
        """
        if len(self) != len(other):
            raise ValueError('shares must have equal lengths')

        return share([a ^ b for (a, b) in zip(self, other)])

    def to_base64(self: share) -> str:
        """
        Return a Base64 string representation of this :obj:`share` object.

        >>> share(bytes([1, 2, 3])).to_base64()
        'AQID'
        >>> ss = [s.to_base64() for s in shares(bytes([1, 2, 3]))]
        >>> xor(share.from_base64(s) for s in ss).hex()
        '010203'
        """
        return base64.standard_b64encode(self).decode('utf-8')

    def __str__(self: share) -> str:
        """
        Return string representation of this :obj:`share` object.

        >>> str(share(bytes([1, 2, 3])))
        'share([1, 2, 3])'
        """
        return 'share([' + ', '.join(str(b) for b in self) + '])'

    def __repr__(self: share) -> str:
        """
        Return string representation of this :obj:`share` object.

        >>> share(bytes([1, 2, 3]))
        share([1, 2, 3])
        """
        return str(self)

def shares(value: Union[bytes, bytearray], quantity: Optional[int] = 2) -> Sequence[share]:
    """
    Convert a bytes-like object into two or more secret shares.

    >>> (s, t) = shares(bytes([1, 2, 3]))
    >>> s ^ t == bytes([1, 2, 3])
    True
    >>> ss = shares(bytes([1, 2, 3]), 20)
    >>> len(ss)
    20
    >>> bytes(xor(ss)).hex()
    '010203'
    >>> all(isinstance(s, share) for s in shares(bytes([1, 2, 3])))
    True

    Some compatibility and validity checks of the supplied parameter values
    are performed.

    >>> shares(bytes([1, 2, 3]), 1)
    Traceback (most recent call last):
      ...
    ValueError: quantity of shares must be at least 2
    """
    if quantity < 2:
        raise ValueError('quantity of shares must be at least 2')

    ss = []
    t = share(value)
    for _ in range(quantity - 1):
        s = share(secrets.token_bytes(len(value)))
        ss.append(s)
        t ^= s
    ss.append(t)
    return ss

def xor(iterable: Sequence[Union[bytes, bytearray]]) -> bytes:
    """
    Apply the exclusive disjunction operation across all of the elements
    of the supplied iterable.

    >>> xor([bytes([1, 2]), bytes([3, 4]), bytes([5, 6])]).hex()
    '0700'

    If all bytes-like objects in the supplied iterable do not have the same
    length, an exception is raised.

    >>> xor([bytes([1, 2]), bytes([3, 4, 5]), bytes([5, 6])]).hex()
    Traceback (most recent call last):
      ...
    ValueError: all bytes-like objects must have the same length

    If the supplied iterable does not contain at least one item, an exception
    is raised.

    >>> xor([]).hex()
    Traceback (most recent call last):
      ...
    ValueError: iterable must have at least one item
    """
    (result, length) = (None, 0)
    for bs in iterable:
        if result is None:
            result = bytearray(bs)
            length = len(result)
        else:
            if len(bs) != length:
                raise ValueError('all bytes-like objects must have the same length')
            for i in range(length):
                # pylint: disable=E1137 # Pylint confused by initial ``None``.
                result[i] ^= bs[i]

    if result is None:
        raise ValueError('iterable must have at least one item')

    return result

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
