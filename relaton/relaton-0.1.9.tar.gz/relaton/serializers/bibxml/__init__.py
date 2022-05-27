"""Serialization of :class:`relaton.models.bibdata.BibliographicItem`
into BibXML (xml2rfc) format roughly per RFC 7991,
with bias towards existing xml2rfc documents where differs.

Primary API is :func:`.serialize()`.

.. seealso:: :mod:`~relaton.serializers.bibxml_string`
"""

from typing import List
from xml.etree.ElementTree import Element
from lxml import objectify, etree

from ...util import as_list
from ...models.bibdata import BibliographicItem, Relation

from .reference import create_reference, create_referencegroup
from .anchor import get_suitable_anchor
from .target import get_suitable_target


__all__ = (
    'serialize',
)


def serialize(item: BibliographicItem, anchor: str = None) -> Element:
    """Converts a BibliographicItem to XML,
    trying to follow RFC 7991.

    Returned root element is either a ``<reference>``
    or a ``<referencegroup>``.

    :param str anchor: resulting root element ``anchor`` property.

    :raises ValueError: if there are different issues
                        with given item’s structure
                        that make it unrenderable per RFC 7991.
    """

    titles = as_list(item.title or [])
    relations: List[Relation] = as_list(item.relation or [])

    constituents = [rel for rel in relations if rel.type == 'includes']

    is_referencegroup = len(titles) < 1 and len(constituents) > 0
    is_reference = len(titles) > 0

    if is_reference:
        root = create_reference(item)

    elif is_referencegroup:
        root = create_referencegroup([
            ref.bibitem
            for ref in constituents])

    else:
        raise ValueError(
            "Able to construct neither <reference> nor <referencegroup>: "
            "impossible combination of titles and relations")

    # Fill in default root element anchor, unless specified
    if anchor is None:
        try:
            anchor = get_suitable_anchor(item)
        except ValueError:
            pass
    if anchor:
        root.set('anchor', anchor)

    # Fill in appropriate target
    try:
        target = get_suitable_target(as_list(item.link or []))
    except ValueError:
        pass
    else:
        root.set('target', target)

    objectify.deannotate(root)
    etree.cleanup_namespaces(root)

    return root
