from uuid import UUID
import base58
from typing import (
    Optional,
    Union,
)

BASE58_ALPHABET = b'123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'


def base58_to_uuid(public_id: str, prefix: Optional[str] = None) -> str:
    """
    >>> base58_to_uuid('fBpkbaCp2dqfowSaRDL3g7')
    '765159e7-750c-4b0b-8be0-a07fbc8f3ac4'
    >>> base58_to_uuid('ACgwBwv1PeYLXpxsMyrSKYbw', 'AC')
    '7dbf495e-254b-4e76-aaab-1bb5b726a53a'
    >>> base58_to_uuid('bPpQJd2cwkVewGNBtCYMC')
    '0182a7e1-d2e9-48dc-805b-d79156802ce6'
    >>> base58_to_uuid('3iEhRdf9YZCNViqA1FRU6')
    '00525efa-b7f3-41c4-b315-8d1836c9ec89'
    """
    prefix = prefix or ''
    return str(
        UUID(
            int=base58.b58decode_int(
                public_id[len(prefix):], alphabet=BASE58_ALPHABET
            )
        )
    )


def uuid_to_base58(internal_id: Union[UUID, str], prefix: Optional[str] = None) -> str:
    """
    >>> uuid_to_base58('765159e7-750c-4b0b-8be0-a07fbc8f3ac4', 'GR')
    'GRfBpkbaCp2dqfowSaRDL3g7'
    >>> uuid_to_base58('7dbf495e-254b-4e76-aaab-1bb5b726a53a')
    'gwBwv1PeYLXpxsMyrSKYbw'
    >>> uuid_to_base58('0182a7e1-d2e9-48dc-805b-d79156802ce6', 'GR')
    'GRbPpQJd2cwkVewGNBtCYMC'
    >>> uuid_to_base58('00525efa-b7f3-41c4-b315-8d1836c9ec89', 'GR')
    'GR3iEhRdf9YZCNViqA1FRU6'
    """
    prefix = prefix or ''
    uuid = internal_id if isinstance(internal_id, UUID) else UUID(hex=internal_id)
    encoded = base58.b58encode_int(uuid.int, alphabet=BASE58_ALPHABET)

    return f'{prefix}{encoded.decode()}'
