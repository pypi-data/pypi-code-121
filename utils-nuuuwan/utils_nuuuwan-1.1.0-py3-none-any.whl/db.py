"""Database utils."""


def get_id_key(entity_name):
    """Get entity id key.

    Follows the simple convention that *id_key* is the *entity_name*
    followed by '_id'.

    Args:
        entity_name (str): entity_name

    Return:
        id_key (str)

    .. code-block:: python

        >>> from utils.db import get_id_key
        >>> entity_name = 'province'
        >>> print(get_id_key(province))
        'province_id'

    """
    return '%s_id' % (entity_name)
