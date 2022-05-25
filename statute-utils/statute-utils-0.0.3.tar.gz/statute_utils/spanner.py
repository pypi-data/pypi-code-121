from collections import deque, namedtuple
from typing import Match

from statute_utils.compiler import (
    match_provision,
    match_provisions,
    match_statute,
    match_statutes,
)


def get_matching_spans(input: str) -> list[Match]:
    """
    Get possible statute text ranges from text, ordered by their character position in the text
    >>> sample = "There is no question that Section 2 of Presidential Decree No. 1474-B is inconsistent with Section 62 of Republic Act No. 3844.; Petitioner’s case was decided under P.D. No. 971, as amended by P.D. No. 1707."
    >>> get_matching_spans(sample)
    [<re.Match object; span=(26, 39), match='Section 2 of '>, <re.Match object; span=(39, 69), match='Presidential Decree No. 1474-B'>, <re.Match object; span=(91, 105), match='Section 62 of '>, <re.Match object; span=(105, 126), match='Republic Act No. 3844'>, <re.Match object; span=(165, 177), match='P.D. No. 971'>, <re.Match object; span=(193, 206), match='P.D. No. 1707'>]
    """
    units = [*match_statutes(input), *match_provisions(input)]
    return sorted(units, key=lambda span: span.start())


def get_statutory_provision_spans(input: str) -> list[str]:
    """
    Combine spans if they are "next" to each other and are of different item classes, i.e. provision and law.
    >>> sample = "There is no question that Section 2 of Presidential Decree No. 1474-B is inconsistent with Section 62 of Republic Act No. 3844.; Petitioner’s case was decided under P.D. No. 971, as amended by P.D. No. 1707."
    >>> get_statutory_provision_spans(sample)
    ['Section 2 of Presidential Decree No. 1474-B', 'Section 62 of Republic Act No. 3844', 'P.D. No. 971', 'P.D. No. 1707']"""

    def item_class(text: str):
        Item = namedtuple("Item", ["text", "category"])
        if match_statute(text):
            return Item(text, "title")
        elif match_provision(text):
            return Item(text, "unit")

    strings: list[str] = []

    if not (items := get_matching_spans(input)):
        return []

    # instantiate queue, assumes more than one item
    q = deque(items)

    # exhaust queue
    while q:  #

        # get items
        prior = q.popleft()
        former = item_class(prior.group())
        try:
            now = q.popleft()
            latter = item_class(now.group())
        except:
            strings.append(prior.group())
            break

        # determine whether or not to combine
        if former.category != latter.category:

            # obvious connection, always combine
            if (distance := prior.end() - now.start()) == 0:
                item = prior.group() + now.group()
                strings.append(item)
                continue

            # probable connection, consider combination
            elif abs(distance) <= 5:
                if "." not in (mid := input[prior.end() : now.start()]):
                    if ";" not in (mid):
                        item = prior.group() + mid + now.group()
                        strings.append(item)
                        continue

        # no connection, do not combine, add
        strings.append(prior.group())
        q.appendleft(now)

    return strings
