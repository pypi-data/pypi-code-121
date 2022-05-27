from typing import List, cast
from lxml import etree


__all__ = (
  'get_paragraphs',
)


def get_paragraphs(val: str) -> List[str]:
    """Returns paragraphs as plain text,
    stripping HTML if needed.
    """
    try:
        return get_paragraphs_html(val)
    except (etree.XMLSyntaxError, ValueError):
        return get_paragraphs_plain(val)


def get_paragraphs_html(val: str) -> List[str]:
    tree = etree.fromstring(f'<main>{val}</main>')
    ps = [
        p.text for p in tree.findall('p')
        if (getattr(p, 'text', '') or '') != ''
    ]
    if len(ps) > 0:
        # We can cast because we excluded falsey p.text
        return cast(List[str], ps)
    else:
        raise ValueError("No HTML text detected")


def get_paragraphs_plain(val: str) -> List[str]:
    return [
        p.strip()
        for p in val.split('\n\n')
        if p.strip() != ''
    ]
