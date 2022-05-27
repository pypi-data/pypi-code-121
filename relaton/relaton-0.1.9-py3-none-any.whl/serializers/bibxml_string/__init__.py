from lxml import etree
from ..types import Serializer
from ..bibxml import serialize as _original_serialize
from ...models.bibdata import BibliographicItem


__all__ = (
  'serialize',
)


def serialize(item: BibliographicItem, **kwargs) -> bytes:
    """Passes given item and any kwargs through
    to :func:`relaton.serializers.bibxml.serialize()`,
    and renders the obtained XML element as an UTF8-encoded string
    with pretty print.
    """
    # etree typings are wonky. This returns a byte array.
    return etree.tostring(
      _original_serialize(item, **kwargs),
      encoding='utf-8')
