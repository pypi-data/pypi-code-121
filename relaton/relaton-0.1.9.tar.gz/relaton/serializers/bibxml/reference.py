from typing import List, Tuple, Set, Optional, Union, cast
import datetime
from xml.etree.ElementTree import Element
from lxml import objectify

from ...util import as_list
from ...models.bibdata import BibliographicItem, DocID, Contributor, Series
from ...models.dates import Date, parse_relaxed_date
from ...models.strings import Title, GenericStringValue

from .series import DOCID_SERIES_EXTRACTORS
from .authors import create_author, is_author
from .abstracts import get_paragraphs
from .target import get_suitable_target
from .anchor import get_suitable_anchor


__all__ = (
    'create_reference',
    'create_referencegroup',
)


E = objectify.E


def create_referencegroup(items: List[BibliographicItem]) -> Element:
    return E.referencegroup(*(
        create_reference(item)
        for item in items
    ))


def create_reference(item: BibliographicItem) -> Element:
    titles: List[Title] = as_list(item.title or [])
    if len(titles) < 1:
        raise ValueError("Unable to create a <reference>: no titles")

    contributors: List[Contributor] = as_list(item.contributor or [])
    author_contributors: List[Contributor] = [
        contrib
        for contrib in contributors
        if is_author(contrib)
    ]

    front = E.front(
        E.title(titles[0].content),
        *(create_author(contrib) for contrib in author_contributors),
    )

    # Publication date… Or at least any date
    published_date: Optional[datetime.date] = None
    published_date_raw: Optional[Union[str, datetime.date]] = None
    all_dates: List[Date] = as_list(item.date or [])
    specificity: Optional[str] = None
    for date in all_dates:
        if date.type == 'published':
            published_date_raw = date.value
            break
    if not published_date_raw and all_dates:
        published_date_raw = all_dates[0].value

    if published_date_raw:
        if isinstance(published_date_raw, str):
            relaxed = parse_relaxed_date(published_date_raw)
            if relaxed:
                published_date = relaxed[0]
                specificity = relaxed[2]
        else:
            published_date = published_date_raw
            specificity = 'day'

    if published_date and specificity:
        date_el = E.date(year=published_date.strftime('%Y'))
        if specificity in ['month', 'day']:
            date_el.set('month', published_date.strftime('%B'))
        if specificity == 'day':
            date_el.set('day', str(published_date.day))
        front.append(date_el)

    # Abstract
    abstracts: List[GenericStringValue] = as_list(item.abstract or [])
    if len(abstracts) > 0:
        front.append(E.abstract(*(
            E.t(p)
            for p in get_paragraphs(abstracts[0].content)
        )))

    ref = E.reference(front)

    # Series
    docids: List[DocID] = as_list(item.docid or [])
    series: Set[Union[None, Tuple[str, str]]] = set()
    for docid in docids:
        series = series | set([
            func(docid)
            for func in DOCID_SERIES_EXTRACTORS
        ])
    series_: List[Series] = as_list(item.series or [])
    series = series | set([
        (cast(List[Title], as_list(s.title or []))[0].content, s.number)
        for s in series_
        if s.number and s.title
    ])
    for series_info in series:
        if series_info is not None:
            ref.append(E.seriesInfo(
                name=series_info[0],
                value=series_info[1],
            ))

    # Target, may be overwritten by callers
    try:
        target = get_suitable_target(as_list(item.link or []))
    except ValueError:
        pass
    else:
        ref.set('target', target)

    # Anchor, may be overwritten by callers
    try:
        anchor = get_suitable_anchor(item)
    except ValueError:
        pass
    else:
        ref.set('anchor', anchor)

    return ref
