from typing import List

from ...util import as_list
from ...models.bibdata import BibliographicItem, DocID


__all__ = (
    'get_suitable_anchor',
    'format_internet_draft_anchor',
)


def format_internet_draft_anchor(id: str, versioned: bool = False) -> str:
    """
    Returns an anchor specific for an Internet Draft.
    If ``versioned`` is True, ``id`` is assumed to contain a version.

    :param str id: primary identifier for the I-D
    :param bool versioned: whether ``id`` is for I-D version or I-D as a whole
    :rtype: str
    """
    if versioned:
        return id
    else:
        return f"I-D.{id}"


def get_suitable_anchor(item: BibliographicItem) -> str:
    """From a :class:`~relaton.models.bibdata.BibliographicItem` instance
    get best anchor value and return it as a string.

    :param item: a :class:`bib_models.bibdata.BibliographicItem` instance
    :returns str: a string to be used as anchor
    :rtype: str
    :raises ValueError: unable to obtain an anchor
    """

    docids = as_list(item.docid or [])

    for docid in docids:
        if docid.type.lower() == 'internet-draft':
            return format_internet_draft_anchor(
                docid.id,
                versioned=True
                    if (item.version and item.version.draft)
                    else False)
        elif docid.scope == 'anchor':
            return docid.id

    try:
        anchor_docid: DocID = (
            [d for d in docids if d.primary]
            or docids)[0]
    except IndexError:
        raise ValueError("No suitable anchor could be determined")
    else:
        return anchor_docid.id
